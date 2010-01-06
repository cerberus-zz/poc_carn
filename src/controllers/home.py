#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task
import logging
from base import Controller, get, post, json, authenticated
from models import *

escola = "Mocidade"
retries = 20

class HomeController(Controller):
    def __init__(self, settings=None):
        super(HomeController, self).__init__(settings)

    @get("/include")
    def index(self, context):
        self.render_to_response("index.html", context, escola=escola)

    @get("/")
    def test(self, context):
        self.render_to_response("included.html", context)

    @post("/vote")
    def vote(self, context, nota_evolucao, nota_harmonia, nota_ms_pb):
        task = Task(url="/resolvevote", params={'nota_evolucao': nota_evolucao, "nota_harmonia": nota_harmonia, "nota_ms_pb": nota_ms_pb})
        task.add(queue_name='carnaval')

    @post("/resolvevote")
    def resolve_vote(self, context, nota_evolucao, nota_harmonia, nota_ms_pb):
        votacao_db = db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(1)
        db.run_in_transaction_custom_retries(retries, self.save_vote, votacao=votacao_db, nota_evolucao=nota_evolucao, nota_harmonia=nota_harmonia, nota_ms_pb=nota_ms_pb)

    def save_vote(self, **kw):
        votacao_db = kw['votacao']
        if not votacao_db:
            votacao = Votacao(numero_votos=0, escola=escola)
        else:
            votacao = votacao_db[0]
        votacao.numero_votos += 1
        votacao.put()

        quesitos = {}
        quesito_db = db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1", votacao.key()).fetch(3)

        for quesito in quesito_db:
            quesitos[quesito.quesito] = quesito

        nome_quesitos = ["nota_evolucao", "nota_harmonia", "nota_ms_pb"]
        for nome_quesito in nome_quesitos:

            if not nome_quesito in quesitos:
                quesito = NotaQuesito(parent=votacao, quesito=nome_quesito, nota_total=0)
            else:
                quesito = quesitos[nome_quesito]

            quesito.nota_total += int(kw[nome_quesito])
            quesito.put()

    @get("/result")
    @json
    def result(self, context):
        quesitos = {}
        numero_votos = 0
        votacao_db =  db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(1)

        if votacao_db:
            votacao = votacao_db[0]
            numero_votos = votacao.numero_votos
            quesitos_db = db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1", votacao.key()).fetch(3)

            for quesito_db in quesitos_db:
                quesitos[quesito_db.quesito] = quesito_db.nota_total

        nota_evolucao = 0
        nota_harmonia = 0
        nota_ms_pb = 0

        if numero_votos:
            nota_evolucao = float(quesitos.get('nota_evolucao', 0)) / float(numero_votos)
            nota_harmonia = float(quesitos.get('nota_harmonia', 0)) / float(numero_votos)
            nota_ms_pb = float(quesitos.get('nota_ms_pb', 0)) / float(numero_votos)

        self.render_to_response("result.html", context,
                votos=numero_votos,
                nota_evolucao=nota_evolucao,
                nota_harmonia=nota_harmonia, 
                nota_ms_pb=nota_ms_pb)

    @get("/zerar")
    def zerar(self, context):
        votacao_db =  db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(1)

        while db.run_in_transaction(self.executa_zerar, votacao_db):
            time.sleep(1)

        self.redirect("/", context)

    def executa_zerar(self, votacao_db):
        if votacao_db:
            quesitos_db = db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1", votacao_db[0].key()).fetch(500)

            if quesitos_db:
                db.delete(quesitos_db)
                return True
            else:
                votacao_db[0].delete()
                return False

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


