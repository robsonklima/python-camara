# -*- coding: utf-8 -*-
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
        client = language.LanguageServiceClient()
        document = types.Document(content=sessao['ementa'], type=enums.Document.Type.PLAIN_TEXT)
        entities = client.analyze_entities(document).entities
        entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION', 'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

        entidades = []

        for entity in entities:
            entidades.append({
                'nome': entity.name,
                'tipo': entity_type[entity.type],
                'metadado': entity.metadata,
                'saliencia': entity.salience,
                'wikipedia_url': entity.metadata.get('wikipedia_url', '-')
            })

        print(entidades)

        sessoesCollection.find_one_and_update(
            {'_id': sessao["_id"]},
            {'$set': {'entidades': entidades}}
        )
    except:
        print(u'Something failed!')