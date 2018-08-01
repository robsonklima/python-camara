import os
import wget
from pathlib import Path

BASE_PATH = os.path.dirname(os.path.abspath( __file__ ))
FILES_FOLDER = "/data"
BASE_URL = 'https://votacoes.camarapoa.rs.gov.br/votacoes/por_votacao.csv?votacao_id='

print('Beginning file download...')

for i in range(6788, 15000):
    try:
        filename = wget.download(BASE_URL + str(i), BASE_PATH + FILES_FOLDER)
        print(filename)
    except:
        print("Something went wrong!")

print('File download finished...')