from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
sessoesCollection = db['sessoes']
cursor = sessoesCollection.find({}).limit(3)

for sessao in cursor:
    print(u'{:<16}: {}'.format(sessao['_id'], sessao['autoria']))

    sessoesCollection.find_one_and_update(
        {'_id': sessao["_id"]},
        {'$set': {'autoria': sessao['autoria'].strip()}}
    )