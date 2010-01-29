from google.appengine.ext import db

class Votacao(db.Model):
    numero_votos = db.IntegerProperty(required=True)
    seed = db.IntegerProperty(required=True)
    escola = db.StringProperty(required=True)

class NotaQuesito(db.Model):
    quesito = db.StringProperty(required=True)
    seed = db.IntegerProperty(required=True)
    nota_total = db.IntegerProperty(required=True)


