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
        return float(self.quesitos[quesito]) / float(self.numero_votos)
