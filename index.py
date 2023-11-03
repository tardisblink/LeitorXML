################### EXTRATOR DE DADOS XML EM PYTHON, VERSÃO DO PYTHON 3.12.0 ###################

# IMPORTAÇÃO DAS BIBLIOTECAS ###################################################################
import os
from lxml import etree
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
from bs4 import BeautifulSoup

# DEFINIÇÃO DAS VARIÁVEIS ######################################################################
data_atual = datetime.now().strftime("%d-%m-%y")

pasta_base = os.getcwd()
pasta_destino = pasta_base+'\\XML_Destino'
pasta_origem = pasta_base+'\\XML_Origem'
pasta_saida = pasta_base+'\\Resultado'

nome_arquivo_csv = os.path.join(pasta_saida , f'resultado_{data_atual}.csv')
log_file = os.path.join(pasta_saida , f'LOG_{data_atual}.txt')
log_debug_file = os.path.join(pasta_saida , f'DEBUG_{data_atual}.txt')
debug_mode = True

# Informar um dicionário com o nome da tag, seguido do atributo, exemplo:
# <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
# TAG: nfeProc ATRIBUTO: xmlns ou versao

tags_xml = { 
    "det": "nItem",
}

# Informar um array com o nome das tags que estarão dentro da tag principal:

tags_desejadas = [
    "ncm", 
    "cean",
    'xprod',
    "picms",
    "picmsst",
    "pmvast"
    ]

# DEFINIÇÃO DAS FUNÇÕES ÚTEIS ###################################################################
def extrator_log(mensagem):
    print('     ' + mensagem)
    with open(log_file, 'a') as log:
        hora_atual = datetime.now().strftime("%H:%M:%S")
        log.write(f'[{hora_atual}] {mensagem}' + '\n')

def debug_log(mensagem):
    with open(log_debug_file, 'a') as log:
        hora_atual = datetime.now().strftime("%H:%M:%S")
        log.write(f'[{hora_atual}] {mensagem}' + '\n')

def criar_pastas():
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    if not os.path.exists(pasta_origem):
        os.makedirs(pasta_origem)
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        
def ler_arquivos():
    qtde_lidos = 0  # Inicialize a variável para contar os arquivos lidos
    qtde_registros = 0
    retorno = []

    extrator_log(f"[INFO] Extracao iniciada!")
    for arquivo_xml in os.listdir(pasta_origem):
        if arquivo_xml.endswith(".xml"):
            caminho_completo = os.path.join(pasta_origem, arquivo_xml)

            try:
                tree = etree.parse(caminho_completo)
                root = tree.getroot()

                extrator_log(f"[INFO] Processando arquivo: {arquivo_xml}")
                qtde_lidos += 1 

                xml_string = etree.tostring(root, pretty_print=False, encoding='utf-8').decode('utf-8')

                # BUSCA PELAS TAGS EM QUESTÃO
                soup = BeautifulSoup(xml_string, "lxml")
                for tag_name, atributo in tags_xml.items():
                    tag_temporaria = soup.find_all(tag_name)
                    for tag in tag_temporaria:

                        nitem = tag.get(atributo)
                        conteudo_temporario = tag.prettify()
                        qtde_registros += 1 
                        retorno.append(conteudo_temporario)

                        if debug_mode:
                            debug_log(f"[DEBUG] Conteudo dentro da tag {tag_name} ({atributo}): \n    {conteudo_temporario}")

                    if not tag_temporaria:
                        extrator_log(f"[ERRO] Não foi encontrada a tag {tag_name} no arquivo {arquivo_xml}")

                if not debug_mode:
                    destino_completo = os.path.join(pasta_destino, arquivo_xml)
                    os.rename(caminho_completo, destino_completo)
                    extrator_log(f"[SUCESSO] {arquivo_xml} processado e movido para a pasta de destino.")

            except Exception as e:
                extrator_log(f"[ERRO] {arquivo_xml}: {str(e)}") 

    return retorno,qtde_lidos,qtde_registros

def extrair_conteudo(lista_xml, tags_desejadas, nome_arquivo_csv):
    # Inicialize uma lista para armazenar os resultados de cada item XML
    resultados = []

    # Itere pela lista de XML
    for xml_string in lista_xml:
        # Parse a string XML em uma árvore XML
        root = ET.fromstring(xml_string)

        # Crie um dicionário para armazenar o conteúdo das tags desejadas
        conteudo_tags = {}

        # Itere pelas tags desejadas e extraia seu conteúdo
        for tag in tags_desejadas:
            elemento = root.find(".//" + tag)

            if elemento is not None:
                conteudo = elemento.text
            else:
                conteudo = "null"
            
            conteudo_tags[tag] = conteudo

        # Adicione o conteúdo das tags a resultados
        resultados.append([conteudo_tags[tag] for tag in tags_desejadas])

    # Escreva o conteúdo no arquivo CSV
    with open(nome_arquivo_csv, mode='w', newline='') as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=';')

        # Escreva o cabeçalho (nomes das tags)
        writer.writerow(tags_desejadas)

        # Escreva o conteúdo nas linhas seguintes
        for resultado in resultados:
            writer.writerow(resultado)


# LEITURA DOS ARQUIVOS ##########################################################################

criar_pastas()
retorno_arquivos, qtde_lidos, qtde_registros = ler_arquivos()
extrair_conteudo(retorno_arquivos, tags_desejadas, nome_arquivo_csv)
extrator_log(f"[INFO] Processamento e transferencia de arquivos XML concluidos, Lidos {qtde_lidos} arquivos e inseridas {qtde_registros} linhas no arquivo CSV")