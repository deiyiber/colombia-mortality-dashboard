import pandas as pd

def quitar_tildes(texto):
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'}
    if isinstance(texto, str):
        for acento, sin_acento in reemplazos.items():
            texto = texto.replace(acento, sin_acento)
    return texto
def cargar_archivos():
    

    muerte = pd.read_csv("info/NoFetal2019.csv", sep=';')
    cod = pd.read_csv("info/CodigosDeMuerte.csv", sep=';')
    pola = pd.read_csv("info/Divipola.csv", sep=';')


    muerte.columns=muerte.columns.str.lower()
    cod.columns=cod.columns.str.lower()
    pola.columns=pola.columns.str.lower()
    muerte.columns=muerte.columns.str.replace(' ','_')
    cod.columns=cod.columns.str.replace(' ','_')
    pola.columns=pola.columns.str.replace(' ','_')

    cod=cod[['capítulo', 'nombre_capítulo', 'código_de_la_cie-10_tres_caracteres',
        'descripción__de_códigos_mortalidad_a_tres_caracteres',
        'código_de_la_cie-10_cuatro_caracteres',
        'descripcion__de_códigos_mortalidad_a_cuatro_caracteres']]
    muerte.columns = [quitar_tildes(col) for col in muerte.columns]
    muerte = muerte.map(quitar_tildes)
    cod.columns = [quitar_tildes(col) for col in cod.columns]
    cod = cod.map(quitar_tildes)
    pola.columns = [quitar_tildes(col) for col in pola.columns]
    pola = pola.map(quitar_tildes)
    return muerte, cod, pola

def data_mapa():
    Mapa=muerte[muerte['ano']==2019]
    dp=pola[['cod_departamento','departamento']].drop_duplicates()
    Mapa= pd.merge(Mapa,dp, on='cod_departamento', how='inner')
    Mapa=pd.DataFrame(Mapa['departamento'].value_counts()).reset_index()
    Mapa['anio']=2019
    Mapa=Mapa.rename(columns={'count':'cantidad_muertes'})
    Mapa['departamento'] = Mapa['departamento'].str.title()
    Mapa['departamento']=Mapa['departamento'].str.replace(',','')
    return Mapa

### Preparar copias de trabajo y unir bases

def preparar_datos(muerte, cod, pola):
    """Crea copias de las bases y las une con los códigos y municipios."""
    muerte_proc = muerte.copy()
    cod_proc = cod.copy()
    pola_proc = pola.copy()

    # --- Unir las bases (codigos y divipola) ---
    muerte_proc = muerte_proc.merge(
    cod_proc[['codigo_de_la_cie-10_tres_caracteres',
              'descripcion__de_codigos_mortalidad_a_tres_caracteres']],
    left_on='cod_muerte',
    right_on='codigo_de_la_cie-10_tres_caracteres',
    how='left')
    
    muerte_proc = muerte_proc.merge(
    pola_proc[['cod_municipio', 'municipio', 'departamento', 'cod_departamento']],
    on='cod_municipio',
    how='left')
    return muerte_proc

### Visualización de las 5 ciudades más violentas de Colombia, considerando homicidios 
### (códigos X95, agresión con disparo de armas de fuego y casos no especificados).

def grafico_barras():
    """Devuelve las 5 ciudades con más homicidios (X95)."""
    violencia = muerte_proc[muerte_proc['cod_muerte'].str.startswith('X95', na=False)]

    violencia_ciudad = (
        violencia.groupby('municipio')
        .size()
        .reset_index(name='total_homicidios')
        .sort_values('total_homicidios', ascending=False)
    )

    top5 = violencia_ciudad.head(5)
    #print(" Ciudades más violentas (códigos X95):")
    #print(top5)
    return top5

# Muestra las 10 ciudades con menor índice de mortalidad.

def grafico_circular():
    """Devuelve las 10 ciudades con menor cantidad total de muertes."""
    mortalidad_ciudad = (
        muerte_proc.groupby('municipio')
        .size()
        .reset_index(name='total_muertes')
        .sort_values('total_muertes', ascending=True)
    )

    ciudadesmenor = mortalidad_ciudad.head(10)
    #print("\n Ciudades con menor mortalidad:")
    #print(ciudadesmenor)
    return ciudadesmenor

###  Listado de las 10 principales causas de muerte en Colombia, 
# incluyendo su código, nombre y total de casos (ordenadas de mayor a menor).
def tabla():
    muerte_proc = muerte.copy()
    cod_proc = cod.copy()
    pola_proc = pola.copy()

    # Unir códigos de muerte para obtener descripción
    muerte_proc = muerte_proc.merge(
        cod_proc[['codigo_de_la_cie-10_tres_caracteres',
                'descripcion__de_codigos_mortalidad_a_tres_caracteres']],
        left_on='cod_muerte',
        right_on='codigo_de_la_cie-10_tres_caracteres',
        how='left')

    # Agrupar por código y descripción, contar casos
    top10_causas = (
        muerte_proc.groupby(['cod_muerte', 'descripcion__de_codigos_mortalidad_a_tres_caracteres'])
        .size()
        .reset_index(name='total_casos')
        .sort_values('total_casos', ascending=False)
        .head(10))
    #print(" 10 principales causas de muerte en Colombia:")
    #print(top10_causas)
    return top10_causas

### Comparación del total de muertes por sexo en cada departamento, 
# para analizar diferencias significativas entre géneros.

def grafico_apiladas():
    pola_proc = pola.copy()

    muerte_sexo = muerte.merge(
        pola_proc[['cod_departamento', 'departamento']],
        on='cod_departamento',
        how='left'
    )

    # Agrupar por departamento y sexo
    muertes_por_sexo = (
        muerte_sexo.groupby(['departamento', 'sexo'])
        .size()
        .reset_index(name='total_muertes')
    )

    #print("\n Total de muertes por sexo y departamento:")
    #print(muertes_por_sexo.head(10))
    return muertes_por_sexo
 
def histograma():
    """Agrupa las muertes por categorías de edad según los códigos DANE y muestra su rango descriptivo."""
    muerte_proc = muerte.copy()

    # --- Diccionario con los rangos DANE y descripciones ---
    rangos_edad = {
        "Mortalidad neonatal": {"codigos": range(0, 5), "rango": "Menor de 1 mes"},
        "Mortalidad infantil": {"codigos": range(5, 7), "rango": "1 a 11 meses"},
        "Primera infancia": {"codigos": range(7, 9), "rango": "1 a 4 años"},
        "Niñez": {"codigos": range(9, 11), "rango": "5 a 14 años"},
        "Adolescencia": {"codigos": [11], "rango": "15 a 19 años"},
        "Juventud": {"codigos": range(12, 14), "rango": "20 a 29 años"},
        "Adultez temprana": {"codigos": range(14, 17), "rango": "30 a 44 años"},
        "Adultez intermedia": {"codigos": range(17, 20), "rango": "45 a 59 años"},
        "Vejez": {"codigos": range(20, 25), "rango": "60 a 84 años"},
        "Longevidad / Centenarios": {"codigos": range(25, 29), "rango": "85 a 100+ años"},
        "Edad desconocida": {"codigos": [29], "rango": "Sin información"}
    }

    # --- Función auxiliar para clasificar cada código ---
    def clasificar_grupo(cod):
        try:
            codigo = int(cod)
        except (ValueError, TypeError):
            return "Edad desconocida"
        for categoria, info in rangos_edad.items():
            if codigo in info["codigos"]:
                return categoria
        return "Edad desconocida"

    # --- Aplicar clasificación ---
    muerte_proc["categoria_edad"] = muerte_proc["grupo_edad1"].apply(clasificar_grupo)

    # --- Agrupar por categoría ---
    dist_edad = (
        muerte_proc.groupby("categoria_edad")
        .size()
        .reset_index(name="total_muertes")
        .sort_values("total_muertes", ascending=False)
    )

    # --- Agregar el rango de edad descriptivo ---
    dist_edad["rango_edad"] = dist_edad["categoria_edad"].map(lambda c: rangos_edad[c]["rango"])

    #print("\n Distribución de muertes por categoría y rango de edad:")
    #print(dist_edad[["categoria_edad", "rango_edad", "total_muertes"]])
    return dist_edad

def grafico_lineal():
    """Devuelve el total de muertes por mes en Colombia."""
    if 'mes' not in muerte_proc.columns:
        raise KeyError("El DataFrame no contiene la columna 'mes'.")

    muertes_mes = (
        muerte_proc.groupby('mes')
        .size()
        .reset_index(name='total_muertes')
        .sort_values('mes')    )

    #print("\n Total de muertes por mes:")
    #print(muertes_mes)
    return muertes_mes
 

global muerte, cod, pola, muerte_proc
muerte, cod, pola =cargar_archivos()
muerte_proc = preparar_datos(muerte, cod, pola)