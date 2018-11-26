# -*- coding: utf-8 -*-	
import sys
import time
import telebot
from telebot import types
import aimlManager
import pandas as pd
import re
from log import log
from unidecode import unidecode
import unicodedata
import Levenshtein as lev
import requests
from telebot.apihelper import get_file
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
# import logManager
# import woofyManager
# import imp

#telebot = imp.load_source('telebot', '/home/chatbot/lib/pyTelegramBotAPI/telebot/__init__.py')

# bot = telebot.TeleBot('712212286:AAHeG-tVXy-9rOWWDA9QiW7nPaz1n1r801E') # dev - maquina
LOCAL_BOT_TOKEN = '796929920:AAGiRRwj-_fXv245dDFXX87lh5V4Aw1ItU8'
bot = telebot.TeleBot(LOCAL_BOT_TOKEN) # local (para teste e manutenção)

aimlMgrDict = {}

# open csv ideb database 
df_ideb = pd.read_csv('tabelas/educ_ideb_rede_municipal.csv')

# open csv criminal database
df_isp = pd.read_csv('tabelas/BaseMunicipioMensal.csv', encoding = "ISO-8859-1", sep=";")

# month converter: written way to number
# month_converter = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

# column converter for ISP database
isp_column_converter = {
	u'hom_doloso': u'homicídios dolosos', 
	u'hom_culposo': u'homicídios culposos', 
	u'hom_culposo | hom_doloso': u'homicídios', 
	u'estupro': u'estupros', 
	u'sequestro': u'sequestros', 
	u'latrocinio': u'latrocinios', 
	u'pessoas_desaparecidas': u'pessoas desaparecidas', 
	u'estelionato': u'estelionatos', 
	u'roubo_comercio': u'roubos no comércio', 
	u'roubo_residencia': u'roubos de residência', 
	u'roubo_veiculo': u'roubos de veículos', 
	u'roubo_carga': u'roubo_carga', 
	u'roubo_transeunte': u'roubo_transeunte', 
	u'roubo_em_coletivo': u'roubo_em_coletivo', 
	u'roubo_banco': u'roubos de banco', 
	u'roubo_cx_eletronico': u'roubos de caixa eletrônico', 
	u'roubo_celular': u'roubos de celular', 
	u'roubo_conducao_saque': u'roubos por condução de saque', 
	u'roubo_bicicleta': u'roubos de bicicleta', 
	u'outros_roubos': u'de outros tipos de roubo', 
	u'total_roubos': u'roubos', 
	u'furto_veiculos': u'furtos de veículo', 
	u'furto_bicicleta': u'furtos de bicicleta', 
	u'outros_furtos': u'de outros furtos', 
	u'total_furtos': u'furtos'
}

def beforeTag(tag, frase):
	if hasTag(tag,frase):
		tagIni = frase.find(tag)
		frase = frase[0:tagIni]
	return frase  
			

def hasTag(tag, frase):
	if tag in frase :
		return True
	return False
   

def removeTag(tag, frase):
	if hasTag(tag,frase):
		tagIni = frase.find(tag)
		content = frase[tagIni + len(tag):len(frase)]
		return content
	return frase

		
def getTagContent(tag, frase, optToken = "♫"):
	if hasTag(tag,frase):
		content = removeTag(tag, frase)
		content = content.split(optToken)
		return content
	return frase
		

def getSession(cid):
	"""Get current user session - session expires after 20 minutes

	"""
	if cid in aimlMgrDict and ((time.time() - aimlMgrDict[cid].timestamp)/60 > 20):
		del aimlMgrDict[cid]
	
	if not cid in aimlMgrDict:
		aimlMgrDict[cid] = aimlManager.aimlManager()
		# sendAnswer(cid, processSpecialAnswer(cid, aimlMgrDict[cid].mensagem("start")))
		
	aimlMgrDict[cid].timestamp = time.time()
        
	return aimlMgrDict[cid]
        

def reservedCommands(cid, pergunta):
	"""Execute reserved commands

	"""

	userSession = getSession(cid)
	
	if pergunta == "dumpBrain":
		userSession.dumpBrain()
		bot.send_message(cid, "Regras Printadas no Servidor (Debug)")
		return True
	
	elif pergunta == "saveBrain":
		userSession.saveBrain()
		sendAnswer(cid, "Arquivo Brain Salvo")
		return True
	
	elif pergunta == "resetBrain":
		userSession.resetBrain()
		bot.send_message(cid, "Memoria Reiniciada")
		return True

	elif pergunta == "deleteBrain":
		userSession.deleteBrain()
		bot.send_message(cid, "Memoria Apagada")
		return True
	
	return False


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


def processSpecialAnswer(cid, resposta):

	if hasTag("►LEARN◄", resposta):
		nodeAiml = getTagContent("►LEARN◄", resposta)
		
		pattern = nodeAiml[0]
		template = nodeAiml[1]
		
		aimlManager.brainLearn(pattern,template)
		
		resposta = beforeTag("►LEARN◄", resposta)
	

	# TAGS PARA A BASE DO IDEB

	elif hasTag("►CSV IDEB IDEB ANO◄", resposta):
		variables = resposta.split(' ; ')[1:]
		municipio = variables[0]
		municipio = re.sub('^d[oae] ', '', municipio)
		match_year = re.search('(20\d\d)', variables[1])
		if match_year:
			year = match_year.group(1)
		else:
			return 'Desculpe, não entendi.'
		col = 'IDEB_AF_M_'
		try:
			df_temp = df_ideb[['Nome do Município', col + year]]
		except:
			string = 'Desculpe, mas não temos informações sobre este ano. Para o campo correspondente, temos dados sobre os anos: '
			filter_col = [i for i in df_ideb if i.startswith(col)]
			string += filter_col[0][-4:]
			for c in filter_col[1:]:
				string += ', ' + c[-4:]
			return string + '.'
		df_temp = df_temp.sort_values(col + year, ascending=False)
		df_temp = df_temp.reset_index(drop=True)
		try:
			idx = df_temp.index[df_temp['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()].tolist()[0]
		except:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'
		idx = df_temp.index[df_temp['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()].tolist()[0]
		ordem = idx+1
		ideb = df_temp[col + year][idx]
		municipio = df_temp['Nome do Município'][idx]
		return 'IDEB ' + municipio + ' em ' + year + ':\n\n' + str(ideb) + ' (' + str(ordem) + 'º de ' + str(len(df_ideb)) + ' municípios).'


	elif hasTag("►CSV IDEB IDEB◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)
		df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
		else:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == unidecode(municipio.lower())]
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'
	
		col = 'IDEB_AF_M_'
		df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
		string = 'IDEB ' + municipio + ':\n\n' 
		for col in df_temp.columns:
			string += '- Em ' + col[-4:] + ':\n\n' + str(df_temp[col].tolist()[0]) + '\n'
		return string
		# log.info(resposta)


	elif hasTag("►CSV IDEB META ANO◄", resposta):
		variables = resposta.split(' ; ')[1:]
		municipio = variables[0]
		municipio = re.sub('^d[oae] ', '', municipio)
		match_year = re.search('(20\d\d)', variables[1])
		if match_year:
			year = match_year.group(1)
		else:
			return 'Desculpe, não entendi.'
		col = 'PROJ_AF_M_'
		try:
			df_temp = df_ideb[['Nome do Município', col + year]]
		except:
			string = 'Desculpe, mas não temos informações sobre este ano. Para o campo correspondente, temos dados sobre os anos: '
			filter_col = [i for i in df_ideb if i.startswith(col)]
			string += filter_col[0][-4:]
			for c in filter_col[1:]:
				string += ', ' + c[-4:]
			return string + '.'
		df_temp = df_temp.sort_values(col + year, ascending=False)
		df_temp = df_temp.reset_index(drop=True)
		try:
			idx = df_temp.index[df_temp['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()].tolist()[0]
		except:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'
		idx = df_temp.index[df_temp['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()].tolist()[0]
		ordem = idx+1
		meta = df_temp[col + year][idx]
		municipio = df_temp['Nome do Município'][idx]
		return 'Meta projetada do IDEB ' + municipio + ' em ' + year + ':\n\n' + str(meta) + ' (' + str(ordem) + 'º de ' + str(len(df_ideb)) + ' municípios).'


	elif hasTag("►CSV IDEB META◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)	
		df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
		else:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == unidecode(municipio.lower())]
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'

		col = 'PROJ_AF_M_'
		df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
		string = 'A meta projetada do IDEB do município ' + municipio + ' é:\n\n' 
		for col in df_temp.columns:
			string += '- Em ' + col[-4:] + ': ' + str(df_temp[col].tolist()[0]) + '\n'
		return string


	elif hasTag("►CSV IDEB ATING META ANO◄", resposta):
		variables = resposta.split(' ; ')[1:]
		municipio = variables[0]
		municipio = re.sub('^d[oae] ', '', municipio)
		match_year = re.search('(20\d\d)', variables[1])
		if match_year:
			year = match_year.group(1)
		else:
			return 'Desculpe, não entendi.'
		try:
			idx = df_ideb.index[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()].tolist()[0]
		except:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'
		col = 'Atingiu_a_meta_AF_M_'
		df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == unidecode(municipio.lower())]
		municipio = df_temp['Nome do Município'].tolist()[0]
		try:
			booleano = df_temp[col + year].tolist()[0]
		except:
			string = 'Desculpe, mas não temos informações sobre este ano. Para o campo correspondente, temos dados sobre os anos: '
			filter_col = [i for i in df_ideb if i.startswith(col)]
			string += filter_col[0][-4:]
			for c in filter_col[1:]:
				string += ', ' + c[-4:]
			return string + '.'

		string = municipio + ' '
		if booleano == 'NÃO':
			string += 'não '
		string += 'cumpre a meta do IDEB no ano de ' + year + '.'
		return string


	elif hasTag("►CSV IDEB ATING META◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)
		df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
		else:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					df_temp = df_ideb[df_ideb['Nome do Município'].apply(lambda x: unidecode(x.lower())) == unidecode(municipio.lower())]
					break
			if found == False:
				return 'Desculpe, não temos informações sobre este município'
		col = 'Atingiu_a_meta_AF_M_'
		df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
		string = municipio + ' atinge a meta:\n\n' 
		for col in df_temp.columns:
			string += '- Em ' + col[-4:] + ': ' + str(df_temp[col].tolist()[0]) + '\n'
		return string


	# TAGS PARA A BASE DO ISP

	elif hasTag("►CSV ISP ANO◄", resposta):

		sendAnswer(cid, "Certo, ja vou buscar sua informação.")

		variables = resposta.split(' ; ')[1:]

		col = variables[0]

		municipio = variables[1]
		year = int(variables[2])
		
		new_df = df_isp[df_isp['vano'] == year]
		if len(new_df) == 0:
			return 'Desculpe, não temos informações para o ano correspondente.'
		new_df = new_df[new_df['fmun'].apply(lambda x: unidecode(x.lower())) == municipio.lower()]
		if len(new_df) == 0:
			found = False
			for mun in set(df_ideb['Nome do Município']):
				if 1 - lev.distance(unidecode(municipio.lower()), unidecode(mun.lower()))/len(unidecode(mun.lower())) > 0.75:
					municipio = mun
					found = True
					new_df = df_isp[df_isp['fmun'].apply(lambda x: unidecode(x.lower())) == unidecode(municipio.lower())]
					break
			if found == False:
				return 'Desculpe, não temos informações para o município correspondente.'

		if ' | ' in col:
			col1 = col.split(' | ')[0]
			col2 = col.split(' | ')[1]
			total = sum(new_df[col1]) + sum(new_df[col2])
		else:
			total = sum(new_df[col])
		municipio = new_df['fmun'].tolist()[0]
		string = municipio + ' tem uma quantidade total de ' + str(total) + ' ' + isp_column_converter[col] + ' para o ano de ' + str(year) + '.'
		return [string, "Deseja saber algo mais? #button#Homicídios;Latrocínios;Roubos;Furtos;Sequestros;Estupros;Pessoas desaparecidas;Estelionatos;Quero saber sobre a base do IDEB"]

	return resposta # caso seja uma pergunta mais genérica, em que não compete buscar em algum banco 


def sendAnswer(cid, resposta, is_voice = False):
	"""Process answers from AIML Kernel
	"""	
	try:
		resposta = resposta.replace('\\n','\n')
		
		if not resposta.replace('\n','').strip() == "":
			
			markup = None
			
			if hasTag("#button#", resposta):
				buttonList = getTagContent("#button#", resposta, ";")
				
				bt_row = len(buttonList)
				
				if bt_row > 3 :
					bt_row = 1
                    
				markup = types.ReplyKeyboardMarkup(resize_keyboard=1, row_width=bt_row, one_time_keyboard=True)

				bts = []
				for opt in buttonList:
					bts.append(types.KeyboardButton(opt))

				if bts != []:   
					markup.add(*bts)

				resposta = beforeTag("#button#", resposta)
				
				
			if markup != None:
				if not is_voice:
					bot.send_message(cid, resposta, reply_markup = markup)
				else:
					tts = gTTS(text=resposta, lang='pt')
					tts.save("tmp/answer" + str(cid) + ".ogg")

					with open("tmp/answer" + str(cid) + ".ogg", "rb") as f:
						bot.send_voice(cid, f, reply_markup = markup)

			else:
				markup = types.ReplyKeyboardRemove(selective = False)

				if not is_voice:
					bot.send_message(cid, resposta, reply_markup = markup)
				else:
					tts = gTTS(text=resposta, lang='pt')
					tts.save("tmp/answer" + str(cid) + ".ogg")

					with open("tmp/answer" + str(cid) + ".ogg", "rb") as f:
						bot.send_voice(cid, f, reply_markup = markup)
            
	except Exception as inst:
		print (type(inst))     # the exception instance
		print (inst.args)      # arguments stored in .args
		print (inst)


def listener(messages):   
	for m in messages:
		try:
			oUser = m.from_user
			oChat = m.chat
			
			cid = oChat.id
			
			uid = oUser.id		
			first_name = oUser.first_name
			last_name = oUser.last_name
			username = oUser.username

			# removing accent from text

			if m.content_type == "text":
				text = unidecode(m.text)

			answer = ""
			
			userSession = getSession(cid)
			session_id = userSession.session_id
			
			if m.content_type == 'text':
				if not reservedCommands(cid, text):
					answer = userSession.mensagem(text)
					answer = processSpecialAnswer(cid, answer)
					if type(answer) == list:
						for ans in answer:
							sendAnswer(cid, ans)
					else:
						sendAnswer(cid, answer)
			
			elif m.content_type == 'location':
				location = m.location
				answer = userSession.mensagem('location')
				answer = processSpecialAnswer(cid, answer)
				sendAnswer(cid, answer)

			elif m.content_type == "voice":
				print(m.voice)

				response = get_file(LOCAL_BOT_TOKEN, m.voice.file_id)
				print(response)

				audio = bot.download_file(response["file_path"])

				with open("tmp/audio" + str(session_id) + ".ogg", "wb") as f:
					f.write(audio)

				ogg_file = AudioSegment.from_file("tmp/audio" + str(session_id) + ".ogg", format="ogg")
				ogg_file.export("tmp/audio" + str(session_id) + ".wav", format="wav")

				r = sr.Recognizer()

				with sr.AudioFile("tmp/audio" + str(session_id) + ".wav") as source:
				    audio_source = r.record(source)

				try:
					# Uses the default API key
					# To use another API key: `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
					text = r.recognize_google(audio_source, language="pt-BR")
					print("You said: " + text)

					answer = userSession.mensagem(text)
					answer = processSpecialAnswer(cid, answer)

					if type(answer) == list:
						for ans in answer:
							sendAnswer(cid, ans, is_voice = True)
					else:
						sendAnswer(cid, answer, is_voice = True)

				except sr.UnknownValueError:
					print("Google Speech Recognition could not understand audio")
				except sr.RequestError as e:
					print("Could not request results from Google Speech Recognition service; {0}".format(e))

				# answer = "Voz recebida!"
				# sendAnswer(cid, answer)
				pass

			# logManager.logMessage(session_id, cid, uid, first_name, last_name, username, text, answer)
			
		except Exception as inst:
			print (type(inst))     # the exception instance
			print (inst.args)      # arguments stored in .args
			print (inst)

bot.set_update_listener(listener)


while True:
	try:
		bot.polling()
	except Exception as inst:
		print(type(inst))     # the exception instance
		print(inst.args)      # arguments stored in .args
		print(inst)




