from .NewPlayer import *
from .item_Trilha import *

class game(object):
	#modulo defaut 
	def __init__(self):
		#define algumas config basicas do game
		self.config ={
		"Posicoes"	: 50,		#numero de casas no tabuleiro
		"NPlayers"	: [2,4],	#numero de jogadores permitido, de X a Y 
		"TamRoleta"	: 4}		#posições possiveis na Roleta
		#lista de itens de sorte presentes no game
		#Podem ser adicionados ou removidos dinamicamente
		self.P_Sorte	= [
			["Ganhou na loteria",  5000],
		 	["Fez um bom Negocio", 1500],
		 	["Foi sorteado",  3500],
			["Ganhou na loteria",  5000],
		 	["Fez um bom Negocio", 1500],
		 	["Foi sorteado",  3500]]
		#lista de itens de Reves presentes no game
		#Podem ser adicionados ou removidos dinamicamente
		#antes do inicio da partida
		self.P_Reves = [
			["Bateu o Carro",		-5000],
			["Tv Queimou", 			-1500],
			["Perdeu SmartPhone",	-3500],
			["Bateu o Carro",		-5000],
			["Tv Queimou", 			-1500],
			["Perdeu SmartPhone",	-3500]]
		#lista com os jogadores da partida atual
		self.players=[]
		self.trilha = None

	#adiciona novo player
	def AddPlayer(self, nome):
		self.players.append(NewPlayer(nome))

	# sorteia a posição de cada casa de sorte ou revez na trilha
	def SortTrilhaGame(self, interavel):
		for item in interavel:
			while 1:
				key=random.randint(1, len(self.trilha)-1) #obtem uma posição numerica aleatorio de uma casa na trilha
				if self.trilha[key].action == None: #verifica se esta posição esta livre
					self.trilha[key].action = item  # define  sorte/revez como ação da casa 
					break
	
	# configura o game
	def configure(self):
		#gera a trilha do game
		self.trilha	= {x:item_Trilha(x) for x in range(self.config["Posicoes"])}
		self.SortTrilhaGame(self.P_Sorte)
		self.SortTrilhaGame(self.P_Reves)

	# giro da roleta, sorteia um numero
	def GiraRoleta(self):
		return random.randint(1, self.config["TamRoleta"])

	#retorna o ultimo item de um dicionario
	def LastItem(self, dic):
		return dic[list(dic.keys())[-1]]

	# Da inicio a partida
	def start(self):
		P_Fila=0
		random.shuffle(self.players)
		#enquanto status for 0,
		#ninguem chegou ao final da trilha, continua o game
		while self.LastItem(self.trilha).status==0:
			player	= self.players[P_Fila]
			Roleta	= self.GiraRoleta()
			P_prox	= min(player.posicao+Roleta, len(self.trilha)-1)
			while (P_prox<len(self.trilha)-2) and (self.trilha[P_prox].status!=0):
				P_prox+=1
			else:
				player.andar(P_prox, self)

			print(player.nome, player.posicao, player.saldo)

			#incrementa +1 a posição da fila, ou volta ao primeiro
			P_Fila=(P_Fila+1 if P_Fila < len(self.players)-1 else 0)
			time.sleep(0.5)
		else:
			print("")
			print('=='*30)
			print('Alguem terminou!')
			for player in self.players:
				print(player.posicao, player.nome, player.saldo)
