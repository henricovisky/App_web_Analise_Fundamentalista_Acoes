import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title='Fórmula mágica')


with st.container():
    st.title('Portifólio de investimendo automático')

@st.cache_data
def requisitar_dados():
    Ac = pd.read_excel('Ações_Mágicas_ROE.xlsx')
    Ac_ROIC = pd.read_excel('Ações_Mágicas_ROIC.xlsx')
    Fii = pd.read_excel('Fii_Tij_Hibrid_Mágicas.xlsx')

    Ac = Ac[Ac['Papel'] != 'JPSA3']
    Ac_ROIC = Ac_ROIC[Ac_ROIC['Papel'] != 'JPSA3']

    tickers = list(Ac['Papel'] + ".SA")
    # Fetch stock data
    cot = yf.download(tickers, period='1d')
    # Extract relevant information
    stock_info = pd.DataFrame(index=tickers)
    stock_info['Cotação'] = cot['Adj Close'].iloc[-1]
    Ac['Cotação'] = list(stock_info['Cotação'])

    # PAra os ROIC
    tickersR = list(Ac_ROIC['Papel'] + ".SA")
    # Fetch stock data
    cotR = yf.download(tickersR, period='1d')
    # Extract relevant information
    stock_infoR = pd.DataFrame(index=tickersR)
    stock_infoR['Cotação'] = cotR['Adj Close'].iloc[-1]
    Ac_ROIC['Cotação'] = list(stock_infoR['Cotação'])

    #PAra os Fiis
    tickersf = list(Fii['Papel'] + ".SA")
    # Fetch stock data
    cotf = yf.download(tickersf, period='1d')
    # Extract relevant information
    stock_infof = pd.DataFrame(index=tickersf)
    stock_infof['Cotação'] = cotf['Adj Close'].iloc[-1]
    Fii['Cotação'] = list(stock_infof['Cotação'])

    return Ac,Fii, Ac_ROIC

tab_titles = ['Rankig Ações', 'Recomendação', 'Ranking Fiis']
tab1, tab2, tab3 = st.tabs(tab_titles)

Ac,Fii,Ac_ROIC = requisitar_dados()

col1, col2 = st.columns(2)
with tab1:
    with st.container():
        #Acpj_ROE = Ac[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'Setor', 'Seg']]
        Acpj_ROIC = Ac_ROIC
        Ac_ROE = Ac[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'Setor', 'Seg']].head(20).round(2)

        # Agrupar por setor e contar a quantidade
        contagem_por_setor = Ac_ROE.groupby('Setor').size().reset_index(name='Quantidade')
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
        styled_df = Ac_ROE.round(2).style.applymap(highlight_sector, subset=['Setor'])

        fig = px.pie(contagem_por_setor, values='Quantidade', names='Setor', title='Setores', hole=0.5,color_discrete_sequence=palette)

        st.plotly_chart(fig)

    with st.container():
        st.write('Ranking de ações calculadas com base no P/L e ROE')


        # Exibir o DataFrame estilizado no Streamlit
        st.dataframe(styled_df)


        Ac_ROIC = Ac_ROIC[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'Setor', 'Seg']].head(20).round(2)
        st.write('Ranking de ações calculadas com base no EV/EBIT e ROIC')

        # Exibir o DataFrame estilizado no Streamlit
        st.dataframe(Ac_ROIC)

    with st.container():
        #limpar setores específicos
        Ac_limp_seg = Ac[['Papel', 'Cotação', 'PJ', 'Div.Yield', 'Setor', 'Seg']]
        Ac_limp_seg = Ac_limp_seg[(Ac_limp_seg['Setor'] != 'Real Estate') & (Ac_limp_seg['Setor'] != 'Consumer Cyclical')]

        st.dataframe(Ac_limp_seg)


with tab2:
    with st.container():
        Acpj = Ac
        Acpj['Mrg. Seg.'] = (1 - (Acpj['Cotação'] / Acpj['PJ'])) * 100
        Acpj = Acpj[Acpj['Mrg. Seg.'] > -5]
        Acpj = Acpj[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.','Setor', 'Seg']]#.head(20)

        graf2 = Acpj
        graf2['QTD'] = 1
        fig = px.pie(graf2, values='QTD', names='Setor', title='Setores', hole=0.5,color_discrete_sequence=palette)
        st.plotly_chart(fig)

    with st.container():
        st.write('Lista das ações ROE com base no Preço justo')
        Acpj = Acpj.round(2)

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

        st.write('Lista das ações ROIC com base no Preço justo')


        Acpj_ROIC['Mrg. Seg.'] = (1 - (Acpj_ROIC['Cotação'] / Acpj_ROIC['PJ'])) * 100
        Acpj_ROIC = Acpj_ROIC[Acpj_ROIC['Mrg. Seg.'] > -5]
        Acpj_ROIC = Acpj_ROIC[['Papel', 'Cotação', 'PJ', 'Mrg. Seg.','Setor', 'Seg']].round(2)

        st.data_editor(
            Acpj_ROIC,
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

