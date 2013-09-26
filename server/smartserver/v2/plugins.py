#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from bottle import PluginError, request

__all__ = ["err", "ContentTypePlugin"]


def err(code='500', msg='Unknown error!'):
    """
    generate error message.
    """
    return {'errors': {'code': code, 'msg': msg}}


# Plugin to check if the request has a content-type not in *types.
# if no, then return error message.
class ContentTypePlugin(object):
    '''This plugin checks the content-type of the request'''
    name = 'content-type'
    api = 2

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, ContentTypePlugin):
                continue
            raise PluginError("Found another Content-Type plugin with "
                              "conflicting settings (non-unique keyword).")

    def apply(self, callback, route):
        contenttypes = route.config.get('content_type', [])
        if not isinstance(contenttypes, list):
            contenttypes = [contenttypes]

        if len(contenttypes) is 0:
            return callback  # content-type not specified

        def wrapper(*args, **kwargs):
            for t in contenttypes:
                if t.lower() in request.content_type:
                    return callback(*args, **kwargs)

            return err(code='500', msg='Invalid content-type header!')

        return wrapper

#This plugin checks the format of request.json, if required keys dont exist, return error message. 
class DataFormatPlugin(object):
    '''This plugin checks the request data-format'''
    name = 'data-Format'
    api = 2

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, DataFormatPlugin):
                continue
            raise PluginError("Found another Content-Type plugin with "
                              "conflicting settings (non-unique keyword).")

    def apply(self, callback, route):
        format = route.config.get('data_format', [])
        if not isinstance(format, list):
            format = [format]

        if len(format) == 0:
            return callback

        def wrapper(*args, **kwargs):
            for key in format:
                if request.json.get(key, 'badkey') == 'badkey':
                    return err(code='500', msg='Invalid request data-format!')
            return callback(*args, **kwargs)
        return wrapper
