#4CÓDIGO QUE EXECUTA O BÁSICO DE UM PROGRAMA COM INTERFACE GRÁFICA
from concurrent.futures import ThreadPoolExecutor, as_completed
from pygame.locals import *
from sys import exit
import requests
import random
import pygame
import time
import uuid
import json

Pool = ThreadPoolExecutor(12) #quantidade de precedimentos paralelos
Instance_list={} #lista de procedimentos assincronos em execução

class Interface(object):
    
    def __init__(self):
        self.mapa_posicoes   =   {0:[80,325],1:[97,345],2:[135,355],3:[165,335],4:[170,300],5:[155,270],6:[130,250],7:[100,225],8:[75,200],9:[55,175],10:[50,140],11:[60,110],12:[80,80],13:[110,60],14:[140,55],15:[180,55],16:[210,75],17:[230,100],18:[235,140],19:[230,170],20:[220,200],21:[210,230],22:[200,260],23:[210,295],24:[240,320],25:[280,325],26:[295,290],27:[275,260],28:[265,225],29:[295,200],30:[330,210],31:[340,240],32:[345,280],33:[360,315],34:[380,340],35:[420,360],36:[460,360],37:[490,340],38:[520,305],39:[515,255],40:[480,225],41:[435,210],42:[400,200],43:[360,180],44:[330,165],45:[305,135],46:[300,95],47:[320,60],48:[360,40],49:[400,40],50:[435,65],51:[440,95]}
        self.DataBase_url    =   "https://jogodavida-2020-default-rtdb.firebaseio.com/"
        self.image_tabuleiro =   "trilha.png"

        self.nickname     = ""
        self.user         = {}      # todas informações do jpogador
        self.largura      = 750     #dimenções da janela
        self.altura       = 410     #dimenções da janela
        self.tam_peca     = 10      #tamanho do icone do usuario
        self.dados        = [0]     # garda as imagens dos dados apos serem carregados
        self.rodada       = False   #armazena o numero da rodada para evitar download de dados desnecessarios do banco de dados
        self.foco_partida = 0       # item focado na lista de partidas
        self.itens_pagina = 7       # quantidade de itens por pagina 
        self.lista_partidas={}      # armazena as partidas disponiveis
        self.partida_id   = 0       # id a partida em andamento
        self.botoes       = {}      # armazena os botoes e seus atributos
        self.pagina       = 1       # a primeira janela tela a ser exibida quando carregar o programa

        self.future_      = {}      #chamadas de procedimentos assincronos rodando em threads diferentes


    def start(self):
        # inicia a biblioteca pygame
        pygame.init()
        pygame.display.set_caption(".::Jogo da Vida::.")
        self.fonte       = pygame.font.get_default_font()       ##### carrega com a fonte padrão
        self.window      = pygame.display.set_mode((self.largura, self.altura))
        self.tabuleiro   = pygame.image.load(self.image_tabuleiro).convert()
        for i in range(1,7):
            self.dados.append(pygame.image.load("dados/dado"+str(i)+".png"))

        self.tela_atual  = 2    # identificador de qual tela exibir
        self.telas       = {    #cada entrada no diconario representa um modulo que gerencia uma determinada tela do jogo
            0: lambda: self.tela_login(),    
            1: lambda: self.tela_lista_partidas(),    
            2: lambda: True,
            3: lambda: self.tela_tabuleiro()
        }
        self.acoes       = {    
            0: lambda event: self.acoes_tela_login(event),    
            1: lambda event: self.acoes_tela_lista_partidas(event),    
            2: lambda event:  True,    
            3: lambda event:  self.acoes_tela_tabuleiro(event)    
        }

        self.telas[self.tela_atual]() # manda abrir a primeira tela do programa
        self.loop() #abre o gerenciador de eventos



###########################################################################
#           TELAS
###########################################################################
    def tela_login(self):
        self.window.fill((0,0,0))
        pygame.draw.rect(self.window, (211,211,211), (130, 105, 300, 200))
        pygame.draw.rect(self.window, (150,150,150), (155, 200, 250, 35))
        self.window.blit(pygame.font.SysFont(self.fonte, 60).render("Nick Name:", 1, (100,100,100)),(150,120))
        self.window.blit(pygame.font.SysFont(self.fonte, 30).render(self.nickname, 1, (0,0,255)),(160,210))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Digite seu NickName e Press Enter:", 1, (0,0,0)),(170,240))
        pygame.display.update() #atualiza a tela.

    def tela_lista_partidas(self):
        self.window.fill((0,0,0))
        self.botoes["addpartida"]=pygame.draw.rect(self.window, (255,211,255), (450, 5, 100, 25))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Nova Partida", 1, (0,0,0)),(455, 10))
        chaves = list(self.lista_partidas.keys())
        #for i,item in enumerate(self.lista_partidas[((self.pagina-1)*self.itens_pagina):((self.pagina)*self.itens_pagina)]):
        for i,key in enumerate(chaves[((self.pagina-1)*self.itens_pagina):((self.pagina)*self.itens_pagina)]):
            color = ((211,211,211) if chaves[self.foco_partida] == key else (100,100,100))
            pygame.draw.rect(self.window, color, (30, ((1+i)*40), 500, 30))
            self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Partida: "+key+" Aguardando Jogadores", 1, (0,0,0)),(30, (((1+i)*40)+5 )))
        print(len(self.lista_partidas), self.foco_partida)
        pygame.display.update() #atualiza a tela.

    def tela_lista_jogadores(self, data={}):
        self.window.fill((0,0,0))
        ''' if (type(data) != type({})):
            data=json.loads(data.result())
        '''

        pygame.draw.rect(self.window, (255,211,255), (30, 40, 500, 30))
        pygame.draw.rect(self.window, (255,211,255), (430, 300, 100, 25))
        pygame.draw.rect(self.window, (255,211,255), (30, 330, 500, 50))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Aguardando entrada de outros Jogadores", 1, (0,0,0)),(140, (40+5 )))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Iniciar Partida", 1, (0,0,0)),(435, (300+5 )))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Quando 2 Jogadores estiverem presentes, podera iniciar o jogo", 1, (0,0,0)),(40, (330+5 )))
        self.window.blit(pygame.font.SysFont(self.fonte, 20).render("Quando 4 Jogadores estiverem presentes, o jogo inicia automaticamente", 1, (0,0,0)),(40, (350+5 )))

        if data== None: data={}
        '''
        for i,key in enumerate(data):
            pygame.draw.rect(self.window, (211,211,211), (30, ((2+i)*40), 500, 30))
            self.window.blit(pygame.font.SysFont(self.fonte, 20).render(data[key]["nome"], 1, (0,0,0)),(30, (((2+i)*40)+5 )))
        print(len(data), "Usuarios")
        if len(data)==2:
            self.tela_atual = 3
        '''
        pygame.display.update() #atualiza a tela.

    def tela_tabuleiro(self):
        self.window.fill((0,0,0))
        self.window.blit(self.tabuleiro, (0,0))
        pygame.display.update() #atualiza a tela.


        #pygame.draw.circle(window, (10, 0, 10), (mapa_posicoes[i][0],mapa_posicoes[i][1]), tam_peca)               

    def anima_dados(self, roleta, xy):
        i = 2 # quantas vezes motrar todos os dados
        for _ in range(i):
            for dado in self.dados[1:]:
                self.window.blit(dado, xy)
                pygame.display.update()
                time.sleep(0.15)
        self.window.blit(self.dados[roleta], xy)
        pygame.display.update()

###########################################################################
#          AÇÕES RELACIONADOS AOS EVENTOS DAS TELAS
###########################################################################
    def acoes_tela_login(self, event):
        if (event.type == KEYDOWN):
            if ((event.key>= 48 and event.key<=57) or (event.key>= 97 and event.key<=122) or ()) and len(self.nickname)<20: 
                self.nickname+=event.unicode
            elif event.key == 8:
                self.nickname= self.nickname[0:-1]
            elif (event.key == 13) or (event.key == 1073741912):
                self.cadastra_user(self.nickname)
                self.tela_atual=1

    def acoes_tela_lista_partidas(self, event):
        if (event.type == MOUSEBUTTONUP):
            if(self.botoes["addpartida"].collidepoint(event.pos)):
                async_(self.add_nova_partida) 
        elif event.key == K_UP:
            self.foco_partida +=(-1 if self.foco_partida > 0 else 0)  
            self.pagina = int(self.foco_partida/self.itens_pagina)+1  
        elif event.key == K_DOWN:
            self.foco_partida +=( 1 if self.foco_partida < len(self.lista_partidas)-1 else 0)
            self.pagina = int(self.foco_partida/self.itens_pagina)+1  
        elif (event.key == 13) or (event.key == 1073741912): #teclas Enter
            self.partida_id = list(self.lista_partidas.keys())[self.foco_partida]
            self.firebase("jogos/"+self.partida_id+"/players", "put", {self.user["id"]:self.user})
            self.tela_atual=2 #proxima tela _ Lista de jogadores da partida

    def acoes_tela_tabuleiro(self, event):
        if (event.type == KEYDOWN):
            if (event.key == 13) or (event.key == 1073741912):
                roleta = random.randint(1,6)
                print("numero sorteado", roleta)
                self.anima_dados(roleta, (570,0)) 


        pass

    def processa_data_partidas(self, data):
        update = False
        data = json.loads(data.result())
        if type(data) in (type("string"), type(None)):
            return 0
        for key in data:
            if (key not in self.lista_partidas):# and (data[key]["status"]=="AddPlayers"):
                self.lista_partidas[key]=data[key]
                update = True
        if update:
            self.telas[self.tela_atual]()

###########################################################################
#          OUTROS MODULOS
###########################################################################
    #modulo que da acesso ao banco de dados do firebase Relatime Database para operações de PUT, GET e POST
    def firebase(self, url, method, data=None, parans=None, headers=None):
        url = self.DataBase_url +url+".json"
        headers = {'content-type': 'application/json'}
        request = { #dicionario de funções lambda que execuam as requisições de acordo com o "method"
            "get"   : lambda url, data, parans, headers: requests.get(url,headers=headers),
            "post"  : lambda url, data, parans, headers: requests.post(url,data=json.dumps(data), headers=headers),
            "put"   : lambda url, data, parans, headers: requests.put(url, data=json.dumps(data), headers=headers)} 
        return (request[method](url, data, parans, headers).text if method in request else False)

    def add_player_partida(self):
        try:
            return self.firebase("jogos/" + Uuid, "put", {"id" : Uuid})
        except Exception as e:
            print("Ocorreu o seguinte erro:", e)

    def add_nova_partida(self):
        try:
            Uuid=str(uuid.uuid4())
            self.firebase("jogos/"+Uuid, "put", {"id":Uuid})
            self.firebase("jogos/"+Uuid+"/players", "put", {self.user["id"]:self.user})
            self.partida_id = Uuid
            self.tela_atual = 2
            return True
        except Exception as e:
            print("Ocorreu o seguinte erro:", e)

    def get_list_partidas_abertas(self):
        try:
            return self.firebase("jogos/", "get")
        except Exception as e:
            print("Ocorreu o seguinte erro:", e)


    def get_list_player_partida(self):
        time.sleep(0) # atrasa a requição para a cada 1seg.
        try:
            return self.firebase("jogos/"+self.partida_id+"/players/", "get")
        except Exception as e:
            print("Ocorreu o seguinte erro:", e)


    def cadastra_user(self, nickname):
        self.user={}
        self.user["nome"] = nickname
        self.user["id"]   = str(uuid.uuid4())
        print(self.firebase("Usuarios/"+self.user['id'], "put", self.user))


    def loop(self):
        while True:
            pygame.time.Clock().tick(10)

            if (self.tela_atual ==1) and ((self.get_list_partidas_abertas.__name__ not in Instance_list) or (Instance_list[self.get_list_partidas_abertas.__name__].done())):
                async_(self.get_list_partidas_abertas, calback=self.processa_data_partidas)

            elif (self.tela_atual ==2) and ((self.get_list_player_partida.__name__ not in Instance_list) or (Instance_list[self.get_list_player_partida.__name__].done())):
                async_(self.get_list_player_partida, calback=self.tela_lista_jogadores)
            
            for event in pygame.event.get():
                if self.tela_atual in self.telas: # tela de login
                    if (event.type == KEYDOWN) or (event.type == MOUSEBUTTONUP):
                        self.acoes[self.tela_atual](event)
                        self.telas[self.tela_atual]()

                elif self.tela_atual ==3:
                    self.acoes[self.tela_atual](event)
                    self.telas[self.tela_atual]()
                elif self.tela_atual ==4:
                    pass
                elif self.tela_atual ==5:
                    pass

               

                if event.type == QUIT:
                    pygame.quit()
                    exit()        

# coloca a "function" recebida para rodar de forma assincrona
# usando varias threads
def async_(function, Instance_list=Instance_list, calback=None):
    Instance_list[function.__name__] = Pool.submit(function)
    if calback is not None:
        Instance_list[function.__name__].add_done_callback(calback)

def main(): #instancia a classe
    app = Interface()
    print(app.future_)
    app.start() #esta deve ser a ultima linha do modulo, pois ela
                # chama o loop() que gera um bloqueio das linhas seguintes


main()
