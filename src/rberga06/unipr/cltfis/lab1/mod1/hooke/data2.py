#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ...datum import Datum

# Masses
MM = Datum(24.31, 0.01)
M0 = Datum(18.84, 0.01) + MM/3
print(M0 + Datum(407.73, 0.01))
print(M0 + Datum(542.47, 0.01))
print(M0 + Datum(667.82, 0.01))
print(M0 + Datum(950.22, 0.01))
