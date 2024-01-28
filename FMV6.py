# importar bibliotecas

from datetime import date

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

# Esta função busca dos dados de açoes e fii no site FUNDAMENTUS e cria 2 arquivos em excel
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
    return df, dfii


def formula_magica_ROE(df):
    # Filtros no data frame de Ações

    Cot = df[df['Cotação'] <= 100]
    # Cot = Cot[Cot['Mrg. Líq.'] >= 5]

    maiorLiquidez = Cot[Cot['Liq.2meses'] >= 800000]
    maiorLiquidez = maiorLiquidez[(maiorLiquidez['Dív.Brut/ Patrim.'] >= 0) & (maiorLiquidez['Dív.Brut/ Patrim.'] <= 3)]
    maiorLiquidez = maiorLiquidez[(maiorLiquidez['P/L'] > 0) & (maiorLiquidez['P/L'] < 50)]
    maiorLiquidez = maiorLiquidez[maiorLiquidez['ROE'] > 9]


    novo = maiorLiquidez  # [['Papel', 'Cotação', 'Div.Yield' , 'P/L', 'ROE', 'Cresc. Rec.5a', 'Mrg. Líq.']]

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

    Ac = dados  # [['Papel', 'Cotação', 'Div.Yield' , 'P/L', 'ROE', 'PJ', 'Setor', 'Seg', 'Nome Curto', 'Nome Longo']]

    # dados['Prec. Compra'] = dados['Cotação'] * dados['Div.Yield']/6 * 0.9
    # dados['Prec. Venda'] = dados['Cotação'] * dados['Div.Yield']/6 * 1.2

    Ac.reset_index(inplace=True)
    Ac = Ac.drop('index', axis=1)

    Ac.to_excel('Ações_Mágicas_ROE.xlsx', index=False)
    #carteirahj = 'Ações_Mágicas_' + str(hoje) + '.xlsx'
    #Ac.to_excel(carteirahj, index=False)

    return Ac


def formula_magica_ROIC(df):
    # Filtros no data frame de Ações

    Cot = df[df['Cotação'] <= 100]
    # Cot = Cot[Cot['Mrg. Líq.'] >= 5]

    maiorLiquidez = Cot[Cot['Liq.2meses'] >= 800000]
    maiorLiquidez = maiorLiquidez[(maiorLiquidez['Dív.Brut/ Patrim.'] >= 0) & (maiorLiquidez['Dív.Brut/ Patrim.'] < 3)]
    maiorLiquidez = maiorLiquidez[maiorLiquidez['EV/EBIT'] > 0]
    maiorLiquidez = maiorLiquidez[maiorLiquidez['ROIC'] > 0]

    novo = maiorLiquidez  # [['Papel', 'Cotação', 'Div.Yield' , 'EV/EBIT', 'ROIC', 'PJ', 'Setor', 'Seg', 'Nome Curto', 'Nome Longo']]

    # Aplicação da fórmula nas ações

    Oev = novo.sort_values(by='EV/EBIT')
    Oev = Oev.reset_index(drop=True)
    Oev['Ordem EV/EBIT'] = Oev.index

    Oroic = Oev.sort_values(by='ROIC', ascending=False)
    Oroic = Oroic.reset_index(drop=True)
    Oroic['Ordem ROIC'] = Oroic.index
    dados = Oroic

    dados['Score'] = dados['Ordem EV/EBIT'] + dados['Ordem ROIC']
    dados = dados.sort_values(by='Score', ascending=True)

    # Remove os Tickers duplicados
    dados['PapelF'] = dados['Papel'].str[:4]
    dados = dados.drop_duplicates(subset='PapelF')

    Ac = dados  # [['Papel', 'Cotação', 'Div.Yield' , 'EV/EBIT', 'Cresc. Rec.5a', 'ROIC']]

    Ac.reset_index(inplace=True)
    Ac = Ac.drop('index', axis=1)

    Ac.to_excel('Ações_Mágicas_ROIC.xlsx', index=False)
    # carteirahj = 'Ações_Mágicas_' + str(hoje) + '.xlsx'
    # Ac.to_excel(carteirahj, index=False)

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
    # FiiT = FiiT[['Papel','Cotação','Dividend Yield', 'FFO Yield', 'P/VP', 'Valor de Mercado', 'Qtd de imóveis' 'PJ', 'Setor', 'Seg', 'Segmento', 'Nome Curto', 'Nome Longo']]

    Opvp = FiiT.sort_values(by='P/VP', ascending=True)
    Opvp = Opvp.reset_index(drop=True)
    Opvp['Ordem P/VP'] = Opvp.index

    Offo = Opvp.sort_values(by='FFO Yield', ascending=False)
    Offo = Offo.reset_index(drop=True)
    Offo['Ordem FFO Yield'] = Offo.index

    Offo['Score'] = Offo['Ordem P/VP'] + Offo['Ordem FFO Yield']
    FiiT = Offo.sort_values(by='Score', ascending=True)

    # FiiT = FiiT[['Papel', 'Segmento', 'Cotação','Dividend Yield', 'P/VP','Qtd de imóveis']]

    FiiT.reset_index(inplace=True)
    FiiT.drop('index', axis=1, inplace=True)

    FiiT.to_excel('Fii_Tij_Hibrid_Mágicas.xlsx', index=False)
    #Fiicarteirahj = 'Fii_Tij_Hibrid_Mágicas_' + str(hoje) + '.xlsx'
    #FiiT.to_excel(Fiicarteirahj, index=False)

    # Rodar essa parte apenas em datas específicas

    # Aplicação da fórmula de Fii Papel

    FiiP = Vaq[(Vaq['Qtd de imóveis'] <= 0) & (Vaq['P/VP'] >= 0.50)]
    # FiiP = FiiP[FiiP['P/VP'] >= 0.50]

    # FiiP = FiiP[['Papel', 'Segmento', 'Cotação', 'FFO Yield', 'Dividend Yield', 'P/VP', 'Valor de Mercado']]

    Opvp = FiiP.sort_values(by='P/VP', ascending=True)
    Opvp = Opvp.reset_index(drop=True)
    Opvp['Ordem P/VP'] = Opvp.index

    Offo = Opvp.sort_values(by='FFO Yield', ascending=False)
    Offo = Offo.reset_index(drop=True)
    Offo['Ordem FFO Yield'] = Offo.index

    Offo['Score'] = Offo['Ordem P/VP'] + Offo['Ordem FFO Yield']
    FiiP = Offo.sort_values(by='Score', ascending=True)

    # FiiP = FiiP[['Papel', 'Segmento', 'Cotação','Dividend Yield', 'P/VP']]

    FiiP.reset_index(inplace=True)
    FiiP.drop('index', axis=1, inplace=True)
    FiiP.to_excel('Fii_Papel_Mágicas.xlsx', index=False)
    #FiiPcarteirahj = 'Fii_Papel_Mágicas_' + str(hoje) + '.xlsx'
    #FiiP.to_excel(FiiPcarteirahj, index=False)

    return FiiT

def hist_dividendos_5anos(Ac):
    # histórico de dividendos das ações
    tickers = Ac.loc[:, 'Papel'] + ".SA"

    dividendos = []
    segmento = []
    setor = []
    nome_c = []
    #nome_l = []

    for ticker in tickers:
        div6 = []

        try:
            div = yf.Ticker(ticker).dividends
            setr = yf.Ticker(ticker).info['sector']
            seg = yf.Ticker(ticker).info['industry']
            nc = yf.Ticker(ticker).info['shortName']
            #nl = yf.Ticker(ticker).info['longName']

        except Exception as e:
            # print(f"Erro ao obter dividendos para {ticker}: {e}")
            y = 0
            dividendos.append(y)
            setor.append(y)
            segmento.append(y)
            nome_c.append(y)
            #nome_l.append(y)

        else:

            anos = ['2023', '2022', '2021']
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
            nome_c.append(nc)
            #nome_l.append(nl)

    Ac['Div. 3A'] = dividendos
    Ac['PJ'] = (Ac['Div. 3A'] / 3) / 0.06
    Ac['Setor'] = setor
    Ac['Seg'] = segmento
    Ac['Nome Curto'] = nome_c
    #Ac['Nome Longo'] = nome_l

    # Ac.to_excel('Ações_Mágicas.xlsx', index=False)
    # carteirahj = 'Ações_Mágicas_' + str(hoje) + '.xlsx'
    # Ac.to_excel(carteirahj, index=False)

    return Ac

# chama funçoes

df, dfii = baixar_dados_AC_and_FII()
ROE = formula_magica_ROE(df)
ROIC = formula_magica_ROIC(df)
fii = formula_fii(dfii)

ROE = hist_dividendos_5anos(ROE)
ROE = ROE[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'P/L', 'ROE', 'P/VP', 'Div. 3A', 'Setor', 'Seg', 'Nome Curto', 'Nome Longo']]

ROIC = hist_dividendos_5anos(ROIC)
ROIC = ROIC[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'EV/EBIT', 'ROIC', 'P/VP', 'Div. 3A', 'Setor', 'Seg', 'Nome Curto', 'Nome Longo']]

ROE.to_excel('Ações_Mágicas_ROE.xlsx', index=False)
ROIC.to_excel('Ações_Mágicas_ROIC.xlsx', index=False)

#fii = hist_dividendos_5anos(fii)
#fii = fii[['Papel', 'Segmento', 'Cotação', 'Dividend Yield', 'FFO Yield', 'P/VP', 'Qtd de imóveis']]

#fii.to_excel('Fii_Tij_Hibrid_Mágicas.xlsx', index=False)
