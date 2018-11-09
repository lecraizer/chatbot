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
# import logManager
# import woofyManager

#import imp
#telebot = imp.load_source('telebot', '/home/chatbot/lib/pyTelegramBotAPI/telebot/__init__.py')

bot = telebot.TeleBot('712212286:AAHeG-tVXy-9rOWWDA9QiW7nPaz1n1r801E') # dev

aimlMgrDict = {}

# open csv ideb database 
df_ideb = pd.read_csv('tabelas/educ_ideb_rede_municipal.csv')

# open csv criminal database
df_crim = pd.read_csv('tabelas/BaseMunicipioMensal.csv', encoding = "ISO-8859-1", sep=";")

# month converter: written way to number
month_converter = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

# column converter for ISP database
# isp_column_converter = {'homicidio doloso': 'hom_doloso', 'homicidio culposo': 'hom_culposo', 'estupro': 'estupro', 'sequestro': 'sequestro'}

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


import unicodedata
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
		year = variables[1]
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
			idx = df_temp.index[df_temp['Nome do Município'].str.lower() == municipio.lower()].tolist()[0]
		except:
			return 'Desculpe, não temos informações sobre este município'

		ordem = idx+1
		ideb = df_temp[col + year][idx]
		return 'IDEB ' + municipio + ' em ' + year + ': ' + str(ideb) + ' (' + str(ordem) + 'º de ' + str(len(df_ideb)) + ' municípios).'


	elif hasTag("►CSV IDEB IDEB◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)
		df_temp = df_ideb[df_ideb['Nome do Município'].str.lower() == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
			col = 'IDEB_AF_M_'
			df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
			string = 'IDEB ' + municipio + ' :\n\n' 
			for col in df_temp.columns:
				string += '- Em ' + col[-4:] + ': ' + str(df_temp[col].tolist()[0]) + '\n'

			return string
		# log.info(resposta)
		return 'Desculpe, mas não temos informações sobre o índice desejado'


	elif hasTag("►CSV IDEB META ANO◄", resposta):
		variables = resposta.split(' ; ')[1:]
		municipio = variables[0]
		municipio = re.sub('^d[oae] ', '', municipio)
		year = variables[1]
		df_temp = df_ideb[df_ideb['Nome do Município'].str.lower() == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
			col = 'PROJ_AF_M_'
			try:
				meta = df_temp[col + year].tolist()[0]
			except:
				string = 'Desculpe, mas não temos informações sobre este ano. Para o campo correspondente, temos dados sobre os anos: '
				filter_col = [i for i in df_ideb if i.startswith(col)]
				string += filter_col[0][-4:]
				for c in filter_col[1:]:
					string += ', ' + c[-4:]
				return string + '.'
			return 'A meta projetada do IDEB do município ' + municipio + ' em ' + year + ' é de ' + str(meta) + '.'
		return 'Desculpe, mas não temos informações sobre o índice desejado'


	elif hasTag("►CSV IDEB META◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)	
		df_temp = df_ideb[df_ideb['Nome do Município'].str.lower() == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
			col = 'PROJ_AF_M_'
			df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
			string = 'A meta projetada do IDEB do município ' + municipio + ' é:\n\n' 
			for col in df_temp.columns:
				string += '- Em ' + col[-4:] + ': ' + str(df_temp[col].tolist()[0]) + '\n'
			return string
		return 'Desculpe, mas não temos informações sobre o índice desejado'


	elif hasTag("►CSV IDEB ATING META ANO◄", resposta):
		variables = resposta.split(' ; ')[1:]
		municipio = variables[0]
		municipio = re.sub('^d[oae] ', '', municipio)
		year = variables[1]
		df_temp = df_ideb[df_ideb['Nome do Município'].str.lower() == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
			col = 'Atingiu_a_meta_AF_M_'
			try:
				booleano = df_temp[col + year].tolist()[0]
				string = municipio + ' '
				if booleano == 'NÃO':
					string += 'não '
				string += 'cumpre a meta do IDEB no ano de ' + year + '.'
				return string
			except:
				string = 'Desculpe, mas não temos informações sobre este ano. Para o campo correspondente, temos dados sobre os anos: '
				filter_col = [i for i in df_ideb if i.startswith(col)]
				string += filter_col[0][-4:]
				for c in filter_col[1:]:
					string += ', ' + c[-4:]
				return string + '.'
		return 'Desculpe, mas não temos informações sobre o índice desejado'


	elif hasTag("►CSV IDEB ATING META◄", resposta):
		municipio = resposta.split(' ; ')[1]
		municipio = re.sub('^d[oae] ', '', municipio)
		df_temp = df_ideb[df_ideb['Nome do Município'].str.lower() == municipio.lower()]
		if len(df_temp) > 0:
			municipio = df_temp['Nome do Município'].tolist()[0]
			col = 'Atingiu_a_meta_AF_M_'
			df_temp = df_temp.loc[:, df_temp.columns.str.startswith(col)]
			string = '' 
			for col in df_temp.columns:
				string += '- Em ' + col[-4:] + ': ' + str(df_temp[col].tolist()[0]) + '\n'

			return string
		return 'Desculpe, mas não temos informações sobre o índice desejado'


	# TAGS PARA A BASE DO ISP

	elif hasTag("►CSV ISP ANO◄", resposta):

		print(resposta.split(' ; ')[1:])


		# variables = resposta.split(' ; ')[1:]
		# column = variables[0]
		# if column in isp_column_converter.keys():
		# 	col = isp_column_converter 
		# municipio = variables[1]
		# municipio = re.sub('^d[oae] ', '', municipio)
		# year = variables[2]




	return resposta # caso seja uma pergunta mais genérica, em que não compete buscar em algum banco 






def sendAnswer(cid, resposta):
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
				bot.send_message(cid, resposta, reply_markup = markup)
			else:
				markup = types.ReplyKeyboardRemove(selective = False)
				bot.send_message(cid, resposta, reply_markup = markup)
            
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

			tokens = m.text.split()
			normalized_tokens = []
			for token in tokens:
				if token.islower():
					normalized_tokens.append(unidecode(token))
				else:
					normalized_tokens.append(token)
			text = ' '.join(normalized_tokens)

			answer = ""
			
			userSession = getSession(cid)
			session_id = userSession.session_id
			
			if m.content_type == 'text':
				if not reservedCommands(cid, text):
					answer = userSession.mensagem(text)
					answer = processSpecialAnswer(cid, answer)
					sendAnswer(cid, answer)
			
			elif m.content_type == 'location':
				location = m.location
				answer = userSession.mensagem('location')
				answer = processSpecialAnswer(cid, answer)
				sendAnswer(cid, answer)

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



