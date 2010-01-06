from google.appengine.ext import db

class Resultados(object):
    def __init__(self):
        self.numero_votos = 0
        self.quesitos = {}

    def votar(self, **kw):
        self.numero_votos += 1
        for quesito, nota in kw.items():
            if not quesito in self.quesitos:
                self.quesitos[quesito] = 0
            self.quesitos[quesito] += int(nota)

    def nota_atual(self, quesito):
        if quesito not in self.quesitos:
            return 0.0
        return float(self.quesitos[quesito]) / float(self.numero_votos)

#    def serializar(self):
#        resultados = Resultados(numero_votos=self.numero_votos)
#        resultados.put()

#        for quesito, nota_total in self.quesitos.items():
#            nota = NotaQuesito(resultados=resultados, quesito=quesito, nota_total=nota_total)
#            nota.put()

#    def deserializar(self):
#        
