from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
sessoesDB = db['sessoes']
votosDB = db['votos']

for sessao in sessoesDB.find({}):
    try:
        projeto = sessao['proposicao'].split('-')[0].strip()
        proc = sessao['proposicao'].split('-')[1].replace('PROC.', '').strip()
        print(projeto, proc)

        votosDB = db['votos']

        votos = votosDB.aggregate([
            {
                "$match": {
                    "sessao.projeto": projeto,
                    "sessao.proc": proc
                }
            },
            {
                "$unwind": '$voto',
                "$unwind": '$vereador'
            },
            {
                "$project":
                    {
                        "_id": 0,
                        "voto": "$voto",
                        "vereador": "$vereador",
                        "partido": "$partido"
                    }
            }
        ])

        vts = []
        for voto in votos:
            vts.append(voto)

        sessoesDB.find_one_and_update(
            {'_id': sessao["_id"]},
            {'$set': {'votos': vts}}
        )

    except Exception as error:
        print("Error: %s" % str(error))