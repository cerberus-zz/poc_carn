#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
import random
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.labs.taskqueue import Task
import logging
from base import Controller, get, post, json, authenticated, javascript
from models import *
from recaptcha import submit

escola = "Mocidade"
retries = 2
seed_count = 50

class HomeController(Controller):
    def __init__(self, settings=None):
        super(HomeController, self).__init__(settings)

    @property
    def public_key(self):
        return self.settings.get('public_key')

    @property
    def private_key(self):
        return self.settings.get('private_key')

    @get("/loadscript.js")
    @javascript
    def load_script(self, context):
        self.render_to_response("load_index.js", context, public_key=self.public_key)

    @get("/include")
    def index(self, context):
        self.render_to_response("index.html", context, escola=escola)

    @get("/")
    def test(self, context):
        self.render_to_response("included.html", context)

    @get("/abrir")
    def abrir(self, context):
        votacao_db = db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(seed_count)

        for votacao in votacao_db:
            while db.run_in_transaction(self.executa_zerar, votacao):
                time.sleep(1)

        for i in range(seed_count):
            votacao = Votacao(numero_votos=0, seed=i, escola=escola)
            votacao.put()

            nome_quesitos = ["nota_evolucao", "nota_harmonia", "nota_ms_pb"]
            for nome_quesito in nome_quesitos:
                quesito = NotaQuesito(parent=votacao, seed=i, quesito=nome_quesito, nota_total=0)
                quesito.put()

        self.redirect("/", context)

    @post("/vote")
    def vote(self, context, nota_evolucao, nota_harmonia, nota_ms_pb, recaptcha_challenge_field, recaptcha_response_field):
        remoteip = context.request.remote_addr
        logging.error("ip: %s" % remoteip)

#        result = submit(recaptcha_challenge_field,
#                        recaptcha_response_field,
#                        self.private_key,
#                        remoteip)

#        if not result.is_valid:
#            self.write_to_response('ERROR', context)
#            logging.error('result.error_code: %s' % result.error_code)
#        else:
        self.adiciona_na_fila(nota_evolucao, nota_harmonia, nota_ms_pb)
        self.write_to_response("OK", context)

    def adiciona_na_fila(self, nota_evolucao, nota_harmonia, nota_ms_pb):
        task = Task(url="/resolvevote", params={'nota_evolucao': nota_evolucao, "nota_harmonia": nota_harmonia, "nota_ms_pb": nota_ms_pb})
        task.add(queue_name='carnaval')

    @post("/resolvevote")
    def resolve_vote(self, context, nota_evolucao, nota_harmonia, nota_ms_pb):
        seed_id = random.randint(0, seed_count - 1)

        votacao_db =  db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1 and seed = :2", escola, seed_id).fetch(1)
        if not votacao_db:
            raise ValueError("Tem que abrir a votacao primeiro!")

        votacao = votacao_db[0]

#        try:
        db.run_in_transaction(self.save_vote, votacao=votacao, seed_id=seed_id, nota_evolucao=nota_evolucao, nota_harmonia=nota_harmonia, nota_ms_pb=nota_ms_pb)
#        except db.TransactionFailedError:
#            self.adiciona_na_fila(nota_evolucao, nota_harmonia, nota_ms_pb)
#        except db.Timeout:
#            self.adiciona_na_fila(nota_evolucao, nota_harmonia, nota_ms_pb)

    def save_vote(self, **kw):
        votacao = kw['votacao']

        seed_id = kw['seed_id']

        nome_quesitos = ["nota_evolucao", "nota_harmonia", "nota_ms_pb"]
        for nome_quesito in nome_quesitos:
            quesito_db =  db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1 and quesito = :2 and seed = :3", votacao.key(), nome_quesito, seed_id).fetch(1)
            quesito = quesito_db[0]
            quesito.nota_total += int(kw[nome_quesito])
            quesito.put()

        votacao.numero_votos += 1
        votacao.put()

    @get("/result")
    @json
    def result(self, context):
        quesitos = {}
        numero_votos = 0
        votacao_db =  db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(seed_count)

        if votacao_db:
            numero_votos = 0
            for votacao in votacao_db:
                numero_votos += votacao.numero_votos
                quesitos_db = db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1", votacao.key()).fetch(3 * seed_count)

                for quesito_db in quesitos_db:
                    if not quesito_db.quesito in quesitos:
                        quesitos[quesito_db.quesito] = 0

                    quesitos[quesito_db.quesito] += quesito_db.nota_total

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
        votacao_db =  db.GqlQuery("SELECT * FROM Votacao WHERE escola = :1", escola).fetch(seed_count)

        for votacao in votacao_db:
            while db.run_in_transaction(self.executa_zerar, votacao):
                time.sleep(1)

        self.redirect("/", context)

    def executa_zerar(self, votacao_db):
        if votacao_db:
            quesitos_db = db.GqlQuery("SELECT * FROM NotaQuesito WHERE ancestor IS :1", votacao_db.key()).fetch(3 * seed_count)

            if quesitos_db:
                for quesito in quesitos_db:
                    quesito.delete()
                return True
            else:
                votacao_db.delete()
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


