import random
import time
#molde do player com suas propriedades
class NewPlayer(object):
	def __init__(self, nome, id):
		self.id = id
		self.nome	 = nome
		self.saldo	 = 10000
		self.posicao = 0

	def andar(self, P_prox, jogo):
		jogo.trilha[self.posicao].sair()
		jogo.trilha[P_prox].entra(self)