from urllib2 import urlopen
from urllib2 import HTTPError
from urllib2 import URLError
from bs4 import BeautifulSoup
from googletrans import Translator
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

from pymongo import MongoClient

BASE_URI = 'https://votacoes.camarapoa.rs.gov.br'
client = MongoClient('localhost', 27017)
db = client.camara
db.sessoes.delete_many({})

for i in range(6797, 15000):
    try:
        html = urlopen(BASE_URI + "/votacoes/" + str(i))
    except HTTPError as e:
        print(e)
    except URLError:
        print("URI not found")
    else:
        print(u"{}: Processando: {}".format(str(i), BASE_URI + "/votacoes/" + str(i)))
        soup = BeautifulSoup(html, "lxml")
        tags_pag = soup.findAll("dd")
        table = soup.findAll("table", { "id": "votos" })
        tds = table[0].findAll("td")
        links_pag = soup.findAll("a")

        # Sessao
        sessao = {
            "sessao": tags_pag[0].getText(),
            "proposicao": tags_pag[1].getText(),
            "ementa": tags_pag[2].getText(),
            "autoria": tags_pag[3].getText(),
            "sim": tags_pag[4].getText(),
            "nao": tags_pag[5].getText(),
            "abstencoes": tags_pag[6].getText(),
            "resultado": tags_pag[7].getText(),
            "horarioInicio": tags_pag[8].getText(),
            "horarioTermino": tags_pag[9].getText(),
            "votos": [],
            "comparecimento": [],
            "categorias": [],
            "entidades": []
        }

        # Votos
        votos = []
        for i, td in enumerate(tds):
            if i % 3 == 0:
                voto = {
                    'vereador': tds[i+0].getText(),
                    'partido': tds[i+1].getText(),
                    'voto': tds[i+2].getText()
                }

                votos.append(voto)
        sessao['votos'] = votos

        # Comparecimento
        links = []
        for link in links_pag:
            if 'assiduidades' in link.get('href'):
                if BASE_URI + link.get('href') not in links:
                    try:
                        html = urlopen(BASE_URI + link.get('href'))
                    except HTTPError as e:
                        print(e)
                    except URLError:
                        print("URI not found")
                    else:
                        soup = BeautifulSoup(html, "lxml")
                        tables = soup.findAll("table", {"class": "votacao"})[-1]
                        tds = tables.findAll("td")

                        vereadores = []
                        for i, td in enumerate(tds):
                            if i % 3 == 0:
                                vereador = {
                                    'vereador': tds[i + 0].getText(),
                                    'partido': tds[i + 1].getText(),
                                    'presenca': tds[i + 2].getText()
                                }
                                vereadores.append(vereador)
                        sessao['comparecimento'] = vereadores


        # Google Classificacao
        try:
            translator = Translator()
            translated = translator.translate(sessao['ementa'], dest='en')
            client = language.LanguageServiceClient()
            document = types.Document(content=translated.text.encode('utf-8'), type=enums.Document.Type.PLAIN_TEXT)

            categorias = []
            data = client.classify_text(document).categories
            for category in data:
                categorias.append({'nome': category.name, 'confianca': category.confidence})
            sessao['categorias'] = categorias
        except Exception as ex:
            print(u"Error: {}".format(ex))

        # Google Entidades
        try:
            client = language.LanguageServiceClient()
            document = types.Document(content=sessao['ementa'], type=enums.Document.Type.PLAIN_TEXT)
            entities = client.analyze_entities(document).entities
            entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION', 'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

            entidades = []
            for entity in entities:
                if (u'UNKNOWN' not in entity_type[entity.type] and u'OTHER' not in entity_type[entity.type]):
                    entidades.append({
                        'nome': entity.name,
                        'tipo': entity_type[entity.type],
                        'metadado': entity.metadata,
                        'saliencia': entity.salience,
                        'wikipedia_url': entity.metadata.get('wikipedia_url', '-')
                    })

            sessao['entidades'] = entidades
        except Exception as ex:
            print(u"Error: {}".format(ex))

        try:
            db.sessoes.insert_one(sessao).inserted_id#
        except Exception as ex:
            print(u"{} - Error: {}".format(i, ex))