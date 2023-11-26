#!/usr/bin/env python3
#
# Copyright (c) 2023 LateGenXer
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#


import os.path
import posixpath
import shutil
import sys
import time
import urllib.error
import urllib.request
import email.message
import email.utils
import http


def download(url, filename=None, ttl=0, content_type=None, verbose=False):
    if filename is None:
        filename = posixpath.basename(url)

    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    if content_type is not None:
        headers['Accept'] = content_type

    dst_exists = os.path.exists(filename)
    if dst_exists:
        dst_size = os.path.getsize(filename)
        dst_mtime = os.path.getmtime(filename)
        if dst_mtime + ttl >= time.time():
            return
        headers['If-Modified-Since'] = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime(dst_mtime))

    request = urllib.request.Request(url, headers=headers)

    try:
        src = urllib.request.urlopen(request)
    except urllib.error.HTTPError as ex:
        if ex.code == http.HTTPStatus.NOT_MODIFIED:
            return
        else:
            raise
    assert src.code != http.HTTPStatus.NOT_MODIFIED

    if verbose:
        print(src.headers)

    if content_type is not None:
        # https://stackoverflow.com/a/75727619
        msg = src.headers
        assert isinstance(msg, email.message.Message)
        params = msg.get_params()
        src_content_type = params[0][0]
        if src_content_type != content_type:
            raise ValueError(f'Expected {content_type}, got {src_content_type}')

    src_mtime = src.headers.get('Last-Modified')
    if src_mtime is None:
        src_mtime = time.time()
    else:
        src_mtime = email.utils.parsedate_tz(src_mtime)
        src_mtime = email.utils.mktime_tz(src_mtime)

    if dst_exists:
        src_size = src.headers.get('Content-Length')
        if src_size is not None:
            src_size = int(src_size)
            if src_size == dst_size and src_mtime == dst_mtime:
                src.close()
                return

    sys.stderr.write(f'Downloading {url}...\n')
    if dst_exists:
        os.unlink(filename)
    dst = open(filename, 'wb')
    shutil.copyfileobj(src, dst)
    dst.close()
    os.utime(filename, (src_mtime, src_mtime))
    src.close()


if __name__ == '__main__':
    _, url, filename = sys.argv[:3]
    try:
        content_type = sys.argv[3]
    except IndexError:
        content_type = None
    download(url, filename, content_type=content_type, verbose=True)
