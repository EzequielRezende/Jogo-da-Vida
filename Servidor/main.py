from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import requests
import JogoDaVida 

DataBase_url = "https://jogodavida-2020-default-rtdb.firebaseio.com/"


#modulo que da acesso ao banco de dados do firebase Relatime Database para operações de PUT, GET e POST
def firebase(url, method, data=None, parans=None, headers=None):
	url = DataBase_url +url+".json"
	headers = {'content-type': 'application/json'}
	request = { #dicionario de funções lambda que execuam as requisições de acordo com o "method"
		"get"	: lambda url, data, parans, headers: requests.get(url,headers=headers),
		"post"	: lambda url, data, parans, headers: requests.post(url,data=json.dumps(data), headers=headers),
		"put"	: lambda url, data, parans, headers: requests.put(url, data=json.dumps(data), headers=headers)} 
	return (request[method](url, data, parans, headers).text if method in request else False)


#retorna o ultimo item de um dicionario
def LastItem(dic):
	return dic[list(dic.keys())[-1]]


#adiciona novo player, modulo de acesso ao Firebase
def AddPlayers(game):
	print("Aguardando entrada dos jogadores para Instancia", game.id)
	while (len(game.players) < game.config["NPlayers"][0]) or ((firebase("jogos/"+game.id+"/status","get")== '"AddPlayers"') and (len(game.players) < game.config["NPlayers"][1])):
		data = json.loads(firebase("jogos/"+game.id+"/players","get"))
		if (data != None) and (len(game.players) != len(data) ):
			for key in data:
				newplay = data[key]
				try:
					if newplay["id"] not in game.players:
						game.addPlayer(newplay)
						print("jogador", newplay["nome"], newplay["id"], "entrou no jogo. Instancia:", game.id)
				except:
					#print("erro ocorrido... continue")
					continue
	else:
		firebase("jogos/"+game.id+"/status","put", "start")
		print("jogos/"+game.id+"/status","put", "start")
		print(len(game.players), "Jogadores Entraram, Iniciando partida.Instancia ", game.id, "\n"*2)


def aguardarJogadaWeb(game, player):
	inicio = time.time()
	while str(firebase("jogos/"+game.id+"/VezDeJogar","get")).replace("'", "").replace('"', ''""'')==str(player.id).replace("'", "").replace('"', ''""''):
		if time.time() - inicio < 30:
			time.sleep(1)
		else:
			return False
	else:
		return True


def loopGame(game):
	N_jogada = 0 # conta quantas rodadas aconteceram
	chegada = LastItem(game.trilha)# chegada corresponde a ultima casa da trilha

	while chegada.status==0: #reinicia a fila enquanto ninguem alcançar o fim da trilha
		for key in game.fila: # faz a fila andar, repassa cada jogador na fila
			N_jogada+=1
			firebase("jogos/"+game.id+"/VezDeJogar","put",game.players[key].id)
			print("Iniciando Rodada de Numero ", N_jogada, "da Instancia ", game.id)
			print("Aguardando", game.players[key].nome, "jogar!!" , "Instancia:", game.id)
			if aguardarJogadaWeb(game, game.players[key]):
				jogada = game.realizaJogada(game.players[key]) # aguarda o jogador fazer sua jogada
				firebase("jogos/"+game.id+"/players/"+str(game.players[key].id)+"/saldo","put", game.players[key].saldo)
				firebase("jogos/"+game.id+"/jogada","put",{
					"id"		:game.players[key].id,
					"nome"		:game.players[key].nome,
					"Roleta"	:jogada[0],
					"P_prox"	:jogada[1],
					"P_atual"	:jogada[2]
				})
			else:
				print(game.players[key].nome, "demorou muito a jogar, Perdeu a Vez", "\n"*2)
			if chegada.status!=0: break #para o jogo quando alguem chegar ao final da trilha
	else:
		firebase("jogos/"+game.id+"/status","put", "closed")
		firebase("Resultados/"+game.id+"/",	"put",{
			"time"		:	time.time(),
			"players"	:	{x:game.players[x].__dict__ for x in game.players},
		})

		print('=='*30)
		print('Alguem terminou!', "Instancia:", game.id)

		for key in game.players:
			print(game.players[key].posicao, game.players[key].nome, game.players[key].saldo)



# cria uma nova instancia do jogo 
def NewInstanceGame(id):
	jogo = JogoDaVida.game(id) #importa a class
	jogo.config["NPlayers"] = [2,2]
	jogo.configure()
	firebase("jogos/"+jogo.id+"/status","put", "AddPlayers")
	firebase("idJogos/", "post", jogo.id)
	AddPlayers(jogo)

	jogo.start()

	#adiciona dados ao banco (trilha, players, fila)
	firebase("jogos/"+jogo.id,	"put",{
		"trilha"	: { x:jogo.trilha[x].__dict__ for x in jogo.trilha			},
		"players"	: { x:jogo.players[x].__dict__ for x in jogo.players		},
		"fila"		: { str(x)+"_":value for x, value in enumerate(jogo.fila)	},
		"status"	:	"start"
	})

	loopGame(jogo) #loop criado para manipular de quem é a vez de jogar



#NewInstanceGame(id)
#arguments = []
def CheckAddGame(args):
	print("Servidor Iniciando....")
	print("Todas as partidas anteriores foram removidos!")
	print("Aguardando criação de novas partidas")

	firebase("jogos/","put", "a")
	while 1:
		data = json.loads(firebase("jogos/", "get"))
		for key in data:
			if key not in args["Instance_list"]:
				args["Instance_list"][key] = args["Pool"].submit(args["Function"], key)
		time.sleep(2)


MaxInstances = 20
Pool = ThreadPoolExecutor(MaxInstances)
Instance_list = {"a":"a"}

CheckAddGame({
	"firebase":firebase,
	"Instance_list":Instance_list,
	"Pool":Pool,
	"Function":NewInstanceGame
})
































'''
for x in as_completed(MultipleGames):
    print(x.result())
'''


##############################################
####### para fins de debug ###################
##############################################
'''
#Printa todos os jogadores
for x in jogo.players:
	print(x.nome)

#printa as configurações atuais do game
print(jogo.config)

#printa as posições de sorte configuradas no game
print(jogo.P_Sorte)

#printa as posições de reves configuradas no game
print(jogo.P_Reves)

#printa a Trilha completa
for x in jogo.trilha:
	print(jogo.trilha[x].number, jogo.trilha[x].status, jogo.trilha[x].player, jogo.trilha[x].action )

# gira roleta, 
print(jogo.GiraRoleta())



# '''
