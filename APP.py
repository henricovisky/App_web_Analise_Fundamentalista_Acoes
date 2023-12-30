import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px


st.set_page_config(page_title='Fórmula mágica')

with st.container():
    st.title('Bons Investimentos a bons preços')
    st.subheader('Tabela de ações')


@st.cache_data
def requisitar_dados():
    Ac = pd.read_excel('Ações_Mágicas.xlsx')
    Ac = Ac[Ac['Papel'] != 'JPSA3']

    tickers = list(Ac['Papel'] + ".SA")

    # Fetch stock data
    cot = yf.download(tickers, period='1d')

    # Extract relevant information
    stock_info = pd.DataFrame(index=tickers)
    stock_info['Cotação'] = cot['Adj Close'].iloc[-1]
    Ac['Cotação'] = list(stock_info['Cotação'])

    return Ac

#col1, col2 = st.columns(2)

with st.container():
    st.write('Ranking de ações calculadas com base no P/L e ROE')
    st.write('---')
    Ac = requisitar_dados()
    Ac = Ac[['Papel', 'Cotação', 'PJ','Div.Yield','Setor', 'Segmento']]

    st.dataframe(Ac)

with st.container():
    graf = Ac.head(15)
    graf['QTD'] = 1
    fig = px.pie(graf, values='QTD', names='Setor', title='Stock Segments', hole=0.5)

    # Show the plot
    st.plotly_chart(fig)

#col3, col4 = st.columns(2)

with st.container():
    st.write('Lista das ações com base no Preço justo')
    st.write('---')
    Acpj = requisitar_dados()
    Acpj['Mrg. Seg.'] = (1 - (Acpj['Cotação'] / Acpj['PJ'])) * 100
    Acpj = Acpj[Acpj['Mrg. Seg.'] > -10]
    Acpj = Acpj[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.','Setor', 'Segmento']]

    st.dataframe(Acpj)

with st.container():
    graf2 = Acpj.head(10)
    graf2['QTD'] = 1
    fig = px.pie(graf2, values='QTD', names='Setor', title='Stock Segments', hole=0.5)

    # Show the plot
    st.plotly_chart(fig)