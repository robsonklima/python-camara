from urllib2 import urlopen
from urllib2 import HTTPError
from urllib2 import URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.camara
db.projetos.delete_many({})

BASE_URI = u"http://camarapoa.rs.gov.br/processos/"

for i in range(1, 200000):
    try:
        html = urlopen(BASE_URI + str(i))
    except HTTPError as e:
        print(e)
    except URLError:
        print("URI not found")
    else:
        soup = BeautifulSoup(html, "lxml")
        dds = soup.findAll("dd")
        projeto = {}

        projeto['processo'] = dds[0].getText().strip()
        projeto['dataAbertura'] = dds[1].getText().strip()
        projeto['autoria'] = dds[2].getText().strip()
        projeto['situacao'] = dds[3].getText().strip()
        projeto['situacaoPlenaria'] = dds[4].getText().strip()
        projeto['localizacaoAtual'] = dds[5].getText().strip()
        projeto['ultimaTramitacao'] = dds[6].getText().strip()

        id = db.projetos.insert_one(projeto).inserted_id
        print(id)
