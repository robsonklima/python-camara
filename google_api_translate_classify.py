# -*- coding: utf-8 -*-
from googletrans import Translator
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
sessoesCollection = db['sessoes']
cursor = sessoesCollection.find({})

for i, sessao in enumerate(cursor):
    print(u'{} - {:<16}: {}'.format(str(i), sessao['_id'], sessao['ementa']))

    try:
        translator = Translator()
        translated = translator.translate(sessao['ementa'], dest='en')
    except:
        print(u"Something failed")

    client = language.LanguageServiceClient()
    document = types.Document(content=translated.text.encode('utf-8'), type=enums.Document.Type.PLAIN_TEXT)

    try:
        categories = []
        data = client.classify_text(document).categories
        for category in data:
            categories.append({
                'nome': category.name,
                'confianca': category.confidence
            })

        sessoesCollection.find_one_and_update(
            {'_id': sessao["_id"]},
            {
                '$set': {'categorias': categories},
                '$unset': {'categoria': 1}
            }
        )
    except:
        print(u"Nothing found!")