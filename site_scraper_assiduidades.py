#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import urlopen
from urllib2 import HTTPError
from urllib2 import URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
db.assiduidades.delete_many({})

BASE_URI = 'https://votacoes.camarapoa.rs.gov.br/'
links = []
sessao = ""

for i in range(6788, 7050):
    try:
        html = urlopen(BASE_URI + "/votacoes/" + str(i))
    except HTTPError as e:
        print(e)
    except URLError:
        print("URI not found")
    else:
        soup = BeautifulSoup(html, "lxml")
        links_pag = soup.findAll("a")
        sessao_pag = soup.findAll("dd")
        sessao = sessao_pag[0].getText()

        for link in links_pag:
            if 'assiduidades' in link.get('href'):
                if BASE_URI + link.get('href') not in links:
                    links.append(BASE_URI + link.get('href'))
                    print(BASE_URI + link.get('href'))

for link in links:
    try:
        html = urlopen(link)
        print(link)
    except HTTPError as e:
        print(e)
    except URLError:
        print("URI not found")
    else:
        soup = BeautifulSoup(html, "lxml")
        tables = soup.findAll("table", { "class": "votacao" })[-1]
        tds = tables.findAll("td")
        vereadores = []

        for i, td in enumerate(tds):
            if i % 3 == 0:
                vereador = {
                    'nome': tds[i+0].getText(),
                    'partido': tds[i+1].getText(),
                    'presenca': tds[i+2].getText()
                }

                vereadores.append({ 'vereador': vereador })

        assiduidade = { 'sessao': sessao, 'vereadores': vereadores }
        id = id = db.assiduidades.insert_one(assiduidade).inserted_id
        print(id)

