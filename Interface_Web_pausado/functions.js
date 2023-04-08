cordenadas = {"0": [115, 480], "1": [140, 510], "2": [185, 520], "3": [230, 490], "4": [240, 440], "5": [220, 400], "6": [190, 370], "7": [145, 330], "8": [110, 294], "9": [80, 255], "10": [65, 205], "11": [80, 160], "12": [110, 115], "13": [150, 90], "14": [200, 75], "15": [250, 80], "16": [295, 110], "17": [320, 150], "18": [320, 200], "19": [325, 250], "20": [310, 290], "21": [295, 335], "22": [285, 380], "23": [295, 435], "24": [335, 470], "25": [390, 478], "26": [420, 420], "27": [385, 385], "28": [380, 330], "29": [415, 295], "30": [465, 310], "31": [485, 355], "32": [490, 410], "33": [505, 460], "34": [540, 500], "35": [590, 526], "36": [645, 530], "37": [700, 500], "38": [730, 440], "39": [725, 380], "40": [675, 330], "41": [620, 305], "42": [564, 285], "43": [505, 265], "44": [460, 240], "45": [430, 195], "46": [425, 135], "47": [450, 85], "48": [510, 55], "49": [565, 60], "50": [610, 95], "51": [625, 140]}

// pausa a execução por x ms
const delay = ms => new Promise(res => setTimeout(res, ms));


// seleciona um elemento pelo seu id
function getId(id){
	return  document.getElementById(id)
}


//seleciona um elemento usando uma query css
function query(_query){
	return document.querySelector(_query)
}


//move um elemento pela tela, de acordo com a tabela de coordenadas
function moveElement (element, local , destino){
	element.style.top	= (window.cordenadas[local][1]-15)+"px";
	element.style.left	= (window.cordenadas[local][0]-15)+"px";

	setTimeout(() =>{
		if(local<destino) {moveElement (element, ++local, destino)}		
	}, 700)
}


//gera um id unico
function create_UUID(){
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}


// calcula e gera o designer da roleta 
function calc_roleta(init){
	text_css = []
	elements = 6
	deg = 360/elements;
	i=1+init-1
	for (let x = 0; x <= elements; x++) {
		div=document.querySelector(".container div:nth-child(" + (x+1) + ")");
		div.style.transform = 'rotate(' + deg*x + 'deg)';
		div.innerHTML=i;
		if (elements%3==0) { variante = 0 } else { variante =  0.5}
		text_css.push("linear-gradient("+((x*deg)+(deg*variante))+"deg,transparent 49%, #000 49%, #000 51%, transparent 51%)")
		if(i==elements){i=1}else{i++}
	}
	
	getId("teste").innerHTML ="<style type='text/css'> .btn-fab { \n background-image:\n "+text_css.join(",\n")+"; }</style>"
	document.querySelector(".container").classList.add("btn-fab");
}


// gira roleta
function giraRoleta(NumSorteado){
	getId('AroRoleta').classList.add('image')
	calc_roleta(NumSorteado) // reordena as opções na roleta
	setTimeout(function(){
		getId('AroRoleta').classList.remove('image')	
	}, 2000)
}


//escreve "data" no banco de dados de acordo com especificações
function writeData(url, data, push, ondisconnect) {
	if(push){
		key = firebase.database().ref().child(url).push().key
		url += key	
	}
	firebase.database().ref(url).set(data);
	if(ondisconnect){
		firebase.database().ref(url).onDisconnect().set(null);
	}
	return firebase.database().ref(url).key
}


//cria uma nova partida no jogo
function criarPartida(){
	Uuid = create_UUID()
	writeData("jogos/"+ Uuid ,{ "id":Uuid }, false, false)
	writeData("jogos/"+ Uuid +"/players/"+window.user["id"], window.user, false, false)

}


//preenche informações na tela
function preenche_info(data){
	////////////////////////////////////////////////////////////
	/////preenche a lista de jogadores que estao entrando///////
	////////////////////////////////////////////////////////////
		count=0
		getId("listafila").innerHTML=""
		getId("lista_jogadores").innerHTML=""
		for (key in data.players){
			div =  document.createElement("div");
			if((data.status=="start" || data.status=="closed") && data.players[key].saldo!=undefined){
				div.classList.add("listPlayers"); 
				div.innerHTML='<div class="P_Nome">'+data.players[key].nome+'</div><div class="P_Saldo">'+data.players[key].saldo+'</div>'
				getId("listafila").append(div)
			}else{
				div.innerHTML=data.players[key].nome
				getId("lista_jogadores").append(div)
			}
			count++
 		query(".abas #n_p_p").innerHTML=count
		}

		if(data.VezDeJogar){
			getId("proxplayer").innerHTML= data.players[data.VezDeJogar].nome
		}
	////////////////////////////////////////////////////////////
	/////mostra a interface do game a atualiza regularmente/////
	////////////////////////////////////////////////////////////
	if(data.status =="start"){
		if("start" != window.status){
			cont = 0
			for (key in data.players){
					div = document.createElement("div")
					div.id = "icon"+key
					div.classList.add("icon")
					div.classList.add("icon"+(cont++))
					div.innerHTML= data.players[key].nome
					getId("trilha").append(div)
					console.log(div)
			}
			window.status = "start"
			window.location = "#jogo"

		}
		// verifica se é a vez de jogar e habilita o botao da roleta
		if(data.VezDeJogar == window.user["id"]){
			getId("bt_girar_roleta").disabled=false
		} else{
			getId("bt_girar_roleta").disabled=true
		}
	}
}