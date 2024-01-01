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

tab_titles = ['Rankig Ações', 'Recomendação', 'Ranking Fiis']
tab1, tab2, tab3 = st.tabs(tab_titles)

Ac,Fii = requisitar_dados()

col1, col2 = st.columns(2)
with tab1:
    with st.container():
        Ac = Ac[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'Setor', 'Segmento']].head(20).round(2)

        # Agrupar por setor e contar a quantidade
        contagem_por_setor = Ac.groupby('Setor').size().reset_index(name='Quantidade')
        # Ordenar pelo maior
        contagem_por_setor = contagem_por_setor.sort_values(by='Quantidade', ascending=False)
        # Obter uma paleta de cores exclusiva com base nas categorias únicas
        palette = px.colors.qualitative.Plotly[:len(contagem_por_setor['Setor'].unique())]

        # Mapear cada categoria para uma cor da paleta
        color_mapping = dict(zip(contagem_por_setor['Setor'].unique(), palette))

        # Função para aplicar cores automaticamente
        def highlight_sector(val):
            return f'background-color: {color_mapping.get(val, "white")}'


        # Aplicar estilos condicionais ao DataFrame
        styled_df = Ac.round(2).style.applymap(highlight_sector, subset=['Setor'])

        fig = px.pie(contagem_por_setor, values='Quantidade', names='Setor', title='Setores', hole=0.5,color_discrete_sequence=palette)

        st.plotly_chart(fig)

    with st.container():
        st.write('Ranking de ações calculadas com base no P/L e ROE')
        Acpj = Ac

        # Exibir o DataFrame estilizado no Streamlit
        st.dataframe(styled_df)

with tab2:
    with st.container():
        Acpj['Mrg. Seg.'] = (1 - (Acpj['Cotação'] / Acpj['PJ'])) * 100
        Acpj = Acpj[Acpj['Mrg. Seg.'] > 0]
        Acpj = Acpj[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.','Setor', 'Segmento']].head(20)

        graf2 = Acpj
        graf2['QTD'] = 1
        fig = px.pie(graf2, values='QTD', names='Setor', title='Setores', hole=0.5,color_discrete_sequence=palette)
        st.plotly_chart(fig)

    with st.container():
        st.write('Lista das ações com base no Preço justo')
        Acpj = Acpj[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.', 'Setor', 'Segmento']].round(2)

        st.data_editor(
            Acpj,
            column_config={
                "Mrg. Seg.": st.column_config.ProgressColumn(
                    help="Margem de segurança",
                    format="%f",
                    min_value=0,
                    max_value=Acpj['Mrg. Seg.'].max(),
                ),
                "Cotação": st.column_config.NumberColumn(
                    format="R$ %f",
                ),
                "PJ": st.column_config.NumberColumn(
                    help="Preço Justo",
                    format="R$ %f",
                ),
            },
            hide_index=True,
        )

        #st.dataframe(Acpj)

with tab3:
    Fii['Qtd de imóveis'] = Fii['Qtd de imóveis'].astype(float)
    with st.container():
        graf3 = Fii  # .head(10)
        graf3['QTD'] = 1
        fig = px.pie(graf3, values='QTD', names='Segmento', title='Segmentos', hole=0.5,color_discrete_sequence=palette)

        # Show the plot
        st.plotly_chart(fig)

    with st.container():
        st.subheader('Lista de Fiis de Tijolo')

        Fii = Fii[['Papel','Segmento', 'Cotação', 'Dividend Yield', 'FFO Yield', 'P/VP', 'Qtd de imóveis']]

        st.data_editor(
            Fii.round(2),
            column_config={
                "Qtd de imóveis": st.column_config.ProgressColumn(
                    label= 'Imóveis',
                    format="%f",
                    help="Margem de segurança",
                    min_value=0,
                    max_value=Fii['Qtd de imóveis'].max(),
                ),
                "Dividend Yield": st.column_config.ProgressColumn(
                    help="Margem de segurança",
                    label='DY',
                    format="%f",
                    min_value=0,
                    max_value=Fii['Dividend Yield'].max(),
                ),

                "Cotação": st.column_config.NumberColumn(
                    format="R$ %f",
                ),
            },
            hide_index=True,
        )

