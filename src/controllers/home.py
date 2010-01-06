#!/usr/bin/env python
#-*- coding:utf-8 -*-

from threading import Lock
from google.appengine.api import memcache
from google.appengine.api.labs.taskqueue import Task
import logging
from base import Controller, get, post, json, authenticated
from models import Resultados

class Escola(object):
    def __init__(self, name):
        self.name = name

class HomeController(Controller):
    def __init__(self, settings=None):
        super(HomeController, self).__init__(settings)
        self.resultados_lock = Lock()


    @property
    def resultados(self):
        resultados = memcache.get("resultados")
        logging.error("resultados")
        if resultados is not None:
            logging.error("achou")
            return resultados
        else:
            logging.error("Nao Achou")
            resultados =  Resultados()
            if not memcache.set("resultados", resultados):
                logging.error("Memcache set failed.")
            return resultados
        
    @get("/include")
    def index(self, context):
        escola = Escola("Mocidade Independente de Padre Miguel")
        self.render_to_response("index.html", context, escola=escola)

    @get("/")
    def test(self, context):
        self.render_to_response("included.html", context)

    def armazena_resultados(self, resultados):
        memcache.set("resultados", resultados)

    @post("/vote")
    def vote(self, context, nota_evolucao, nota_harmonia, nota_ms_pb):
        logging.error("Colocando voto na fila")
        task = Task(url="/resolvevote", params={'nota_evolucao': nota_evolucao, "nota_harmonia": nota_harmonia, "nota_ms_pb": nota_ms_pb})
        task.add(queue_name='carnaval')

    @post("/resolvevote")
    def resolve_vote(self, context):
        nota_evolucao=10
        nota_harmonia=10
        nota_ms_pb=10
        logging.error("Processando voto")
        resultados = self.resultados
        resultados.votar(nota_evolucao=nota_evolucao, nota_harmonia=nota_harmonia, nota_ms_pb=nota_ms_pb)
        self.armazena_resultados(resultados)

    @get("/result")
    @json
    def result(self, context):
        self.render_to_response("result.html", context,
                votos=self.resultados.numero_votos,
                nota_evolucao=self.resultados.nota_atual('nota_evolucao'),
                nota_harmonia=self.resultados.nota_atual('nota_harmonia'), 
                nota_ms_pb=self.resultados.nota_atual('nota_ms_pb'))

    @get("/zerar")
    def zerar(self, context):
        self.resultados_lock.acquire()
        try:
            self.armazena_resultados(Resultados())
        finally:
            self.resultados_lock.release()
        self.redirect("/", context)

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


