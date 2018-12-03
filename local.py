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
# import imp
from tags import match_tag

LOCAL_BOT_TOKEN = '796929920:AAGiRRwj-_fXv245dDFXX87lh5V4Aw1ItU8'
bot = telebot.TeleBot(LOCAL_BOT_TOKEN) # local (para teste e manutenção)

aimlMgrDict = {}

# month converter: written way to number
# month_converter = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}


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
    
    else:
        return match_tag(resposta)


def sendAnswer(cid, resposta, is_voice = False):
    """Process answers from AIML Kernel
    """ 
    try:
        resposta = resposta.replace('\\n','\n')
        log.info( '%s: %s' % ('R', resposta) )
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

                    bot.send_message(cid, resposta)

            else:
                markup = types.ReplyKeyboardRemove(selective = False)

                if not is_voice:
                    bot.send_message(cid, resposta, reply_markup = markup)
                else:
                    tts = gTTS(text=resposta, lang='pt')
                    tts.save("tmp/answer" + str(cid) + ".ogg")
                    print("depois do save")
                    with open("tmp/answer" + str(cid) + ".ogg", "rb") as f:
                        print("dentro do with")
                        bot.send_voice(cid, f, reply_markup = markup)

                    bot.send_message(cid, resposta)

            
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
                log.info( '%s: %s' % ('P', m.text) )
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
                response = get_file(LOCAL_BOT_TOKEN, m.voice.file_id)

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
                    log.info( '%s: %s' % ('PV', text) )
                    bot.send_message(cid, "Você disse: " + text)

                    answer = userSession.mensagem(text)

                    answer = processSpecialAnswer(cid, answer)

                    if type(answer) == list:
                        for ans in answer:
                            sendAnswer(cid, ans, is_voice = True)
                            log.info( '%s: %s' % ('RV', ans) )
                    else:
                        sendAnswer(cid, answer, is_voice = True)
                        log.info( '%s: %s' % ('RV', answer) )

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

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