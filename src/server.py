#!/usr/bin/env python
#-*- coding:utf-8 -*-

from os.path import dirname, join, abspath
import sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from yaml import load

import controllers

def loadSettings():
    settings = load(open(abspath(join(dirname(__file__), 'settings.yaml')),'r').read())
    return settings

controllers = controllers.Controller.get_all()

mappings = []

my_settings = loadSettings()

for controller in controllers:
    ctrl = controller(settings=my_settings)
    mappings.extend(ctrl.get_mappings())

application = webapp.WSGIApplication(mappings, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
