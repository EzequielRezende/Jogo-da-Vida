import json
import uuid
from .NewPlayer import *
from .item_Trilha import *


class game(object):
	#modulo defaut 
	def __init__(self, id):
		self.id = id
		self.config ={			#define algumas config basicas do game
		"Posicoes"	: 50,		#numero de casas no tabuleiro
		"NPlayers"	: [2,6],	#numero de jogadores permitido, de X a Y 
		"TamRoleta"	: 6}		#posições possiveis na Roleta

		#listas de itens de sorte e revez presentes no game
		#Podem ser adicionados ou removidos dinamicamente
		self.P_Sorte	= [["Ganhou na loteria", 5000], ["Fez um bom Negocio",1500],["Foi sorteado",	 3500] ,["Ganhou na loteria", 5000],["Fez um bom Negocio",	1500] ,["Foi sorteado",		3500]]
		self.P_Reves 	= [["Bateu o Carro",	-5000],	["Tv Queimou", 		 -1500],["Perdeu SmartPhone",-3500],["Bateu o Carro",	 -5000],["Tv Queimou", 			-1500],["Perdeu SmartPhone",-3500]]
		self.players	= {} #dict com os jogadores da partida atual
		self.trilha 	= {} #info de todas as casas da trilha, quem é de revez, sorte ou neutra


	# configura o game
	def configure(self):
		#gera a trilha do game
		self.trilha	= {x:item_Trilha(x) for x in range(self.config["Posicoes"]+2)}
		self.SortTrilhaGame(self.P_Sorte) # sorteia as posições de sorte
		self.SortTrilhaGame(self.P_Reves) # sorteia as posições de reves


	# sorteia a posição de cada casa de sorte ou revez na trilha
	def SortTrilhaGame(self, itens):
		for item in itens:
			casa=random.randint(1, len(self.trilha)-1)
			while self.trilha[casa].action != None:
				casa=random.randint(1, len(self.trilha)-1) #obtem uma posição numerica aleatorio de uma casa na trilha
			else:
				self.trilha[casa].action = item  # define  sorte/revez como ação da casa 


	# adiciona um jogador
	def addPlayer(self, newplay):
		self.players[newplay["id"]] = NewPlayer(nome=newplay["nome"],id=newplay["id"] )


	# giro da roleta, sorteia um numero
	def GiraRoleta(self):
		return random.randint(5, self.config["TamRoleta"])


	#realiza a jogada do player da vez
	def realizaJogada(self, player):
		Roleta	= self.GiraRoleta()
		P_prox	= min(player.posicao+Roleta, len(self.trilha)-1) # menor valor, posição atual+roleta ou final da trilha
		print("Inicio da Jogada:", player.nome, player.posicao, player.saldo, "Instancia:", self.id)
		print("Roleta", Roleta, "Instancia:", self.id)
		while (P_prox<len(self.trilha)) and (self.trilha[P_prox].status!=0): #verifica se a proxima casa esta ocupada, se sim, pula ela p_prox++
			print("Prox. casa", P_prox, "ocupada, +1", "Instancia:", self.id)
			P_prox+=1
		else:
			retorno = [Roleta, P_prox, player.posicao]
			player.andar(P_prox, self)
			print("Jogada Finalizada", player.nome, player.posicao, player.saldo, "Instancia:", self.id, "\n"*2)
			return retorno


	# Da inicio a partida
	def start(self):
		self.fila = list(self.players.keys())
		random.shuffle(self.fila)
