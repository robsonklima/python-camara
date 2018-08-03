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

for sessao in cursor:
    print(u'{:<16}: {}'.format(sessao['_id'], sessao['ementa']))

    try:
        translator = Translator()
        translated = translator.translate(sessao['ementa'], dest='en')
    except:
        print(u"Something failed")

    client = language.LanguageServiceClient()
    document = types.Document(content=translated.text.encode('utf-8'), type=enums.Document.Type.PLAIN_TEXT)

    try:
        categories = client.classify_text(document).categories

        for category in categories:
            print(u'=' * 40)
            print(u'{:<16}: {}'.format('name', category.name))
            print(u'{:<16}: {}'.format('confidence', category.confidence))

            sessoesCollection.find_one_and_update(
                {'_id': sessao["_id"]},
                {'$set': {'categoria': {'nome': category.name, 'confianca': category.confidence}}}
            )
    except:
        print("Nothing found!")

    print(u'=' * 40)