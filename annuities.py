#
# Copyright (c) 2024 LateGenXer
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#


import datetime

from data import mortality
from data import boe


cur_year = datetime.datetime.now(datetime.timezone.utc).year


yc = boe.yield_curves()


# https://en.wikipedia.org/wiki/Actuarial_present_value
def present_value(cur_age, kind, table:mortality.Table):
    yob = cur_year - cur_age

    ages = list(range(cur_age, 121))

    p = 1.0
    pv = 0.0
    s = yc[f'{kind}_Spot']
    for age in ages:
        years = age - cur_age
        index = float(years)
        index = max(index,  0.5)
        index = min(index, 40.0)
        rate = s[index]
        if False:
            print(f'{years:2d}  {rate:6.2%}  {p:7.2%}')
        pv += p * (1.0 + rate)**-years
        qx = table.mortality(yob + age, age)
        p *= 1.0 - qx

    return pv


def annuity_rate(cur_age, kind, table:mortality.Table):
    pv = present_value(cur_age, kind, table)
    ar = 1.0/pv
    return ar
