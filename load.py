#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib
import urllib2

def post():
    url = 'http://poccarn.appspot.com/vote'
    values = {'nota_evolucao' : '9',
              'nota_harmonia' : '6',
              'nota_ms_pb' : '8' }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print the_page

if __name__ == '__main__':
    for i in range(100):
        print
        print
        print "Request number %d" % (i + 1)
        post()
