import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title='Fórmula mágica')

with st.container():
    st.title('Bons Investimentos a bons preços')
    st.subheader('Tabela de ações')


@st.cache_data
def requisitar_dados():
    Ac = pd.read_excel('Ações_Mágicas.xlsx')

    Fii = pd.read_excel('Fii_Tij_Hibrid_Mágicas.xlsx')

    Ac = Ac[Ac['Papel'] != 'JPSA3']

    tickers = list(Ac['Papel'] + ".SA")

    # Fetch stock data
    cot = yf.download(tickers, period='1d')

    # Extract relevant information
    stock_info = pd.DataFrame(index=tickers)
    stock_info['Cotação'] = cot['Adj Close'].iloc[-1]
    Ac['Cotação'] = list(stock_info['Cotação'])

    #PAra os Fiis

    tickersf = list(Fii['Papel'] + ".SA")

    # Fetch stock data
    cotf = yf.download(tickersf, period='1d')

    # Extract relevant information
    stock_infof = pd.DataFrame(index=tickersf)
    stock_infof['Cotação'] = cotf['Adj Close'].iloc[-1]
    Fii['Cotação'] = list(stock_infof['Cotação'])



    return Ac,Fii

with st.container():
    st.write('Ranking de ações calculadas com base no P/L e ROE')

    Ac,Fii = requisitar_dados()
    Acpj = Ac
    Ac = Ac[['Papel', 'Cotação', 'PJ','Div.Yield','Setor', 'Segmento']]

st.dataframe(Ac)

with st.container():
    graf = Ac.head(15)
    graf['QTD'] = 1
    fig = px.pie(graf, values='QTD', names='Setor', title='Setores', hole=0.5)

    st.plotly_chart(fig)

st.write('---')

with st.container():
    st.subheader('Lista das ações com base no Preço justo')
    Acpj['Mrg. Seg.'] = (1 - (Acpj['Cotação'] / Acpj['PJ'])) * 100
    Acpj = Acpj[Acpj['Mrg. Seg.'] > -10]
    Acpj = Acpj[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.','Setor', 'Segmento']]

    st.dataframe(Acpj)

with st.container():
    graf2 = Acpj.head(10)
    graf2['QTD'] = 1
    fig = px.pie(graf2, values='QTD', names='Setor', title='Setores', hole=0.5)

    # Show the plot
    st.plotly_chart(fig)

st.write('---')

with st.container():
    st.subheader('Lista de Fiis de Tijolo')
    st.dataframe(Fii)

with st.container():
    graf3 = Fii#.head(10)
    graf3['QTD'] = 1
    fig = px.pie(graf3, values='QTD', names='Segmento', title='Segmentos', hole=0.5)

    # Show the plot
    st.plotly_chart(fig)