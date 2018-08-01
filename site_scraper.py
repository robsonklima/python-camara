from urllib2 import urlopen
from urllib2 import HTTPError
from urllib2 import URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
db.sessoes.delete_many({})

for i in range(6788, 15000):
    try:
        html = urlopen("https://votacoes.camarapoa.rs.gov.br/votacoes/" + str(i))
    except HTTPError as e:
        print(e)
    except URLError:
        print("URI not found")
    else:
        soup = BeautifulSoup(html, "lxml")
        tags = soup.findAll("dd")

        sessao = {
            "sessao": tags[0].getText(),
            "proposicao": tags[1].getText(),
            "ementa": tags[2].getText(),
            "autoria": tags[3].getText(),
            "sim": tags[4].getText(),
            "nao": tags[5].getText(),
            "abstencoes": tags[6].getText(),
            "resultado": tags[7].getText(),
            "horarioInicio": tags[8].getText(),
            "horarioTermino": tags[9].getText()
        }

        db.sessoes.insert_one(sessao).inserted_id