import json
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
import os

# --- Cargar datos ---
df = pd.read_csv("info/mapa.csv", sep='|')
lineal1 = pd.read_csv("info/lineal.csv", sep='|')
df_ciudades = pd.read_csv("info/df_ciudades.csv", sep='|')
circular = pd.read_csv("info/circular.csv", sep='|')
apiladas = pd.read_csv("info/apiladas.csv", sep='|')
histogra = pd.read_csv("info/histogra.csv", sep='|')
tablita = pd.read_csv("info/tablita.csv", sep='|')

# --- GeoJSON ---
with open("departamentos_colombia.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

# --- Mapa ---
fig_mapa = px.choropleth_mapbox(
    df,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.name",
    color="cantidad_muertes",
    mapbox_style="open-street-map",
    zoom=5,
    color_continuous_scale="Blues",
    center={"lat": 4.5, "lon": -74.1},
    title="Distribución total de muertes por departamento en Colombia (2019)"
)
fig_mapa.update_layout(
    title_x=0.5,
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    paper_bgcolor="#e6f2ff"  # Fondo pastel azul
)

# --- Gráfico de líneas ---
fig_lineal = px.line(
    lineal1,
    x="mes",
    y="total_muertes",
    markers=True,
    title="Tendencia mensual de muertes",
    line_shape="linear",
    color_discrete_sequence=["#0d47a1"]
)
fig_lineal.update_traces(line=dict(width=4), marker=dict(size=10, color="#1565c0"))
fig_lineal.update_layout(
    xaxis_title="Mes",
    yaxis_title="Total de muertes",
    title_x=0.5,
    paper_bgcolor="#e6f2ff",  # Fondo pastel azul
    plot_bgcolor="#ffffff"
)

# --- Gráfico de barras ---
fig_barras = px.bar(
    df_ciudades.sort_values(by="total_homicidios", ascending=False),
    x="municipio",
    y="total_homicidios",
    text="total_homicidios",
    color="total_homicidios",
    color_continuous_scale="Blues",
    title="Ciudades más violentas"
)
fig_barras.update_traces(textposition='outside')
fig_barras.update_layout(
    xaxis_title="Municipio",
    yaxis_title="Total de homicidios",
    title_x=0.5,
    paper_bgcolor="#e6f2ff",  # Fondo pastel azul
    plot_bgcolor="#ffffff"
)

# --- Circular ---
fig_circular = px.pie(
    circular,
    names="municipio",
    values="total_muertes",
    title="Ciudades con menor índice de mortalidad",
    color_discrete_sequence=px.colors.sequential.Blues
)
fig_circular.update_traces(textposition='inside', textinfo='percent+label')
fig_circular.update_layout(
    title_x=0.5,
    paper_bgcolor="#e6f2ff"  # Fondo pastel azul
)

# --- Barras apiladas ---
fig_apiladas = px.bar(
    apiladas,
    x="departamento",
    y="total_muertes",
    color="sexo",
    title="Muertes por Departamento y Sexo",
    text="total_muertes",
    color_discrete_sequence=px.colors.sequential.Blues
)
fig_apiladas.update_traces(textposition='inside')
fig_apiladas.update_layout(
    barmode="stack",
    title_x=0.5,
    paper_bgcolor="#e6f2ff",  # Fondo pastel azul
    plot_bgcolor="#ffffff"
)

# --- Histograma ---
fig_histograma = px.bar(
    histogra.sort_values(by="grupo_edad1"),
    x="grupo_edad1",
    y="total_muertes",
    text="total_muertes",
    color="total_muertes",
    color_continuous_scale="Blues",
    title="Distribución de muertes por grupo de edad"
)
fig_histograma.update_traces(textposition="outside")
fig_histograma.update_layout(
    title_x=0.5,
    paper_bgcolor="#e6f2ff",  # Fondo pastel azul
    plot_bgcolor="#ffffff"
)

# --- Tabla ---
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
        "overflowY": "auto",
        "width": "95%",
        "margin": "auto",
        "backgroundColor": "#f0f8ff"  # Fondo pastel azul claro
    },
    style_header={
        "backgroundColor": "#e3f2fd",
        "fontWeight": "bold",
        "textAlign": "center"
    },
    style_cell={
        "textAlign": "center",
        "padding": "8px",
        "whiteSpace": "normal",
        "height": "auto",
        "backgroundColor": "#f8fbff"
    },
    page_size=10
)

# --- Textos descriptivos personalizables ---
texto_mapa = "Mapa que muestra la distribución geográfica de las muertes por departamentos en Colombia. Los tonos más oscuros indican mayor cantidad de casos."
texto_lineal = "Gráfico lineal que muestra la evolución temporal de las muertes a lo largo de los meses del año 2019."
texto_barras = "Ranking de las ciudades con mayores índices de homicidios y violencia en Colombia durante 2019."
texto_circular = "Distribución porcentual de las muertes en las ciudades con menores índices de mortalidad."
texto_apiladas = "Desglose de muertes por departamento discriminado por sexo (masculino y femenino)."
texto_histograma = "Distribución de las muertes por grupos de edad, mostrando qué segmentos poblacionales fueron más afectados."
texto_tabla = "Tabla detallada con los códigos de mortalidad y su descripción correspondiente."

# --- App ---
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    style={
        "backgroundColor": "#e6f2ff",  # Fondo pastel azul para toda la app
        "fontFamily": "Arial, sans-serif",
        "padding": "20px"
    },
    children=[
        html.H1("Análisis de Mortalidad en Colombia - 2019",
                style={"textAlign": "center", "color": "#0d47a1", "marginTop": "20px"}),
        html.Hr(),

        # --- Mapa con texto ---
        html.Div([
            html.Div(dcc.Graph(figure=fig_mapa, style={"height": "70vh"}), 
                    style={"width": "70%", "display": "inline-block", "padding": "10px"}),
            html.Div([
                html.H3("Descripción del Mapa", style={"color": "#0d47a1"}),
                html.P(texto_mapa, style={"textAlign": "justify", "lineHeight": "1.6"})
            ], style={"width": "25%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"})
        ]),
        html.Hr(),

        # --- Línea + Barras ---
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_lineal, style={"height": "70vh"}),
                html.Div([
                    html.H4("Explicación Gráfico Lineal", style={"color": "#0d47a1"}),
                    html.P(texto_lineal, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            
            html.Div([
                dcc.Graph(figure=fig_barras, style={"height": "70vh"}),
                html.Div([
                    html.H4("Explicación Gráfico de Barras", style={"color": "#0d47a1"}),
                    html.P(texto_barras, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px"})
        ]),
        html.Hr(),

        # --- Circular + Apiladas ---
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_circular, style={"height": "70vh"}),
                html.Div([
                    html.H4("Explicación Gráfico Circular", style={"color": "#0d47a1"}),
                    html.P(texto_circular, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            
            html.Div([
                dcc.Graph(figure=fig_apiladas, style={"height": "70vh"}),
                html.Div([
                    html.H4("Explicación Barras Apiladas", style={"color": "#0d47a1"}),
                    html.P(texto_apiladas, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px"})
        ]),
        html.Hr(),

        # --- Histograma + Tabla ---
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_histograma, style={"height": "70vh"}),
                html.Div([
                    html.H4("Explicación Histograma", style={"color": "#0d47a1"}),
                    html.P(texto_histograma, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            
            html.Div([
                html.H3("Códigos de mortalidad - Casos registrados",
                        style={"textAlign": "center", "color": "#0d47a1", "marginBottom": "10px"}),
                tabla_dash,
                html.Div([
                    html.H4("Explicación Tabla", style={"color": "#0d47a1"}),
                    html.P(texto_tabla, style={"textAlign": "justify"})
                ], style={"padding": "15px"})
            ], style={"width": "48%", "display": "inline-block", "padding": "10px", "verticalAlign": "top"})
        ]),
        html.Hr(),

        # --- Autores ---
        html.Div([
            html.H4("Autores:", style={"textAlign": "center", "color": "#1565c0"}),
            html.P("Deiyiber Ducuara  |  Kiliam Alvarado",
                   style={"textAlign": "center", "color": "#0d47a1", "fontWeight": "bold"})
        ], style={"marginTop": "30px", "marginBottom": "20px"})
    ]
)


#if __name__ == "__main__":
##  app.run(debug=True)