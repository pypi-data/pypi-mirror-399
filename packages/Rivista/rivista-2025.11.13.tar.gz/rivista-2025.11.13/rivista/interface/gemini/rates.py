#!/usr/bin/python
# -*- coding: utf-8 -*-

from jetforce import RateLimiter

general_rate_limiter = RateLimiter("100/m")
short_rate_limiter = RateLimiter("5/30s")
long_rate_limiter = RateLimiter("60/5m")
