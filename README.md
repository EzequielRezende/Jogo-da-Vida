# Jogo-da-Vida

Programa desenvolvido como avaliação final da diciplina Laboratório de Programação, ofertado no segundo semestre do curso Analise e Desenvolvimento de Sistemas do IFBA campus Eunápolis-Ba 

Jogo da Vida, é um jogo de tabuleiro online,  mult-player e mult-partidas.

Desenvolvido em duas partes
 
Um Servidor: É executado e gerencia cada partida criada.
uma partida aceita novos jogadores ate atingir o numero maximo definido pelo adm do servidor (defaut=4)

Uma Interface: Cada jogador deve executar sua interface em seu pc/desktop, e se já houver alguma partida criada ele pode entrar e jogar, se nao ele deve criar uma nova partida e aguardar por outros jogadores
obs: a interface web começou a ser desenvolvida mas foi pausada para dar prioridade a interface desktop desenvolvida com Pygame, possivelmente esta sera terminada junto a disciplina de Desenvolvimento Web, ou em outra oportunidade.


iniciar servidor
	python main.py

iniciar interface grafica
	python game.py

