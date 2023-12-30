# importar bibliotecas

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import random
from datetime import date, datetime, timedelta

#Esta função busca dos dados de açoes e fii no site FUNDAMENTUS e cria 2 arquivos em excel
hoje = date.today()


def baixar_dados_AC_and_FII():
    # Busca no site fundamentus

    url = 'https://www.fundamentus.com.br/resultado.php'
    urlfii = 'https://www.fundamentus.com.br/fii_resultado.php'

    agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

    resposta = requests.get(url, headers=agent)
    respostafii = requests.get(urlfii, headers=agent)

    soup = BeautifulSoup(resposta.text, 'lxml')
    soupfii = BeautifulSoup(respostafii.text, 'lxml')

    tabela = soup.find_all('table')[0]
    tabelafii = soupfii.find_all('table')[0]

    df = pd.read_html(str(tabela), decimal=',', thousands='.')[0]
    dfii = pd.read_html(str(tabelafii), decimal=',', thousands='.')[0]

    # Lista de colunas de Ações com %
    colunas = ['Div.Yield', 'ROIC', 'Mrg Ebit', 'Mrg. Líq.', 'ROE', 'Cresc. Rec.5a']

    # Loop for para processar cada coluna
    for coluna in colunas:
        df[coluna] = df[coluna].str.replace("%", "", regex=False)
        df[coluna] = df[coluna].str.replace(".", "", regex=False)
        df[coluna] = df[coluna].str.replace(",", ".", regex=False)
        df[coluna] = df[coluna].astype(float)

    # Lista de colunas de Fiis com %
    colunasf = ['Dividend Yield', 'FFO Yield', 'Vacância Média', 'Cap Rate']

    # Loop for para processar cada coluna
    for coluna in colunasf:
        dfii[coluna] = dfii[coluna].str.replace("%", "", regex=False)
        dfii[coluna] = dfii[coluna].str.replace(".", "", regex=False)
        dfii[coluna] = dfii[coluna].str.replace(",", ".", regex=False)
        dfii[coluna] = dfii[coluna].astype(float)

    df.to_excel('dadosAções.xlsx', index=False)
    dfii.to_excel('dadosFii.xlsx', index=False)

    # dfcarteirahj = 'dadosAções_' + str(hoje) + '.xlsx'
    # dfiicarteirahj = 'dadosFii_' + str(hoje) + '.xlsx'
    # df.to_excel(dfcarteirahj, index=False)
    # dfii.to_excel(dfiicarteirahj, index=False)
    return df,dfii


def formula_magica(df):
    # Filtros no data frame de Ações

    Cot = df[df['Cotação'] <= 100]
    # Cot = Cot[Cot['Mrg. Líq.'] >= 5]

    maiorLiquidez = Cot[Cot['Liq.2meses'] >= 1000000]
    maiorLiquidez = maiorLiquidez[maiorLiquidez['P/L'] > 0]
    maiorLiquidez = maiorLiquidez[maiorLiquidez['ROE'] > 9]

    # patrimonioLiquido = maiorLiquidez[maiorLiquidez['Patrim. Líq'] >= 0]
    # roic = patrimonioLiquido[patrimonioLiquido['ROE'] >= 0]
    # roic = roic[roic['EV/EBIT'] >= 0]
    # EVEBIT = EVEBIT[EVEBIT['Cresc. Rec.5a'] >=0]
    # EVEBIT

    novo = maiorLiquidez[['Papel', 'Cotação', 'Div.Yield', 'P/L', 'ROE', 'Cresc. Rec.5a', 'Mrg. Líq.']]

    # Aplicação da fórmula nas ações

    Oev = novo.sort_values(by='P/L')
    Oev = Oev.reset_index(drop=True)
    Oev['Ordem P/L'] = Oev.index

    Oroic = Oev.sort_values(by='ROE', ascending=False)
    Oroic = Oroic.reset_index(drop=True)
    Oroic['Ordem ROE'] = Oroic.index
    dados = Oroic

    dados['Score'] = dados['Ordem P/L'] + dados['Ordem ROE']
    dados = dados.sort_values(by='Score', ascending=True)

    # Remove os Tickers duplicados
    dados['PapelF'] = dados['Papel'].str[:4]
    dados = dados.drop_duplicates(subset='PapelF')

    Ac = dados[['Papel', 'Cotação', 'Div.Yield', 'P/L', 'Cresc. Rec.5a', 'Mrg. Líq.']]

    # dados['Prec. Compra'] = dados['Cotação'] * dados['Div.Yield']/6 * 0.9
    # dados['Prec. Venda'] = dados['Cotação'] * dados['Div.Yield']/6 * 1.2

    Ac.reset_index(inplace=True)
    Ac = Ac.drop('index', axis=1)

    Ac.to_excel('Ações_Mágicas.xlsx', index=False)
    #carteirahj = 'Ações_Mágicas_' + str(hoje) + '.xlsx'
    #Ac.to_excel(carteirahj, index=False)

    return Ac


def formula_fii(dfii):
    # Rodar essa parte apenas em datas específicas

    # Filtros no data frame de Fii

    # Cotacao = dfii[dfii['Cotação'] <= 200]
    # Liq = Cotacao[Cotacao['Liquidez'] >= 1000000]
    # Vaq = Liq[Liq['Vacância Média'] <= 7]
    Vaq = dfii[(dfii['Cotação'] <= 300) & (dfii['Liquidez'] >= 900000) & (dfii['Vacância Média'] <= 7)]

    # Aplicação da fórmula de Fii Hibrid

    FiiT = Vaq[Vaq['Qtd de imóveis'] >= 5]
    FiiT = FiiT[
        ['Papel', 'Segmento', 'Cotação', 'Dividend Yield', 'FFO Yield', 'P/VP', 'Valor de Mercado', 'Qtd de imóveis']]

    Opvp = FiiT.sort_values(by='P/VP', ascending=True)
    Opvp = Opvp.reset_index(drop=True)
    Opvp['Ordem P/VP'] = Opvp.index

    Offo = Opvp.sort_values(by='FFO Yield', ascending=False)
    Offo = Offo.reset_index(drop=True)
    Offo['Ordem FFO Yield'] = Offo.index

    Offo['Score'] = Offo['Ordem P/VP'] + Offo['Ordem FFO Yield']
    FiiT = Offo.sort_values(by='Score', ascending=True)

    FiiT = FiiT[['Papel', 'Segmento', 'Cotação', 'Dividend Yield', 'P/VP', 'Qtd de imóveis']]

    FiiT.reset_index(inplace=True)
    FiiT.drop('index', axis=1, inplace=True)

    FiiT.to_excel('Fii_Tij_Hibrid_Mágicas.xlsx', index=False)
    #Fiicarteirahj = 'Fii_Tij_Hibrid_Mágicas_' + str(hoje) + '.xlsx'
    #FiiT.to_excel(Fiicarteirahj, index=False)

    # Rodar essa parte apenas em datas específicas

    # Aplicação da fórmula de Fii Papel

    FiiP = Vaq[(Vaq['Qtd de imóveis'] <= 0) & (Vaq['P/VP'] >= 0.50)]
    # FiiP = FiiP[FiiP['P/VP'] >= 0.50]

    FiiP = FiiP[['Papel', 'Segmento', 'Cotação', 'FFO Yield', 'Dividend Yield', 'P/VP', 'Valor de Mercado']]

    Opvp = FiiP.sort_values(by='P/VP', ascending=True)
    Opvp = Opvp.reset_index(drop=True)
    Opvp['Ordem P/VP'] = Opvp.index

    Offo = Opvp.sort_values(by='FFO Yield', ascending=False)
    Offo = Offo.reset_index(drop=True)
    Offo['Ordem FFO Yield'] = Offo.index

    Offo['Score'] = Offo['Ordem P/VP'] + Offo['Ordem FFO Yield']
    FiiP = Offo.sort_values(by='Score', ascending=True)

    FiiP = FiiP[['Papel', 'Segmento', 'Cotação', 'Dividend Yield', 'P/VP']]

    FiiP.reset_index(inplace=True)
    FiiP.drop('index', axis=1, inplace=True)
    FiiP.to_excel('Fii_Papel_Mágicas.xlsx', index=False)
    #FiiPcarteirahj = 'Fii_Papel_Mágicas_' + str(hoje) + '.xlsx'
    #FiiP.to_excel(FiiPcarteirahj, index=False)

    return FiiT,FiiP


def hist_dividendos_5anos(Ac):
    # histórico de dividendos das ações
    tickers = Ac.loc[:, 'Papel'] + ".SA"

    dividendos = []
    segmento = []
    setor = []

    for ticker in tickers:
        div6 = []

        try:
            div = yf.Ticker(ticker).dividends
            setr = yf.Ticker(ticker).info['sector']
            seg = yf.Ticker(ticker).info['industry']

        except Exception as e:
            print(f"Erro ao obter dividendos para {ticker}: {e}")
            y = 0
            dividendos.append(y)
            setor.append(y)
            segmento.append(y)

        else:

            anos = ['2023', '2022', '2021', '2019', '2018']
            div6 = []
            # Lista para os dividendos dos últimos 6 anos
            for x in anos:
                if x in div:
                    div6.append(div[x].sum())
                else:
                    div6.append(0)
            y = sum(div6)
            dividendos.append(y)
            setor.append(setr)
            segmento.append(seg)

    Ac['Div. 5A'] = dividendos
    Ac['PJ'] = (Ac['Div. 5A'] / 5) / 0.06
    Ac['Setor'] = setor
    Ac['Segmento'] = segmento

    Ac = Ac[(Ac['Setor'] != 'Real Estate') & (Ac['Segmento'] != 'Household & Personal Products')]

    Ac.to_excel('Ações_Mágicas.xlsx', index=False)
    # carteirahj = 'Ações_Mágicas_' + str(hoje) + '.xlsx'
    # Ac.to_excel(carteirahj, index=False)

    return Ac

# chama funçoes

df,dfii = baixar_dados_AC_and_FII()

Ac = formula_magica(df)
Ac = hist_dividendos_5anos(Ac)
fii = formula_fii(dfii)
