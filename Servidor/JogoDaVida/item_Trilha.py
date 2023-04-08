import random
import time
class item_Trilha(object):
	def __init__(self, number):
		self.number = number
		self.status=0
		self.player=None
		self.action=None

	#acionado quando o usuario entrar na casa e 
	#houver uma ação de bonus ou reves para executar
	def ExecAction(self, player):
		print(player.nome,  self.action)
		player.saldo += self.action[1]

	#acionado quando o jogador entra na posição
	def entra(self, player):
		player.posicao=self.number
		self.status=1
		self.player=player
		if self.action != None:
			self.ExecAction(player)

	#acionado quando o jogador sai da posição
	def sair(self):
		self.player=None
		self.status=0

	

####################################################################################################################
####################################################################################################################
####################################################################################################################

