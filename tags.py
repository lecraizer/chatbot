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


# open csv ideb database 
df_ideb = pd.read_csv('tabelas/educ_ideb_rede_municipal.csv')

# open csv criminal database
df_isp = pd.read_csv('tabelas/BaseMunicipioMensal.csv', encoding = "ISO-8859-1", sep=";")


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


def hasTag(tag, frase):
	if tag in frase :
		return True
	return False


def match_tag(resposta):

    if hasTag("►CSV IDEB IDEB ANO◄", resposta):
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


    if hasTag("►CSV IDEB MAIOR IDEB ANO◄", resposta):
        variables = resposta.split(' ; ')[1:]
        match_year = re.search('(20\d\d)', variables[0])
        if match_year:
            year = match_year.group(1)
        else:
            return 'Desculpe, não entendi.'
        col = 'IDEB_AF_M_' + year

        df_temp = df_ideb[df_ideb[col] == max(df_ideb[col])]
        return 'O município de maior IDEB no ano de ' + year + ' é ' + df_temp['Nome do Município'].iloc[0] + '.'


    if hasTag("►CSV IDEB MENOR IDEB ANO◄", resposta):
        variables = resposta.split(' ; ')[1:]
        match_year = re.search('(20\d\d)', variables[0])
        if match_year:
            year = match_year.group(1)
        else:
            return 'Desculpe, não entendi.'
        col = 'IDEB_AF_M_' + year

        df_temp = df_ideb[df_ideb[col] == min(df_ideb[col])]
        return 'O município de menor IDEB no ano de ' + year + ' é ' + df_temp['Nome do Município'].iloc[0] + '.'


    if hasTag("►CSV IDEB MAIOR META IDEB ANO◄", resposta):
        variables = resposta.split(' ; ')[1:]
        match_year = re.search('(20\d\d)', variables[0])
        if match_year:
            year = match_year.group(1)
        else:
            return 'Desculpe, não entendi.'
        col = 'PROJ_AF_M_' + year

        df_temp = df_ideb[df_ideb[col] == max(df_ideb[col])]
        return 'O município de maior meta do IDEB no ano de ' + year + ' é ' + df_temp['Nome do Município'].iloc[0] + '.'


    if hasTag("►CSV IDEB MENOR META IDEB ANO◄", resposta):
        variables = resposta.split(' ; ')[1:]
        match_year = re.search('(20\d\d)', variables[0])
        if match_year:
            year = match_year.group(1)
        else:
            return 'Desculpe, não entendi.'
        col = 'PROJ_AF_M_' + year

        df_temp = df_ideb[df_ideb[col] == max(df_ideb[col])]
        return 'O município de menor meta do IDEB no ano de ' + year + ' é ' + df_temp['Nome do Município'].iloc[0] + '.'


    if hasTag("►CSV IDEB QUANTOS META IDEB ANO◄", resposta):
        variables = resposta.split(' ; ')[1:]
        match_year = re.search('(20\d\d)', variables[0])
        if match_year:
            year = match_year.group(1)
        else:
            return 'Desculpe, não entendi.'
        col = 'Atingiu_a_meta_AF_M_' + year

        df_temp = df_ideb[df_ideb[col] == 'SIM']
        
        return 'Um total de ' + str(len(df_temp)) + ' municípios atingiu a meta do IDEB em ' + year + '.'


    # TAGS PARA A BASE DO ISP
    elif hasTag("►CSV ISP ANO◄", resposta):

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
        return [string, "Deseja saber sobre outro ano, município ou tipo de crime? #button#Ano;Município;Quero saber sobre outro tipo de crime;"]
	
    return resposta # caso seja uma pergunta mais genérica, em que não compete buscar em algum banco 
