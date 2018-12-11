# -*- coding: utf-8 -*-
import aiml
import time
import random

class aimlManager():
    
    # Create the kernel and learn AIML files
    
	def __init__(self):
		self.session_id = random.randint(0,10000)
		self.kernel = aiml.Kernel()
		self.timestamp = time.time()
		self.kernel.learn("saudacoes.aiml")
		self.kernel.learn("informacoes_gerais.aiml")
		self.kernel.learn("base_ideb.aiml")
		self.kernel.learn("base_isp.aiml")
		self.kernel.learn("outras_regras.aiml")
				
		#self.kernel.respond("load aiml humanizacao")
		#self.kernel.respond("load aiml processos")
		#self.kernel.respond("load aiml onibus")
		#kernel.respond("load aiml processos")

	def brainLearn(self, pattern, template):
	   
		from xml.sax.saxutils import escape

		textAiml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
		textAiml += "<aiml version=\"1.0.1\">"
		textAiml += "<category>"
		textAiml += "<pattern>" + escape(pattern.upper()) + "</pattern>"
		textAiml += "<template>" + escape(template) + "</template>"
		textAiml += "</category>"
		textAiml += "</aiml>"

		self.kernel.learnString(textAiml)		

	def deleteBrain(self):
		self.kernel.resetBrain()
		
	def resetBrain(self):
		self.kernel.resetBrain()
		self.kernel.learn("rules.aiml")
		self.kernel.respond("load aiml humanizacao")
		self.kernel.respond("load aiml processos")
		self.kernel.respond("load aiml onibus")
    
	def saveBrain(self):
		self.kernel.saveBrain("brain.aiml")

	def dumpBrain(self):
		self.kernel._brain.dump()

	def mensagem(self, text):
		return self.kernel.respond(text)