import csv
from datetime import datetime

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

from selenium.webdriver.common.by import By
import os
from os import path

def get_dados():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('window-size=1500,800')

    navegador = webdriver.Chrome(options=options)

    navegador.get('https://landing.shopper.com.br/')

    sleep(2)

    login_button = navegador.find_element(By.CLASS_NAME, 'login')
    login_button.click()
    sleep(3)

    email = navegador.find_element(By.NAME, 'email')
    email.send_keys('<seuemailaqui>@gmail.com')
    senha = navegador.find_element(By.NAME, 'senha')
    senha.send_keys('<suasenhaaqui>')
    senha.submit()
    sleep(15)
    try:
        entendido = navegador.find_element(By.XPATH, '//*[@id="cadastro_b"]/div[3]/div[2]/div/div/div/div/div[4]/button')
        entendido.click()
    except:
        pass

    alimentos = navegador.find_element(By.XPATH, '//*[@id="cadastro_b"]/div[1]/div[4]/ul/li[3]/a')
    alimentos.click()

    conteudo = navegador.page_source

    return conteudo

def buscar_informacoes(conteudo):
    soup = bs(conteudo, 'html.parser')

    resultado = []
    resultado_seller = []
    categorias = soup.find_all('div', class_='department carousel-products loaded')


    for categoria in categorias:
        nome_categoria = categoria.find('div', 'department-name').find('span').get_text().strip()

        itens = soup.find_all('div', class_='sc-fkJVfC cMvCOU')
        for item in itens:
            item_dic = {}
            nome_item = item.find('p', class_='sc-kHdrYz dUFjAH').get_text().strip()
            imagem = item.find('div', class_='sc-gfqkcP boWfZO').find('img').get('src').strip()
            preco = item.find('p', class_='priceP').get_text().strip().replace(',', '.')
            try:
                preco = float(preco)
            except:
                preco = 0.0

            try:
                desconto = item.find('p', class_='economyP').get_text().strip()
            except:
                desconto = '0%'

            try:
                seller_players = item.find_all('div', class_='market')
                seller_player = seller_players[0].find('div', class_='img').find('img').get('alt').replace('merchant ', '')
                price_player = seller_players[0].find('div', class_='price').find('p').get_text().replace(',', '.')
                price_player = float(price_player)
            except:
                seller_player = None
                price_player = None

            item_dic['name'] = nome_item
            item_dic['department'] = 'Alimentos'
            item_dic['category'] = nome_categoria
            item_dic['image'] = imagem
            item_dic['price_to'] = preco
            item_dic['discount'] = desconto
            item_dic['store'] = 'Shopper'
            item_dic['created_at'] = datetime.now().date()
            item_dic['hour'] = datetime.now().time()
            resultado.append(item_dic)

            item_dic_seller = {}

            item_dic_seller['name'] = nome_item
            item_dic_seller['department'] = 'Alimentos'
            item_dic_seller['category'] = nome_categoria
            item_dic_seller['seller_store'] = 'Shopper'
            item_dic_seller['seller_player'] = seller_player
            item_dic_seller['price_store'] = preco
            item_dic_seller['price_player'] = price_player
            item_dic_seller['discount_store'] = desconto
            item_dic_seller['image'] = imagem
            item_dic_seller['created_at'] = datetime.now().date()
            item_dic_seller['hour'] = datetime.now().time()
            resultado_seller.append(item_dic_seller)

    return [resultado, resultado_seller]

def criar_arquivos(resultado, resultado_seller):
    keys = resultado[0].keys()
    with open('assortment.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(resultado)

    keys = resultado_seller[0].keys()
    with open('seller.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(resultado_seller)

conteudo = get_dados()
informacoes = buscar_informacoes(conteudo)

hoje = str(datetime.now()).replace('.', ' ').replace(':','-')
if path.exists("assortment.csv"):
    os.rename('assortment.csv', f'assortment-{hoje}.csv')
if path.exists("seller.csv"):
    os.rename('seller.csv', f'seller-{hoje}.csv')

if len(informacoes) == 2:
    exportar = criar_arquivos(informacoes[0], informacoes[1])
