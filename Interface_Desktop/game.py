import time
import uuid
import pygame
import random
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pygame.locals import *


Pool = ThreadPoolExecutor(12) #quantidade de precedimentos paralelos
Instance_list={} #lista de procedimentos assincronos em execução
pygame.init()



mapa_posicoes   =   {0:[80,325],1:[97,345],2:[135,355],3:[165,335],4:[170,300],5:[155,270],6:[130,250],7:[100,225],8:[75,200],9:[55,175],10:[50,140],11:[60,110],12:[80,80],13:[110,60],14:[140,55],15:[180,55],16:[210,75],17:[230,100],18:[235,140],19:[230,170],20:[220,200],21:[210,230],22:[200,260],23:[210,295],24:[240,320],25:[280,325],26:[295,290],27:[275,260],28:[265,225],29:[295,200],30:[330,210],31:[340,240],32:[345,280],33:[360,315],34:[380,340],35:[420,360],36:[460,360],37:[490,340],38:[520,305],39:[515,255],40:[480,225],41:[435,210],42:[400,200],43:[360,180],44:[330,165],45:[305,135],46:[300,95],47:[320,60],48:[360,40],49:[400,40],50:[435,65],51:[440,95]}

def fonte(name="Times New Roman", size=30):
	return pygame.font.SysFont(name, size)

def async_(function, Instance_list=Instance_list, calback=None):
    Instance_list[function.__name__] = Pool.submit(function)
    if calback is not None:
        Instance_list[function.__name__].add_done_callback(calback)


class Dados(object):

	images	=	{}

	def __init__(self, images,tela, width=160, heigth=160, pos_x=0, pos_y=0):
		self.tela		= tela
		self.pos_x		= pos_x
		self.pos_y		= pos_y
		self.dado_image	= None
		self.listeners		= {} 									# garda a relação de metodos x  eventos



		
		for key in images: #carrega todas as imagens
			self.images[key] = pygame.image.load(images[key]).convert()

		self.dado_image = Box(width=width, heigth=heigth, pos_x=pos_x, pos_y=pos_y) #cria um sprite
		self.rect		= self.dado_image.rect	#obtem o rect correspondente a superficie

		self.tela.elements.add(self.dado_image) #add o sprite a lista de elementos da tela
		self.dado_image.image = self.images[1]  #altera a imagem do sprite para dado_1
		'''
		pygame.draw.rect(tela.surface, (255,255,255), (480,150,150,150))
		pygame.display.update()
		'''

	def animar(self, sort):
		max_voltas = 2
		for volta in range(1,1+max_voltas): 				# repassa todos os dados ate 2 vezes
			for key in self.images:								# para cada imagem na lista
				self.dado_image.image = self.images[key] 	# altera a imagem do dado para a imagem da vez
				self.tela.elements.draw(self.tela.surface)	# manda  desenha os elements na tela
				pygame.display.update()	
				if (volta == max_voltas) and (key == sort): # se ja fora a ultima volta da animação, para no mumerdo de "sort"
					break
				else:
					time.sleep(0.25)						# pausa a animação por 0,25seg para ser visivel 
		
	def reset(self):
		pass # ainda sera implementado

	def on(self, event_name, function):				# add event
		if event_name not in self.listeners:		# verifica se ja existe algum ouvinte para o event_name
			self.listeners[event_name] =[]			# se nao, cria uma lista vazia para adicionar ouvintes
		self.listeners[event_name].append(function)	# add function para chamada  

	def event(self, event, origem=None):							# aguarda a ocorrencia de um evento e chama a o metodo correspondente
		if origem != self:
			origem=self
		for event_name in ("all", pygame.event.event_name(event.type)):
			if event_name in self.listeners:
				for listener in self.listeners[event_name]:
					listener(event, origem)



class Box(pygame.sprite.Sprite):
	def __init__(self, width=25, heigth=25, pos_x=0, pos_y=0, text=None, bgcolor=None, color=(0,0,0), fonte=fonte(), id=uuid.uuid1(), imageurl=None, addEventlistner=() ):
		super().__init__()
		self.id 			= id
		self.image			= (pygame.image.load(imageurl).convert() if imageurl is not None else pygame.Surface([width, heigth]))	#cria uma superficie
		self.rect			= self.image.get_rect()				#obtem o rect correspondente a superficie
		self.rect.topleft	= [pos_x, pos_y]					#posiciona em X e Y
		self.color 			= color
		self.bgcolor 		= bgcolor
		self.fonte			= fonte
		self.width 			= width
		self.heigth 		= heigth
		self.listeners		= {} 									# garda a relação de metodos x  eventos

		if bgcolor is not None and imageurl is None: # somente usa o preenchimento de cor solida se nao houver um arquivo de imagem carregado 
			self.image.fill(bgcolor) # preenche com uma cor solida
		else:
			self.image.set_colorkey((0,0,0))
		
		if text	 is not None:
			self.write(text)

		if len(addEventlistner)==2:
			self.on(addEventlistner[0], addEventlistner[1])

	def on(self, event_name, function):				# add event
		if event_name not in self.listeners:		# verifica se ja existe algum ouvinte para o event_name
			self.listeners[event_name] =[]			# se nao, cria uma lista vazia para adicionar ouvintes
		self.listeners[event_name].append(function)	# add function para chamada  

	def event(self, event, origem=None):							# aguarda a ocorrencia de um evento e chama a o metodo correspondente
		if origem != self:
			origem=self
		for event_name in ("all", pygame.event.event_name(event.type)):
			if event_name in self.listeners:
				for listener in self.listeners[event_name]:
					listener(event, origem)

	def write(self, text):
		self.txt		=	self.fonte.render(text, False, self.color)#rendeniza o texto com a fonte do sistemma
		self.txt_rect	=	self.txt.get_rect(center=(self.width/2, self.heigth/2))
		if self.bgcolor is not None:
			self.image.fill(self.bgcolor)
		self.image.blit(self.txt, self.txt_rect)

	def update(self, surface):
		gp = pygame.sprite.Group()
		gp.add(self)
		gp.draw(surface)
		gp.remove(self)
		gp=None


class Tela(object):

	def __init__(self, surface, color=(255,255,255)):
		self.color 		= color						# cor de fundo para esta tela
		self.display	= 0 						# esta visivel? 0 nao, 1 sim
		self.elements	= pygame.sprite.Group()		# grupo de elementos a redenizar em surface			
		self.heigth		= surface.get_height()		# obtem a altura da jela
		self.listeners	= {} 						# garda a relação de metodos x  eventos
		self.surface	= surface					# janela onde essa tela sera exibida
		self.width		= surface.get_width()		# obtem a altura da janela

	def on(self, event_name, function):				# add event
		if event_name not in self.listeners:		# verifica se ja existe algum ouvinte para o event_name
			self.listeners[event_name] =[]			# se nao, cria uma lista vazia para adicionar ouvintes
		self.listeners[event_name].append(function)	# add function para chamada  

	def clearevent(self, event_name):				# remove ouvinte de um evento
		self.listeners.pop(event_name, None)

	def show(self):									# mostra a tela
		self.surface.fill(self.color)				# preenche a tela com cor solida
		self.elements.draw(self.surface)				# mostra todos elementos na tela
		self.display = 1

	def update(self):								# atualiza a tela
		pass

	def event(self, event, origem=None):							# aguarda a ocorrencia de um evento e chama a o metodo correspondente
		if origem != self:
			origem=self
		if self.display ==0:
			self.show()
		for event_name in ("all", pygame.event.event_name(event.type)):
			if event_name in self.listeners:
				for listener in self.listeners[event_name]:
					listener(event, origem)




class Menu(object):

	def __init__(self, surface, tela, callback,itens={}, title="Menu", width=0, height=0, size = 50, pos_x=0, pos_y=0, bgcolor=(192,192,192), color=(0,0,0), fonte=fonte()):
		self.item_foco	=	1
		self.pag_foco	=	1
		self.display	=	0
		self.listeners	=	{} 						# garda a relação de metodos x  eventos
		self.tela 		=	tela
		self.size		=	size
		self.color 		=	color
		self.bgcolor	=	bgcolor
		self.title		=	title
		self.surface	=	surface
		self.pos_x		=	pos_x
		self.pos_y		=	pos_y
		self.callback	=	callback
		self.itens		=	None
		self.width 		=	(width 	if width >0 else (int(surface.get_width())-pos_y) *0.75)
		self.height 	=	(height if height>0 else (int(surface.get_height())-pos_x)*0.9)
		self.itens_pag	=	int((self.height/(self.size+10))-1)
		self.contenier	=	pygame.Surface((self.width, self.height))
		self.elements	=	pygame.sprite.Group()

		self.setItens(itens)

		self.tela.on("all", self.event)
		self.on("KeyDown", self.change)
	
	def setItens(self, itens):
		self.itens=	(itens  if type(itens) is dict else {key:value for key, value in enumerate(itens)})
		self.pags =	int(len(self.itens)/self.itens_pag)
	
	def change(self, event, origem):
		if event == "show":
			self.update(event)
		elif pygame.event.event_name(event.type) =="KeyDown":
			if event.key in (K_UP, K_DOWN):
				 # -1 se tecla para cima, +1 se para baixo, sou 0 se  not 0 < item_foco < len(itens)
				update=(-1 if event.key==K_UP and self.item_foco > 0 else (1 if event.key==K_DOWN and self.item_foco < len(self.itens)-1 else 0) )
				if update !=0: # se +1 ou -1, necesario update
					self.item_foco +=update
					self.pag_foco = int(self.item_foco/self.itens_pag)+1
					self.update(event)
			elif event.unicode == "\r":
				keys = list(self.itens.keys())
				self.callback(self.itens[keys[self.item_foco]]["id"])

	def update(self, event):
			keys = list(self.itens.keys())
			self.contenier.fill(self.tela.color)
			self.surface.blit(self.contenier, (self.pos_x, self.pos_y))
			self.elements.remove(self.elements.sprites())

			for i, key in enumerate(keys[((self.pag_foco-1)*self.itens_pag):((self.pag_foco)*self.itens_pag)]):
				color, bgcolor = ((self.bgcolor, self.color) if key == self.item_foco else (self.color, self.bgcolor))
				self.elements.add(Box(self.width, self.size, self.pos_x,self.pos_y+((i)*(self.size+10)),self.itens[key]["text"],bgcolor=bgcolor, color=color))
			self.elements.draw(self.surface)			# mostra rodos elementos na tela
	
	def show(self, event):
		self.display = 1
		self.update(event)

	def on(self, event_name, function):				# add event
		if event_name not in self.listeners:		# verifica se ja existe algum ouvinte para o event_name
			self.listeners[event_name] =[]			# se nao, cria uma lista vazia para adicionar ouvintes
		self.listeners[event_name].append(function)	# add function para chamada  


	def event(self, event, origem=None):
		if origem != self:
			origem=self
		if self.display == 0:
			self.show("init")
		for event_name in ("all", pygame.event.event_name(event.type)):
			if event_name in self.listeners:
				for listener in self.listeners[event_name]:
					listener(event, origem)




class Player(object):

	def __init__(self, info):
		self.id			=	None
		self.icon 		=	None
		self.posicao	=	0
		self.saldo		=	1000
		for key in info: # se alguma informação recebida fore diferente, sobrescreve
			setattr(self, key, info[key])

	def getId(self):
		return self.id

	def andar(self, dest):
		print("Vou andar de ", self.posicao ,"para", dest)
		while self.posicao< dest:
			self.posicao+=1
			print(self.posicao)
			self.icon.rect.center=(mapa_posicoes[self.posicao])
			tela3.elements.draw(tela3.surface)
			time.sleep(0.5)
			pygame.event.get()
			pygame.display.update()




class Interface(object):

	
	def __init__(self):
		self.DataBase_url	= "https://jogodavida-2020-default-rtdb.firebaseio.com/"
		self.title_janela	= ".::Jogo da Vida::."
		self.largura		= 750	#dimenções da janela
		self.altura			= 410	#dimenções da janela
		self.rodada			= None	#armazena o numero da rodada para evitar download de dados desnecessarios do banco de dados
		self.partida_id		= None
		self.jogador_da_vez	= None
		self.future_		= {}	#chamadas de procedimentos assincronos rodando em threads diferentes
		self.telas			= {}
		self.players		= {}
		self.user			= {}
		self.nickname		= ""
		self.tela_atual		= 0		#primeira tela a ser mostrada

	def start(self):
		pygame.init() # inicia a biblioteca pygame
		pygame.display.set_caption(self.title_janela)
		self.window	 = pygame.display.set_mode((self.largura, self.altura))

	def fonte(self, name=pygame.font.get_default_font(), size=30):
		return pygame.font.SysFont(name, size)

	def tela_add(self, tela, key):
		self.telas[key]=tela


	def firebase(self, url, method, data=None, parans=None, headers=None):
		url = self.DataBase_url +url+".json"
		headers = {'content-type': 'application/json'}
		request = { #dicionario de funções lambda que execuam as requisições de acordo com o "method"
			"get"   : lambda url, data, parans, headers: requests.get(url,headers=headers),
			"post"  : lambda url, data, parans, headers: requests.post(url,data=json.dumps(data), headers=headers),
			"put"   : lambda url, data, parans, headers: requests.put(url, data=json.dumps(data), headers=headers)} 
		return (request[method](url, data, parans, headers).text if method in request else False)



	def loop(self):
		while True:
			if self.telas[self.tela_atual].display == 0:
				self.telas[self.tela_atual].show()
				print("show")
			
			for event in pygame.event.get():
				if event.type == QUIT:
					self.tela_atual=None
					pygame.quit()
					exit()        
				self.telas[self.tela_atual].event(event)
			pygame.display.update()
			pygame.time.Clock().tick(5)
		


itensmenu1=[]

#######################################
## procedimentos para primeira Tela
def input_nickname(event, origem):
	nick_char_permitidos = "abcdefghijklmnopqrstuvxywz0123456789-_ "
	if event.unicode.lower() in nick_char_permitidos:
		interface.nickname+=event.unicode
	elif event.unicode == "\x08": # backspace
		interface.nickname=interface.nickname[:-1]
	elif event.unicode == "\r": #enter
		print("Enter") # terminou de digitar o nick

	for item in list(tela0.elements.sprites()):
		if item.id =="nickname":
			tela0.elements.remove(item)
			item.write(interface.nickname)
			tela0.elements.add(item)
			break

	tela0.elements.update(tela0.surface)

def click_bt_entrar(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		interface.user["nome"] = interface.nickname
		interface.user["id"]   = str(uuid.uuid4())
		print(interface.firebase("Usuarios/"+interface.user['id'], "put", interface.user))

		interface.tela_atual=1
		async_(get_lista_partidas)
		print("clicou em Entrar")

#######################################
## procedimentos para segunda Tela
def click_bt_nova_partida(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		Uuid=str(uuid.uuid4())
		interface.firebase("jogos/"+Uuid, "put", {"id":Uuid})
		interface.firebase("jogos/"+Uuid+"/players/"+interface.user["id"]+"/", "put", interface.user)
		interface.partida_id = Uuid
		interface.tela_atual=2
		async_(get_lista_players)

def select_partida(id):
	interface.partida_id = id
	interface.firebase("jogos/"+id+"/players/"+interface.user["id"]+"/", "put", interface.user)
	interface.tela_atual=2
	async_(get_lista_players)

def get_lista_partidas():
	while interface.tela_atual==1:
		try:
			time.sleep(0.5)
			data = json.loads(interface.firebase("jogos", "get"))
			N_data=[]
			for key in data:
				if (data[key]!="a") and (data[key]["status"] == "AddPlayers"):
					N_data.append({"id":key, "text":key+"_txt"})

			if len(N_data)==0:
				continue

			if interface.tela_atual==1:
				menu_lista_partidas.setItens(N_data)
				menu_lista_partidas.update("show")
		except Exception as e:
			print("ocorreu o seguinte erro", e)


#######################################
## procedimentos para terceira Tela
def click_bt_init_part(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		print("clicou em iniciar partida")

def get_lista_players():
	while interface.tela_atual==2:
		data = json.loads(interface.firebase("jogos/"+interface.partida_id+"/players/", "get"))
		
		if len(data)>=2:
			interface.tela_atual=3
			Prepara_tabuleiro(data)

		if interface.tela_atual==2:
			menu_lista_players.setItens([{"id":key, "text":data[key]["nome"]} for key in data])
			menu_lista_players.update("show")
		time.sleep(0.5)

#######################################
## procedimentos para quarta Tela
def  testa_movimento(event, origem):
	for key in interface.players:
		interface.players[key].andar(10)

def Prepara_tabuleiro(data):
	print("prepare")
	tela3.elements.add(Box(width=170, heigth=30 , pos_x=5, pos_y=7, bgcolor=(192,192,192), text=interface.user["nome"], fonte=fonte(size=20) ))
	for i, key in enumerate(data, start=1):
		interface.players[key]		=	Player(data[key])											# CHAMA  a class Player para cada jogador na partida
		interface.players[key].icon	=	Box   (imageurl="icon_"+str(i)+"-removebg-preview.png") 	# vincula um icone a ele
		interface.players[key].icon.rect.center=(mapa_posicoes[0]) 									#posiciona o icone na posiçao 0 do tabuleiro (inicio)
		tela3.elements.add(interface.players[key].icon) 											# adiciona o icone dele a lista de elementos da tela

		#gera o nome + saldo de cada player para ser mostrado no placar
		text = interface.players[key].nome +" R$"+ str(interface.players[key].saldo)
		interface.players[key].Text_placar = Box(width=160, heigth=30 , pos_x=575, pos_y=245+(i*32), bgcolor=(100,100,100), text=text, fonte=fonte(size=15) )
		tela3.elements.add(interface.players[key].Text_placar)

		#identidicador de quem é o jogador da Vez
		interface.txt_prox_aJogar = Box(width=160, heigth=25 , pos_x=575, pos_y=210, bgcolor=(100,100,100), text="Loading...", fonte=fonte(size=18) )
		tela3.elements.add(interface.txt_prox_aJogar)
		async_(load_update_db)

#este modulo contem um loop que pode gerar um bloqueio na aplicação se for chamado na Thread principal
#portanto deve ser chamado usando o modulo '''async_()'''
#ele busca continuamente atualizações no banco de dados referente ao status do jogo
def load_update_db():
	print("Loop de atualização do banco de dados iniciado")
	while interface.tela_atual == 3:
		ult_jogada=None
		try:
			data = interface.firebase("jogos/"+interface.partida_id+"/VezDeJogar", "get").replace('"', "", 2)
			if (interface.jogador_da_vez != data) and (data in interface.players):
				interface.txt_prox_aJogar.write(interface.players[data].nome)
				tela3.elements.draw(interface.window)
				interface.jogador_da_vez = data
				print("agora e a vez de ", data)

				if (interface.jogador_da_vez is not None):
					jogada = json.loads(interface.firebase("jogos/"+interface.partida_id+"/jogada", "get"))
					if (jogada != ult_jogada) and (interface.players[jogada["id"]].posicao != jogada["P_prox"]):
						print(jogada["Roleta"])
						interface.dado.animar(jogada["Roleta"])
						interface.players[jogada["id"]].andar(jogada["P_prox"])
						ult_jogada=jogada 


			time.sleep(0.5)
		except Exception as e:
			print(" EM 'load_update_db' ocorreu o seguinte erro", e )
	else:
	 	print("Tela incorreta")


def click_efetuar_Jogada(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		print("jogar")
		if interface.jogador_da_vez == interface.user["id"]:
			interface.txt_prox_aJogar.write("Loading...")
			async_(efetuar_Jogada)
	else:
		print("fora de  area")



def efetuar_Jogada():
	interface.firebase("jogos/"+interface.partida_id+"/VezDeJogar", "put", None)




'''
def Move_icon(dest, player):
	for key in mapa_posicoes:
		player.icon.rect.center=(mapa_posicoes[key])
		tela3.elements.draw(tela3.surface)
		time.sleep(0.5)
		pygame.event.get()
		pygame.display.update()
'''


#######################################
## procedimentos para Tela  XXXXXXXXXXXXX

def click_bt_close(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		print("Bt close click")


def click_bt_meus_result(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		interface.window.fill((192,192,192), (200,30,500,350))
		tela9.elements_meus_results.draw(interface.window)
		print("click_bt_meus_result")



def click_bt_sobre(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		interface.window.fill((192,192,192), (200,30,500,350))
		tela9.elements_sobre.draw(interface.window)

def click_bt_maiores_pontos(event, origem):
	if origem.rect.collidepoint(event.pos): # verifica se o click foi no BT
		interface.window.fill((192,192,192), (200,30,500,350))
		tela9.elements_maiores_pontos.draw(interface.window)


interface = Interface()
interface.start()



#######################################
## Primeira tela: Login
#######################################
tela0	=	Tela(surface=interface.window)
tela0.elements.add(Box(350,300, 150,50, bgcolor=(192,192,192)))
tela0.elements.add(Box(350, 40, 150,70, bgcolor=(192,192,192), color=(0,0,0), text="Login", fonte=fonte(size=35)))
tela0.elements.add(Box(350, 40, 150,120, bgcolor=(192,192,192), color=(0,0,0), text="Insira seu Nick Name:", fonte=fonte(size=15)))
tela0.elements.add(Box(320, 40, 165,150, bgcolor=(100,100,100), color=(0,0,0), id="nickname",  fonte=fonte(name="calibri", size=45)))

tela0.elements.add(Box(350, 40, 150,200, bgcolor=(192,192,192), color=(0,0,0), text="Escolha seu icone:", fonte=fonte(size=15)))
tela0.elements.add(Box(imageurl="icon_1-removebg-preview.png", pos_x=250, pos_y=250))
tela0.elements.add(Box(imageurl="icon_2-removebg-preview.png", pos_x=300, pos_y=250))
tela0.elements.add(Box(imageurl="icon_3-removebg-preview.png", pos_x=350, pos_y=250))
tela0.elements.add(Box(imageurl="icon_4-removebg-preview.png", pos_x=400, pos_y=250))

bt_entrar =  Box(width=60, heigth=25, pos_x=420, pos_y=310, bgcolor=(0,144,255), color=(0,0,0), text="Entrar", fonte=fonte(size=15))
tela0.on("MouseButtonUp", bt_entrar.event)
bt_entrar.on("MouseButtonUp", click_bt_entrar)
tela0.elements.add(bt_entrar)

tela0.on("KeyDown", input_nickname)
interface.tela_add(tela0, 0)



#######################################
## Segunda tela: lista de partidas disponives para jogar
#######################################
tela1	=	Tela(surface=interface.window)
bt_nova_partida= Box(120, 30, 450,15, text="Nova Partida", bgcolor=(192,192,192), fonte=fonte(size=25))
bt_nova_partida.on("MouseButtonUp", click_bt_nova_partida)
tela1.on("MouseButtonUp", bt_nova_partida.event)
tela1.elements.add(bt_nova_partida)
menu_lista_partidas 	=	Menu(surface=interface.window, tela=tela1, itens=itensmenu1,callback=select_partida,  pos_x=70, pos_y=70,size=30, width=500)
interface.tela_add(tela1, 1)




#######################################
## Terceira tela: lista de jogadores na partida
#######################################
tela2	=	Tela(surface=interface.window)
tela2.elements.add(Box(500, 30, 30,10, text="Aguardando outros jogadores!!", bgcolor=(192,192,192), fonte=fonte(size=25)))
tela2.elements.add(Box(500, 30, 30,330, text="Quando 2 jogadores estiverem presentes, podera iniciar a Partida.", bgcolor=(192,192,192), fonte=fonte(size=16)))
tela2.elements.add(Box(500, 30, 30,360, text="Quando 2 jogadores estiverem presentes, a Partida inicia automaticamente.", bgcolor=(192,192,192), fonte=fonte(size=16)))
bt_init_part = Box(150, 30, 380,290, text="Iniciar Partida", bgcolor=(192,192,192), fonte=fonte(size=20))
tela2.on("MouseButtonUp", bt_init_part.event)
bt_init_part.on("MouseButtonUp", click_bt_init_part)
tela2.elements.add(bt_init_part)
menu_lista_players 	=	Menu(surface=interface.window, tela=tela2, itens=itensmenu1[0:4],callback=print,  pos_x=30, pos_y=70,size=30, width=500, height=200)
interface.tela_add(tela2, 2)




#######################################
## quarta tela: tela de jogo, tabuleiro
#######################################
tela3	=	Tela(surface = interface.window)
tela3.elements.add(Box(imageurl="trilha.png"))


#tela3.on("MouseButtonUp", testa_movimento)

#dicionario contendo o url de cada imagem do dado (de 1 a 6)
images_dados = { key:"dados/dado"+str(key)+".png" for key in range(1,7)}

interface.dado = Dados(images_dados, tela3, width=50, heigth=50, pos_x=570, pos_y=0)
interface.dado.on("MouseButtonUp", click_efetuar_Jogada)
interface.dado.on("K_DOWN", click_efetuar_Jogada)
tela3.on("MouseButtonUp", interface.dado.event)
interface.dado.animar(3)

#placar
tela3.elements.add(Box(width=170, heigth=60, pos_x=570, pos_y=180, bgcolor=(192,192,192)))
tela3.elements.add(Box(width=170, heigth=30 , pos_x=570, pos_y=180, bgcolor=(192,192,192), text="Proximo a jogar", fonte=fonte(size=20) ))

tela3.elements.add(Box(width=170, heigth=160, pos_x=570, pos_y=245, bgcolor=(192,192,192)))
tela3.elements.add(Box(width=170, heigth=30 , pos_x=570, pos_y=245, bgcolor=(192,192,192), text="Participantes", fonte=fonte(size=20) ))


Bt_config = Box(imageurl="Engrenagem.png", pos_x=510, pos_y=5)
tela3.on("MouseButtonUp", Bt_config.event)
#Bt_config.on("MouseButtonUp", print)
tela3.elements.add(Bt_config)

interface.tela_add(tela3, 3)

'''
for id in interface.players:
	casas = random.randint(1,20)
	interface.players[id].andar(casas)
'''


###############################################
## xxxxxxx tela: tela de opções, configurações
###############################################

tela9	=	Tela(surface = interface.window)

tela9.elements.add(Box(width=170, heigth=400, pos_x=5, pos_y=5, bgcolor=(192,192,192)))

bt_meus_result=Box(width=160, heigth=25,  pos_x=10, pos_y=15, bgcolor=(192,192,192), text="Resultados", fonte=fonte(size=18))
bt_meus_result.on("MouseButtonUp", click_bt_meus_result)
tela9.elements.add(bt_meus_result)


bt_maiores_pontos=Box(width=160, heigth=25,  pos_x=10, pos_y=45, bgcolor=(192,192,192), text="Maiores pontuações", fonte=fonte(size=18))
bt_maiores_pontos.on("MouseButtonUp", click_bt_maiores_pontos)
tela9.elements.add(bt_maiores_pontos)

bt_sobre = Box(width=160, heigth=25,  pos_x=10, pos_y=75, bgcolor=(192,192,192), text=".::Sobre::.", fonte=fonte(size=18))
bt_sobre.on("MouseButtonUp", click_bt_sobre)
tela9.elements.add(bt_sobre)


tela9.elements.add(Box(width=560, heigth=400, pos_x=185, pos_y=5, bgcolor=(192,192,192)))

bt_close=Box(width=70, heigth=20,  pos_x=670, pos_y=10, bgcolor=(192,192,192), text="::Fechar::", fonte=fonte(size=15))
bt_close.on("MouseButtonUp", click_bt_close)
tela9.elements.add(bt_close)




tela9.on("MouseButtonUp", bt_close.event)
tela9.on("MouseButtonUp", bt_sobre.event)
tela9.on("MouseButtonUp", bt_meus_result.event)
tela9.on("MouseButtonUp", bt_maiores_pontos.event)

#sub telas
tela9.elements_meus_results   = pygame.sprite.Group()
tela9.elements_meus_results.add(Box(500, 20, 200,50, bgcolor=(100,100,100), color=(255,255,255),text="Resultados da Partida", fonte=fonte(size=15)))
for x in range(4):
	tela9.elements_meus_results.add(Box(500, 20, 200,70+(x*25), bgcolor=(255,255,255), color=(0,0,0),text="Jogador_"+str(x), fonte=fonte(size=15)))




tela9.elements_maiores_pontos = pygame.sprite.Group()
tela9.elements_maiores_pontos.add(Box(500, 20, 200,50, bgcolor=(100,100,100), color=(255,255,255),text="JOgadores com Maiores Pontuações", fonte=fonte(size=15)))
for x in range(10):
	tela9.elements_maiores_pontos.add(Box(500, 20, 200,70+(x*25), bgcolor=(255,255,255), color=(0,0,0),text="Jogador_"+str(x), fonte=fonte(size=15)))


tela9.elements_sobre = pygame.sprite.Group()
tela9.elements_sobre.add(Box(500, 20, 200,50, bgcolor=(255,255,255), color=(0,0,0),text="Programa desenvolvido para avaliação final do 2º simestre", fonte=fonte(size=15)))
tela9.elements_sobre.add(Box(500, 20, 200,70, bgcolor=(255,255,255), color=(0,0,0),text="Diciplina: Laboratorio de Programação", fonte=fonte(size=15)))
tela9.elements_sobre.add(Box(500, 20, 200,90, bgcolor=(255,255,255), color=(0,0,0),text="Curso: Analise e Desenvolvimento de sistema", fonte=fonte(size=15)))
tela9.elements_sobre.add(Box(500, 20, 200,110, bgcolor=(255,255,255), color=(0,0,0),text="Turma: 2020.1", fonte=fonte(size=15)))
tela9.elements_sobre.add(Box(500, 20, 200,130, bgcolor=(255,255,255), color=(0,0,0),text="Prof: Danilo", fonte=fonte(size=15)))
tela9.elements_sobre.add(Box(500, 20, 200,150, bgcolor=(255,255,255), color=(0,0,0),text="IFBA Campus Eunapolis", fonte=fonte(size=15)))



#tela9.elements_sobre.add(Box(text=" \n \n "))


interface.tela_add(tela9, 9)


interface.loop()