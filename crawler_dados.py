import pandas as pd
import time
import os
import sys
from selenium import webdriver
 

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", os.getcwd() + '/tabelas')
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

driver = webdriver.Firefox(firefox_profile=profile)

if sys.argv[1] == 'isp':
    driver.get('http://www.ispdados.rj.gov.br/estatistica.html')
    time.sleep(3)
    driver.get('http://www.ispdados.rj.gov.br/Arquivos/BaseMunicipioMensal.csv')

elif sys.argv[1] == 'ideb':
    driver.get("http://apps.mprj.mp.br/sistema/inloco/")
    time.sleep(7)

    driver.find_element_by_xpath('/html/body/div[1]/div/div[10]/section/h1/span').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/a').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/ul/div[5]/li').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/ul/div[5]/ul/div[1]').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/ul/div[5]/ul/div[1]/ul/div[2]').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[8]/div[2]').click()
    driver.find_element_by_xpath('/html/body/div[1]/div/div[8]/div[2]/div/ul/li[3]/a').click()
    
    # tratamento da base - remoção da última coluna ('geom')
    time.sleep(7)
    df = pd.read_csv('tabelas/educ_ideb_rede_municipal.csv')
    print( df.columns)
    del df['geom']
    df.to_csv('tabelas/educ_ideb_rede_municipal.csv',index=False)

# aguardando o carregamento da pagina
time.sleep(7)
driver.close()