import json
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
import os

# --- Cargar datos ---
df = pd.read_csv("info/mapa.csv", sep='|',encoding='latin1')
lineal1 = pd.read_csv("info/lineal.csv", sep='|',encoding='latin1')
df_ciudades = pd.read_csv("info/df_ciudades.csv", sep='|',encoding='latin1')
circular = pd.read_csv("info/circular.csv", sep='|',encoding='latin1')
apiladas = pd.read_csv("info/apiladas.csv", sep='|',encoding='latin1')
histogra = pd.read_csv("info/histogra.csv", sep='|',encoding='latin1')
tablita = pd.read_csv("info/tablita.csv", sep='|',encoding='latin1')

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

# --- Histograma AJUSTADO ---
# Ordenar por la columna de categoría para mantener el orden lógico
histogra_ordenado = histogra.sort_values('categoria_edad')

fig_histograma = px.bar(
    histogra_ordenado,
    x="rango_edad",
    y="total_muertes",
    text="total_muertes",
    color="total_muertes",
    color_continuous_scale="Blues",
    title="Distribución de muertes por grupo de edad",
    category_orders={"rango_edad": [
        "60 a 84 años",
        "85 a 100+ años", 
        "45 a 59 años",
        "30 a 44 años",
        "20 a 29 años",
        "Menor de 1 mes",
        "15 a 19 años",
        "1 a 11 meses",
        "5 a 14 años",
        "1 a 4 años",
        "Sin información"
    ]}
)
fig_histograma.update_traces(textposition="outside")
fig_histograma.update_layout(
    title_x=0.5,
    paper_bgcolor="#e6f2ff",  # Fondo pastel azul
    plot_bgcolor="#ffffff",
    xaxis_title="Rango de Edad",
    yaxis_title="Total de Muertes",
    xaxis_tickangle=-45  # Rotar etiquetas para mejor legibilidad
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
texto_mapa = """Mapa coroplético que muestra la distribución geográfica de muertes por departamento en Colombia (2019). 

CARACTERÍSTICAS:
• Tonos oscuros = Mayor concentración de casos
• Tonos claros = Menor concentración de casos

DEPARTAMENTOS CON MAYOR MORTALIDAD:
• Bogotá D.C.: más de 38,000 muertes
• Antioquia: 34,473 muertes  
• Valle del Cauca: 28,443 muertes

Los departamentos con menor densidad poblacional (Vaupés, Guainía, Amazonas) registran las cifras más bajas."""

texto_lineal = """El gráfico de líneas muestra la variación mensual en el número de muertes durante 2019. Se observan fluctuaciones a lo largo del año,
 con ciertos picos que pueden asociarse a factores estacionales, climáticos o coyunturales. Este tipo de análisis permite detectar tendencias
   temporales que podrían orientar acciones preventivas o de salud pública."""
texto_barras = """Esta visualización presenta las cinco ciudades con mayor número de homicidios, considerando los códigos de causa X95 (agresión con
 disparo de arma de fuego) y casos no especificados. El gráfico permite identificar los principales focos de violencia letal en el país, mostrando 
 contrastes claros entre zonas urbanas y regiones intermedias, y resaltando la importancia de políticas de seguridad diferenciadas por territorio."""
texto_circular = """El gráfico circular muestra las diez ciudades con menor número de muertes registradas durante 2019. Cada sector representa el
 aporte porcentual de cada ciudad al total nacional. Esta visualización permite reconocer los municipios con mejores indicadores de mortalidad, 
 que pueden servir como referencia para el diseño de estrategias de bienestar y prevención."""
texto_apiladas = """En este gráfico se comparan las muertes de hombres y mujeres en cada departamento. La estructura apilada permite visualizar
 simultáneamente la participación de ambos sexos y las diferencias relativas entre regiones. Se observa que, en la mayoría de los departamentos, 
 los hombres presentan tasas de mortalidad superiores, en especial en zonas con alta incidencia de violencia o accidentes."""
texto_histograma = """histograma agrupa las muertes según los rangos definidos en la variable GRUPO_EDAD1, permitiendo analizar la mortalidad a 
lo largo del ciclo de vida. La visualización muestra una clara concentración en los grupos de edad avanzada, coherente con el perfil epidemiológico 
nacional, aunque también se identifican picos en edades jóvenes asociados a causas externas o violentas."""

texto_tabla = """Esta tabla resume las diez principales causas de muerte en el país durante 2019, mostrando su código,
 el nombre de la causa y el número total de casos. El orden descendente facilita identificar los factores que más contribuyen
   a la mortalidad general, entre los que suelen destacar enfermedades cardiovasculares, respiratorias y ciertos tipos de cáncer.
     Este análisis es clave para priorizar políticas de salud pública."""

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
                html.P(texto_mapa, style={"whiteSpace": "pre-line", "textAlign": "justify", "lineHeight": "1.6"})
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