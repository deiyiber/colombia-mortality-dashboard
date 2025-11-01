import json
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
#import process as datos
import os

# --- Datos del mapa ---
#df = datos.data_mapa()
df =pd.read_csv("info/mapa.csv",sep='|')
# --- Datos del gráfico de lineal ---
lineal1=pd.read_csv("info/lineal.csv",sep='|')
# --- Datos del gráfico de barras ---
df_ciudades = pd.read_csv("info/df_ciudades.csv",sep='|')
# --- Datos del gráfico circular ---
circular = pd.read_csv("info/circular.csv",sep='|')
# --- Datos del gráfico apilado ---
apiladas = pd.read_csv("info/apiladas.csv",sep='|')
# --- Datos del histograma ---
histogra = pd.read_csv("info/histogra.csv",sep='|')
# --- Datos de la tabla ---
tablita = pd.read_csv("info/tablita.csv",sep='|')
# --- Cargar GeoJSON local ---

with open("departamentos_colombia.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

# --- Mapa de calor por departamento ---
fig_mapa = px.choropleth_mapbox(
    df,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.name",
    color="cantidad_muertes",
    mapbox_style="open-street-map",
    zoom=5,
    center={"lat": 4.5, "lon": -74.1}
)
fig_mapa.update_layout(
    title=dict(
        text="Distribución total de muertes por departamento en Colombia (2019)",
        x=0.5, xanchor='center'
    ),
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    paper_bgcolor="white"
)
# --- Gráfico de líneas ---
fig_lineal = px.line(
    lineal1,
    x="mes",
    y="total_muertes",
    markers=True,
    title="Tendencia mensual de muertes",
    line_shape="linear"
)
fig_lineal.update_traces(line=dict(width=3), marker=dict(size=8))
fig_lineal.update_layout(
    xaxis_title="Mes",
    yaxis_title="Total de muertes",
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_x=0.5
)
# --- Gráfico de barras ---
fig_barras = px.bar(
    df_ciudades.sort_values(by="total_homicidios", ascending=False),
    x="municipio",
    y="total_homicidios",
    text="total_homicidios",
    color="total_homicidios",
    color_continuous_scale="Reds",
    title="Ciudades más violentas"
)
fig_barras.update_traces(textposition='outside')
fig_barras.update_layout(
    xaxis_title="Municipio",
    yaxis_title="Total de homicidios",
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_x=0.5
)
# --- Gráfico circular ---
fig_circular = px.pie(
    circular,
    names="municipio",
    values="total_muertes",
    title="Ciudades con menor índice de mortalidad",
    color_discrete_sequence=px.colors.sequential.Reds
)
fig_circular.update_traces(textposition='inside', textinfo='percent+label')
fig_circular.update_layout(title_x=0.5)
# --- Gráfico de barras apiladas ---
fig_apiladas = px.bar(
    apiladas,
    x="departamento",
    y="total_muertes",
    color="sexo",
    title="Muertes por Departamento y Sexo",
    text="total_muertes",
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_apiladas.update_traces(textposition='inside')
fig_apiladas.update_layout(
    barmode="stack",
    xaxis_title="Departamento",
    yaxis_title="Total de muertes",
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_x=0.5
)
# --- Histograma (por grupos de edad) ---
fig_histograma = px.bar(
    histogra.sort_values(by="grupo_edad1"),
    x="grupo_edad1",
    y="total_muertes",
    text="total_muertes",
    color="total_muertes",
    color_continuous_scale="Reds",
    title="Distribución de muertes por grupo de edad"
)
fig_histograma.update_traces(textposition="outside")
fig_histograma.update_layout(
    xaxis_title="Grupo de edad",
    yaxis_title="Total de muertes",
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_x=0.5
)
# --- Tabla de datos ---
tabla_dash = dash_table.DataTable(
    columns=[
        {"name": "Código de Muerte", "id": "cod_muerte"},
        {"name": "Descripción de códigos mortalidad (3 caracteres)", "id": "descripcion__de_codigos_mortalidad_a_tres_caracteres"},
        {"name": "Total de casos", "id": "total_casos"}
    ],
    data=tablita.to_dict("records"),
    style_table={
        "overflowX": "auto",
        "border": "1px solid #ccc",
        "maxHeight": "500px",
        "overflowY": "auto"
    },
    style_header={
        "backgroundColor": "#f8f9fa",
        "fontWeight": "bold",
        "textAlign": "center"
    },
    style_cell={
        "textAlign": "center",
        "padding": "8px",
        "whiteSpace": "normal",
        "height": "auto"
    },
    page_size=10
)

# --- App Dash ---
app = Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H2("Mapa de muertes por departamento - 2019", style={"textAlign": "center"}),
    # Mapa
    dcc.Graph(figure=fig_mapa, style={"height": "70vh"}),
    html.Hr(),
    dcc.Graph(figure=fig_lineal, style={"height": "70vh"}),
    html.Hr(),
    # Gráfico de barras
    dcc.Graph(figure=fig_barras, style={"height": "70vh"}),
    html.Hr(),
    # Gráfico circular
    dcc.Graph(figure=fig_circular, style={"height": "70vh"}),
    html.Hr(),
    # Gráfico de barras apiladas
    dcc.Graph(figure=fig_apiladas, style={"height": "70vh"}),
    html.Hr(),
    # Histograma
    dcc.Graph(figure=fig_histograma, style={"height": "70vh"}),
    html.Hr(),
    # Tabla
    html.H3("Códigos de mortalidad - Casos registrados", style={"textAlign": "center", "marginTop": "30px"}),
    tabla_dash
])

#if __name__ == "__main__":
##   app.run(debug=True)
