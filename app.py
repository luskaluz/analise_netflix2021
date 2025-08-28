import pandas as pd 
import streamlit as st 
import matplotlib.pyplot as plt 
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go 
 
st.set_page_config( 
    page_title="Dashboard de Streaming", 
    page_icon="📊", 
    layout="wide", 
) 
 
# Carregar o dataset 
@st.cache_data 
def load_data(): 
    df = pd.read_csv('netflix_titles.csv') 
    return df 
 
df = load_data() 
 
st.sidebar.header("Filtros") 
 
# Limpeza de dados 
df['listed_in'] = df['listed_in'].str.replace('&', ',', regex=False) 
 
# Separar filmes e séries 
df_movies = df[df['type'] == 'Movie'].copy() 
df_tv_shows = df[df['type'] == 'TV Show'].copy() 
 
# Obter gêneros individuais para filmes (excluindo 'International')
generos_filmes_individuais = df_movies[~df_movies['listed_in'].str.contains('International', na=False)]['listed_in'].str.split(', ').explode().dropna().unique()
generos_filmes_individuais = sorted([gen for gen in generos_filmes_individuais if gen.strip()])

# Obter gêneros individuais para séries
generos_series_individuais = df_tv_shows['listed_in'].str.split(', ').explode().dropna().unique()
generos_series_individuais = sorted([gen for gen in generos_series_individuais if gen.strip()])

# Filtros com subheaders
st.sidebar.subheader("Filtro de Gênero de Filmes")
genfilme_selecionados = st.sidebar.multiselect(
    "Selecione os gêneros de filmes:", 
    generos_filmes_individuais, 
    default=generos_filmes_individuais
)

st.sidebar.subheader("Filtro de Gênero de Séries")
gentv_selecionados = st.sidebar.multiselect(
    "Selecione os gêneros de séries:", 
    generos_series_individuais, 
    default=generos_series_individuais
)

# Aplicar filtros
if genfilme_selecionados:
    df_movies_filtered = df_movies[df_movies['listed_in'].str.contains('|'.join(genfilme_selecionados), na=False)]
else:
    df_movies_filtered = df_movies

if gentv_selecionados:
    df_tv_shows_filtered = df_tv_shows[df_tv_shows['listed_in'].str.contains('|'.join(gentv_selecionados), na=False)]
else:
    df_tv_shows_filtered = df_tv_shows

st.header('Gêneros Mais Populares') 

# MÉTRICAS PRINCIPAIS
st.header('📊 Métricas Principais')

# Calcular métricas com base nos filtros aplicados
total_filmes = len(df_movies_filtered)
total_series = len(df_tv_shows_filtered)

# Para média, consideramos apenas países informados
paises_unicos_filmes = df_movies_filtered['country'].str.split(', ').explode().dropna().nunique()
paises_unicos_series = df_tv_shows_filtered['country'].str.split(', ').explode().dropna().nunique()

media_filmes = total_filmes / paises_unicos_filmes if paises_unicos_filmes > 0 else 0
media_series = total_series / paises_unicos_series if paises_unicos_series > 0 else 0

# País com maior quantidade (apenas entre os países informados)
paises_filmes_count = df_movies_filtered['country'].str.split(', ').explode().dropna().value_counts()
pais_mais_filmes = paises_filmes_count.index[0] if not paises_filmes_count.empty else "N/A"
qtd_filmes_pais_top = paises_filmes_count.iloc[0] if not paises_filmes_count.empty else 0

paises_series_count = df_tv_shows_filtered['country'].str.split(', ').explode().dropna().value_counts()
pais_mais_series = paises_series_count.index[0] if not paises_series_count.empty else "N/A"
qtd_series_pais_top = paises_series_count.iloc[0] if not paises_series_count.empty else 0

# Gênero mais popular (apenas entre os gêneros informados)
generos_filmes_count = df_movies_filtered[df_movies_filtered['listed_in'].notna()]['listed_in'].str.split(', ').explode().value_counts()
# Excluir 'International' dos filmes
generos_filmes_count = generos_filmes_count[~generos_filmes_count.index.str.contains('International', na=False)]
genero_mais_popular_filmes = generos_filmes_count.index[0] if not generos_filmes_count.empty else "N/A"

generos_series_count = df_tv_shows_filtered[df_tv_shows_filtered['listed_in'].notna()]['listed_in'].str.split(', ').explode().value_counts()
generos_series_count = generos_series_count[~generos_series_count.index.str.contains('International TV Shows', na=False)]
genero_mais_popular_series = generos_series_count.index[0] if not generos_series_count.empty else "N/A"

# Layout das métricas em 4 colunas
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        label="📽️ Total de Filmes",
        value=f"{total_filmes:,}",
        help="Total de filmes com os filtros aplicados"
    )
    st.metric(
        label="📺 Total de Séries",
        value=f"{total_series:,}",
        help="Total de séries com os filtros aplicados"
    )

with col_m2:
    st.metric(
        label="📊 Média Filmes/País",
        value=f"{media_filmes:.1f}",
        help="Média de filmes por país"
    )
    st.metric(
        label="📊 Média Séries/País",
        value=f"{media_series:.1f}",
        help="Média de séries por país"
    )

with col_m3:
    st.metric(
        label="🏆 País com + Filmes",
        value=pais_mais_filmes,
        delta=f"{qtd_filmes_pais_top} filmes",
        help="País com maior quantidade de filmes"
    )
    st.metric(
        label="🏆 País com + Séries",
        value=pais_mais_series,
        delta=f"{qtd_series_pais_top} séries",
        help="País com maior quantidade de séries"
    )

with col_m4:
    st.metric(
        label="🎭 Gênero + Popular entre Filmes",
        value=genero_mais_popular_filmes,
        help="Gênero mais popular entre filmes"
    )
    st.metric(
        label="🎭 Gênero + Popular entre Séries",
        value=genero_mais_popular_series,
        help="Gênero mais popular entre séries excluindo o gênero Internacional"
    )

st.divider()

st.header('Gêneros Mais Populares') 
 
# Top 10 Gêneros de Filmes (com filtro aplicado)
generos_filmes = df_movies_filtered[~df_movies_filtered['listed_in'].str.contains('International', na=False)]['listed_in'].str.split(', ').explode() 
top10_filmes = generos_filmes.value_counts().head(10) 
 
# Top 10 Gêneros de Séries (com filtro aplicado)
generos_series = df_tv_shows_filtered['listed_in'].str.split(', ').explode() 
top10_series = generos_series.value_counts().head(10) 
 
# Layout lado a lado 
col1, col2 = st.columns(2) 
 
with col1: 
    st.subheader("Top 10 Gêneros de Filmes")
    if not top10_filmes.empty:
        fig1, ax1 = plt.subplots(figsize=(6, 4)) 
        sns.barplot(x=top10_filmes.values, y=top10_filmes.index, ax=ax1, palette='viridis') 
        ax1.set_title('Top 10 Gêneros de Filmes') 
        st.pyplot(fig1)
    else:
        st.write("Nenhum filme encontrado com os filtros selecionados.")
 
with col2: 
    st.subheader("Top 10 Gêneros de Séries de TV")
    if not top10_series.empty:
        fig2, ax2 = plt.subplots(figsize=(6, 4)) 
        sns.barplot(x=top10_series.values, y=top10_series.index, ax=ax2, palette='plasma') 
        ax2.set_title('Top 10 Gêneros de Séries de TV') 
        st.pyplot(fig2)
    else:
        st.write("Nenhuma série encontrada com os filtros selecionados.")

# Gráfico de Filmes e Séries por País
st.header('Distribuição por Países')

# Obter contagem de países para filmes
paises_filmes = df_movies_filtered['country'].str.split(', ').explode().dropna()
contagem_paises_filmes = paises_filmes.value_counts().reset_index()
contagem_paises_filmes.columns = ['country', 'count']

# Obter contagem de países para séries
paises_series = df_tv_shows_filtered['country'].str.split(', ').explode().dropna()
contagem_paises_series = paises_series.value_counts().reset_index()
contagem_paises_series.columns = ['country', 'count']

# Mapas choropleth
col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribuição Mundial - Filmes")
    if not contagem_paises_filmes.empty:
        fig_map_filmes = px.choropleth(
            contagem_paises_filmes,
            locations='country',
            color='count',
            hover_name='country',
            hover_data={'count': True},
            color_continuous_scale='Blues',
            locationmode='country names',
            title='Número de Filmes por País',
            labels={'count': 'Quantidade de Filmes'}
        )
        fig_map_filmes.update_layout(
            height=500,
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
        )
        st.plotly_chart(fig_map_filmes, use_container_width=True)
    else:
        st.write("Nenhum dado de país encontrado para filmes.")

with col4:
    st.subheader("Distribuição Mundial - Séries")
    if not contagem_paises_series.empty:
        fig_map_series = px.choropleth(
            contagem_paises_series,
            locations='country',
            color='count',
            hover_name='country',
            hover_data={'count': True},
            color_continuous_scale='Oranges',
            locationmode='country names',
            title='Número de Séries por País',
            labels={'count': 'Quantidade de Séries'}
        )
        fig_map_series.update_layout(
            height=500,
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
        )
        st.plotly_chart(fig_map_series, use_container_width=True)
    else:
        st.write("Nenhum dado de país encontrado para séries.")

# Ranking dos Top 10 países (complementar aos mapas)
st.subheader("Ranking dos Top 10 Países")
col5, col6 = st.columns(2)

with col5:
    if not contagem_paises_filmes.empty:
        st.write("**Top 10 Países - Filmes**")
        top10_filmes_ranking = contagem_paises_filmes.head(10)
        for i, row in top10_filmes_ranking.iterrows():
            st.write(f"{i+1}. {row['country']}: {row['count']} filmes")

with col6:
    if not contagem_paises_series.empty:
        st.write("**Top 10 Países - Séries**")
        top10_series_ranking = contagem_paises_series.head(10)
        for i, row in top10_series_ranking.iterrows():
            st.write(f"{i+1}. {row['country']}: {row['count']} séries")
