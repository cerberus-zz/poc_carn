#!/usr/bin/env python
#-*- coding:utf-8 -*-

from base import Controller, get, post, json, authenticated

class Escola(object):
    def __init__(self, name):
        self.name = name

class HomeController(Controller):
    @get("/")
    def index(self, context):
        escola = Escola("Mocidade Independente de Padre Miguel")
        self.render_to_response("index.html", context, escola=escola)

#    @get("/linked")
#    def linked_content(self, context):
#        self.write_to_response("linked content was here<br /><a href='/'>Home</a>", context)

#    @get("/json")
#    @json
#    def json_view(self, context):
#        node = JsonNode('node1','node1')
#        child_node = JsonNode('node2','node2')
#        child_node2 = JsonNode('node3','node3')
#        node.children.append(child_node)
#        node.children.append(child_node2)

#        self.write_to_response(node.to_str(), context)

#    @get("/new")
#    @authenticated
#    def new(self, context):
#        self.render_to_response("new.html", context)
#    
#    @post("/create_idea")
#    def create_idea(self, context, idea):
#        idea = IdeaNode(text=idea, owner=self.get_authenticated_user())
#        idea.put()
#        self.redirect("/", context)


