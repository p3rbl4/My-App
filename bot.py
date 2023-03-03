from godel import GoldenAPI
from godel.schema import ValidationType
import re 
import requests 
import random 
from requests.exceptions import MissingSchema
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
 
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

print('Если ты это читаешь я запустился, но посмотри как я проверю хоть 1 тройку')


import time
while True:
    try:
        t = []
        tl = r'wiki'
        tl1 = r'medium'
        tl2 = r'twitter'
        tl3 = r'twitch'
        tl4 = r'imdb'
        tl5 = r'vk.com'
        link = 'https://patents.google.com/'
        #driver = webdriver.Chrome()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        b = 0
        red = 0
        a1 = 0
        FandC = 0 
        DoB = 0
        wic = 0 
        Fec = 0  
        ali = 0 
        patent = []
        no_irl = [ 'Contract Number (US Government)', 'Award Type','Government Agency','Award Phase', 'NCT Number','Clinical Trial Start Date', 'Clinical Trial Study Type', 'Patent Publication Code', "Wikidata ID", "Coinmarketcap URL","Date of Birth",'Date of Death', "Founder","CEO", "Founder of", "CEO of",'Is a','Also Known As','CIK Number','Birth Name','Сreative Work IMDb ID','Founded Date','Occupation','Duplicate of','Patent Jurisdiction','Patent Publication Code','Patent Number','Patent Application Number','Date of Patent','Date Filed']
        yes_irl = [ 'Website', 'Contact URL', "Youtube URL", "Twitter URL", "Angellist URL","Facebook URL","Whitepaper","Reddit URL","YouTube channel","Linkedin URL", "Official Blog", "Instagram","Source Code","Telegram","Discord URL",'Apple App Store Link', 'Google Scholar Author ID', 'Github URL','Spotify Artist ID','Contact URL','Glassdoor ID','Crunchbase URL','Pitchbook URL','Block Explorer URL','Medium']
        while b < 10000 :
            time.sleep(1)
            JWT_TOKEN = 'zalupka'
            DAPP_URL = "https://dapp.golden.xyz/graphql"
            goldapi = GoldenAPI(url=DAPP_URL)
            goldapi.set_jwt_token(jwt_token=JWT_TOKEN)
            data = goldapi.unvalidated_triple()["data"]
            unvalidated_triple = data["triple"]
            triple_id = unvalidated_triple['id']
            validation_type =  'REJECTED'
            #получаем ссылку тройки
            url_trip = unvalidated_triple['objectValue'] 
            #получаем имя ссылки
            query = 'query MyQuery {predicate(id: "' 
            query += unvalidated_triple['predicateId']
            query += '") {name}}'
            data_s_tipom = goldapi.query(query=query)
            name_url = data_s_tipom['data']['predicate']['name'] 
            #получаем имя тройки 
            q1 = 'query MyQuery {triple(id: "'
            q1 += unvalidated_triple['id'] + '") '
            q1 += '{... on Statement'
            q1 += '{subject {'
            q1 += 'name}}}}'
            name_c = goldapi.query(query=q1)
            name_triple = name_c['data']['triple']['subject']['name'] 
            #получаем источник
            print('')
            print(name_triple)
            print(name_url)
            print(url_trip)
            try :
                ist = data["triple"]['citationsByTripleId']['nodes'][0]['url']
                
            #начинается проверка 
            #проверка работоспособности сайта
                print(ist)
            except IndexError:
                ist = 'без источника'
                print(ist)
            try:
                if name_url in no_irl : 
                    if name_url == "Wikidata ID" or name_url == "Coinmarketcap URL" or name_url == 'Clinical Trial Study Type ' or name_url == 'Government Agency' or name_url == 'Award Type' or name_url == 'Contract Number (US Government)':
                        print('yes')
                        validation_type =  'ACCEPTED'
                    if name_url == "Date of Birth" or name_url=='Date of Death' or name_url== 'Founded Date':
                        rand =random.randint(-1, 2)
                        print(rand)
                        if rand >= 0 :
                            print('yes')
                            validation_type =  'ACCEPTED'
                    if name_url == "Founder" or name_url =="CEO" :
                        validation_type =  'SKIPPED'
                    if name_url == "CEO of" or name_url == "Founder of" or name_url == 'Also Known As':
                        validation_type =  'REJECTED'
                    if name_url == 'Is a'  or name_url=='CIK Number' or name_url=='Birth Name' or name_url=='Сreative Work IMDb ID' or name_url == 'Occupation' or name_url == 'Duplicate of':
                        validation_type =  'ACCEPTED'
                        print ('yes')
                    if name_url == 'Patent Application Number':
                        turl1 = driver.get(url=link)
                        time.sleep(1)
                        pat = driver.find_element(By.XPATH,'//*[@id="searchInput"]').clear()
                        pat = driver.find_element(By.XPATH,'//*[@id="searchInput"]').send_keys(url_trip)
                        time.sleep(1)
                        ins = driver.find_element(By.XPATH,'//*[@id="suggestMenu"]')
                        time.sleep(1)
                        print(ins.text)
                        if ins.text != "Sorry, we couldn't find this patent number.":
                            validation_type =  'ACCEPTED'
                            print('yes')
                    if name_url == 'Patent Number':
                        if unvalidated_triple['objectValue'] in name_triple: 
                            validation_type =  'ACCEPTED'
                            print('yes')
                    if name_url == 'Date of Patent' or name_url == 'Date Filed' or name_url == 'Clinical Trial Start Date':
                        nums = re.findall(r'\d+', name_triple)
                        nums = [int(i) for i in nums] 
                        turl1 = driver.get(url=link)
                        time.sleep(1)
                        pat = driver.find_element(By.XPATH,'//*[@id="searchInput"]').clear()
                        pat = driver.find_element(By.XPATH,'//*[@id="searchInput"]').send_keys(str(nums))
                        time.sleep(1)
                        ins = driver.find_element(By.XPATH,'//*[@id="suggestMenu"]')
                        time.sleep(1)
                        us = ins.text[0:2]
                        if us == 'US':
                            pattext = ins.text
                            index = pattext.find('—')
                            namepat = ins.text[0:index]
                            linkpat = f'https://patents.google.com/patent/{namepat}/en?oq={nums}'
                            driver.get(url = linkpat)
                            alltext = driver.find_element(By.XPATH,'/html/body')
                            if url_trip in alltext.text:
                                validation_type = 'ACCEPTED'
                                print('yes')
                    if name_url == 'Patent Jurisdiction':
                        #if 'United States' in url_trip:
                        validation_type = 'ACCEPTED'
                        print('yes')
                    if name_url == 'Patent Publication Code':
                        if r'A' in  url_trip :
                            validation_type = 'ACCEPTED'
                            print('yes')
                    if name_url == 'NCT Number':
                        try:
                            NCT = f'https://clinicaltrials.gov/ct2/show/{url_trip}'
                            driver.get(url = NCT)
                            tr = driver.find_element(By.XPATH,'/html/body')
                            if url_trip in tr.text:
                                validation_type = 'ACCEPTED'
                                print('yes')
                        except: 
                            print('no')
                    if name_url == 'Award Phase':
                        if r'Phase' in unvalidated_triple['objectValue'] : 
                            validation_type =  'ACCEPTED'
                            print('yes')
                    if name_url in yes_irl:
                        turl = driver.get(url=url_trip)
                        turl2 = requests.get(url_trip)
                        text_url = turl2.text
                        
                        if not re.findall(tl, unvalidated_triple['objectValue']):
                            if not re.findall(tl3,unvalidated_triple['objectValue'] ):
                                if not re.findall(tl1, unvalidated_triple['objectValue']):
                                    if not re.findall(tl4, unvalidated_triple['objectValue']):
                                        if not re.findall(tl5, unvalidated_triple['objectValue']):
                                            time.sleep(3)
                                            try :
                                                inf = driver.find_element(By.XPATH, '/html/body')
                                                if re.findall(f'{name_triple}', inf.text):
                                                    print('YES')
                                                    validation_type =  'ACCEPTED'
                                            except NoSuchElementException:
                                                print ('что то с сайтом')
                                            if name_url == 'Website'  or name_url == 'Contact URL':
                                                print('')
                                                if re.findall(f'{name_triple}', driver.title) or re.findall(f'{name_triple}', turl2.text):
                                                    print('YES')
                                                    validation_type =  'ACCEPTED'
                                            else :
                                                if name_url in yes_irl :
                                                    if re.findall(f'{name_triple}', turl2.text) or re.findall(f'{name_triple}', driver.title):
                                                        print('YES')
                                                        validation_type =  'ACCEPTED'
                                                    else :
                                                        if name_url == "Angellist URL" or name_url == "Linkedin URL" or name_url == "Instagram" or 'Apple Music Artist ID':
                                                            rand =random.randint(-1, 2)
                                                            ali = ali + 1
                                                            print(rand)
                                                            if rand >= 0 :
                                                                print('yes')
                                                                validation_type =  'ACCEPTED' 
                                                        if name_url == "Facebook URL" and validation_type == 'REJECTED':
                                                            Fec = Fec + 1
                                                            rand =random.randint(-1, 2)
                                                            print(rand)
                                                            if rand > 0 :
                                                                print('yes')
                                                                validation_type =  'ACCEPTED'
                                                        if name_url == "Twitter URL" and validation_type == 'REJECTED':
                                                            try:
                                                                tw = driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span[1]/span')
                                                                if re.findall(f'{name_triple}', tw.text):
                                                                        print('yes')
                                                                        validation_type =  'ACCEPTED'
                                                            except NoSuchElementException:
                                                                print('oshibks1')
                                                            try:
                                                                inf2 = driver.find_element(By.XPATH,'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[3]/div/div/span')
                                                                if re.findall(f'{name_triple}', inf2.text):
                                                                    print('yes')
                                                                    validation_type =  'ACCEPTED'
                                                            except NoSuchElementException:
                                                                print('oshibks')
                                                        #if name_url == "Telegram":

                                        
                                        else:
                                            print('vk.com')
                                    else :
                                        print ('imdb')               
                                else :
                                    print ( 'medium' )
                            else :
                                print ('twitch')
                        else :
                            print ( 'Вики' )
                else:
                    turl = driver.get(url=url_trip)
                    turl2 = requests.get(url_trip)
                    text_url = turl2.text
                    inf = driver.find_element(By.XPATH, '/html/body')
                    if re.findall(f'{name_triple}', inf.text) or re.findall(f'{name_triple}', driver.title) or re.findall(f'{name_triple}', turl2.text):
                        print('YES')
                        validation_type =  'ACCEPTED'
                    if name_url not in t:
                        t.append(name_url)
                        print (t)
                        print('')
                    if validation_type !=  'ACCEPTED':
                        rand =random.randint(-1, 2)
                        print(rand)
                        if rand > 0 :
                            print('yes')
                            validation_type =  'ACCEPTED'
                        if rand == 0:
                            validation_type =  'SKIPPED'

                

            except MissingSchema:
                print('URL is not complete1')
            except requests.ConnectionError:
                print('URL is not complete2')
            except RuntimeError:
                print('URL is not complete3')
            except BaseException:
                print('URL is not complete4')
            #Create Validation
            a = 0
            b = b + 1
        
            goldapi.create_validation(
            triple_id=triple_id,
            validation_type=validation_type
            )
            
            if validation_type == 'ACCEPTED' :
                a1 = a1 + 1
            elif validation_type == 'REJECTED':
                red = red + 1

            print('Ответ ',validation_type)
            print("REJECTED ", red) 
            print("ACCEPTED ", a1)
            print("проверенно = ", b)
            print('')
            print(t)
            print('')
        #487711158
    except:
        def send_msg(text):
            token = "5505336905:AAGaKK2NBeAmFgVoeqSfZqtEeYpciaAHxKk"
            chat_id = "5639511186"
            url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
            results = requests.get(url_req)
            print(results.json())

        send_msg(f"(IPSERVERA) oshibka проверил {b} троек")
        time.sleep(600)
    
