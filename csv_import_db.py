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
    if (file != ".DS_Store"):
        with open(BASE_PATH + "/data/" + file, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', fieldnames=("A","B","C"))

            sessao = {}

            for i, row in enumerate(reader):
                if (i == 0):
                    sessao = row["C"]
                else:
                    voto = { "vereador": row["A"], 'partido': row["B"], 'voto': row["C"], 'sessao': sessao }
                    db.votos.insert_one(voto).inserted_id

