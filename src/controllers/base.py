#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from os.path import dirname, join
import sys
import inspect
from new import classobj 

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template

__CONTROLLERS__ = []
__CONTROLLERSDICT__ = {}

def get_controller_name(controller):
    return controller.lower().replace("controller", "")

def json(func):
    def actual(*args, **kw):
        if not args or len(args) < 2:
            raise RuntimeError("The decorated function must be inside a controller!")

        instance = args[1]
        instance.response.headers['Content-Type'] = "application/json"
        func(*args, **kw)

    return actual

def javascript(func):
    def actual(*args, **kw):
        if not args or len(args) < 2:
            raise RuntimeError("The decorated function must be inside a controller!")

        instance = args[1]
        instance.response.headers['Content-Type'] = "text/javascript"
        func(*args, **kw)

    return actual

def authenticated(func):
    def actual(*args, **kw):
        if not args or len(args) < 2:
            raise RuntimeError("The decorated function must be inside a controller!")

        instance = args[1]

        user = users.get_current_user()
        if user:
            func(*args, **kw)
        else:
            instance.redirect(users.create_login_url(instance.request.uri))
    return actual

def get(route, name=None):
    def dec(func):
        actual_name = func.__name__
        if name:
            actual_name = name
        conf = (
            actual_name, {
                'route': route,
                'method': func.__name__,
                'http_method':'get'
            }
        )
        return func, conf

    return dec

def post(route, name=None):
    def dec(func):
        actual_name = func.__name__
        if name:
            actual_name = name
        conf = (
            actual_name, {
                'route': route,
                'method': func.__name__,
                'http_method':'post'
            }
        )
        return func, conf

    return dec

class MetaController(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('MetaController', 'Controller'):
            __CONTROLLERS__.append(cls)
            __CONTROLLERSDICT__[name] = cls
            cls.__routes__ = []
            for attr, value in attrs.items():
                if isinstance(value, tuple) and len(value) is 2:
                    cls.__routes__.append(value)

        super(MetaController, cls).__init__(name, bases, attrs)

class Controller(object):
    __metaclass__ = MetaController

    def __init__(self, settings=None):
        self.settings = settings

    @classmethod
    def get_all(cls):
        return __CONTROLLERS__

    def get_authenticated_user(self):
        return users.get_current_user()

    def create_single_mapping(self, route_info):
        http_method = route_info[1][1]['http_method']
        method = route_info[0]
        method_name = route_info[1][1]['method']
        route = route_info[1][1]['route']

        def execute_method(instance, *args, **kw):
            updated_args = list(args)
            if self in updated_args: updated_args.remove(self)
            if instance in updated_args: updated_args.remove(instance)
            
            arguments, varargs, varkw, defaults = inspect.getargspec(method)
            for argument in arguments:
                if argument == "self" or argument == "context": continue
                if instance.request.get(argument, None):
                    kw[argument] = instance.request.get(argument, None) 
            
            return method(self, instance, *updated_args, **kw)

        methods = {}
        methods[http_method.lower()] = execute_method

        new_class=classobj('RouteHandler%s' % method_name, (webapp.RequestHandler,), methods)

        return (route, new_class)

    def get_mappings(self):
        mappings = []
        for route in self.__routes__:
            mappings.append(self.create_single_mapping(route))
        return mappings

    def write_to_response(self, text, context):
        context.response.out.write(text)

    def render_to_response(self, template_name, context, **kw):
        current_dir = dirname(__file__)
        current_skin = self.settings.get('skin')
        ctrl_name = get_controller_name(self.__class__.__name__)
        path = join(current_dir, "..", "templates", current_skin, ctrl_name, template_name)
        context.response.out.write(template.render(path, kw))

    def redirect(self, url, context):
        context.redirect(url)
