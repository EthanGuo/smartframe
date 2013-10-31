#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["v1"]

def __load_api_v1():
    from .v1.apis import appweb
    return appweb

v1 = __load_api_v1()
