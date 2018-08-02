#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
from pymongo import MongoClient

BASE_PATH = os.path.dirname(os.path.abspath( __file__ ))
files = os.listdir(BASE_PATH + "/data/")

client = MongoClient('localhost', 27017)
db = client.camara
db.votos.delete_many({})

for file in files:
    if (file == ".DS_Store"):
        continue

    with open(BASE_PATH + "/data/" + file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', fieldnames=("A","B","C"))

        sessao = {}

        for i, row in enumerate(reader):
            if (i == 0):
                dados = row["C"].split('-')

                for dado in dados:
                    if 'Projeto: ' in dado:
                        sessao['projeto'] = dado.replace('Projeto:', '').strip()

                    if 'PROC. ' in dado:
                        sessao['proc'] = dado.replace('PROC.', '').strip()

                    if 'EMENDA' in dado:
                        sessao['emenda'] = dado.replace('EMENDA', '').strip()

                    if 'Autoria:' in dado:
                        sessao['autoria'] = dado.replace('Autoria:', '').strip()

                    if 'Resultado:' in dado:
                        sessao['resultado'] = dado.replace('Resultado:', '').strip()

                    if 'Data de votação:' in dado:
                        sessao['dataVotacao'] = dado.replace('Data de votação:', '').strip()

                    if 'Horário de início:' in dado:
                        sessao['horarioInicio'] = dado.replace('Horário de início:', '').strip()

                    if 'Horário de término:' in dado:
                        sessao['horarioTermino'] = dado.replace('Horário de término:', '').strip()

                    if 'Link para projeto:' in dado:
                        sessao['linkProjeto'] = dado.replace('Link para projeto:', '').strip()

            else:
                voto = { "vereador": row["A"], 'partido': row["B"], 'voto': row["C"], 'sessao': sessao }
                id = id = db.votos.insert_one(voto).inserted_id
                print(id)


