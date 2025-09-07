import dash
from dash import html, dcc, callback, Input, Output
from urllib.parse import parse_qs, urlparse
from joblib import load
import pandas as pd
import dash_mantine_components as dmc

from utils import predictor

#preparamos la predicción
modelo_LGBM_M1 = load("modelo_reentrenado/LGBM/LGBM_m1.joblib")
modelo_LGBM_M2 = load("modelo_reentrenado/LGBM/LGBM_m2.joblib")
modelo_LGBM_residuo = load("modelo_reentrenado/LGBM/LGBM_residuo.joblib")

modelo_XGboost_M1 = load("modelo_reentrenado/XG_boost/XG_boost_m1.joblib")
modelo_XGboost_M2 = load("modelo_reentrenado/XG_boost/XG_boost_m2.joblib")
modelo_XGboost_residuo = load("modelo_reentrenado/XG_boost/XG_boost_residuo.joblib")

dia_inicio = "13/08/2025" #esta es la ultima fecha donde tengo datos
fecha_predecir = "19/08/2025" #dia de referencia de la semana que quiero predecir
fecha_predecir = pd.to_datetime(fecha_predecir,format='%d/%m/%Y')
dia_inicio = pd.to_datetime(dia_inicio,format='%d/%m/%Y')
dia_predicho = dia_inicio 

def prediccion(numero_semanas):
    prediccion_LGBM,fecha1 = predictor(numero_semanas=numero_semanas,
                                modelo_1=modelo_LGBM_M1,
                                modelo_2=modelo_LGBM_M2,
                                modelo_residuo=modelo_LGBM_residuo, 
                                dia_predicho=dia_predicho)
    
    prediccion_XGboost,fecha2= predictor(numero_semanas=numero_semanas,
                                   modelo_1=modelo_XGboost_M1,
                                   modelo_2=modelo_XGboost_M2,
                                   modelo_residuo=modelo_XGboost_residuo,
                                   dia_predicho=dia_predicho)
    #usamos parametros hallados en el modelado con el ensemble a traves de PSO-CS
    prediccion_final = (0.84493549*prediccion_XGboost +
                0.15506451*prediccion_LGBM
                )
    return round(prediccion_final,2), fecha1

#dash.register_page(__name__, path="/prediccion-barranquilla", name="prediccion")
numero_semanas = {"4 semanas":4 ,"8 semanas":8, "12 semanas":12 ,"16 semanas": 16 ,"24 semanas":24}

import dash
from dash import html, Input, Output
from dash import dcc
from urllib.parse import urlparse, parse_qs

dash.register_page(__name__, path="/prediccion")

layout = html.Div([
    html.H2("Página de predicción"),
    dcc.Location(id="url-prediccion"),  # para leer parámetros
    html.Div(id="resultado-prediccion")
])

@dash.callback(
    Output("resultado-prediccion", "children"),
    Input("url-prediccion", "href")
)
def mostrar_prediccion(href):
    if href is None:
        return "Esperando selección..."
    query = parse_qs(urlparse(href).query)
    semanas = query.get("semanas", ["?"])[0]
    
    # 🔽 Aquí puedes correr tu lógica de predicción real
    valor_predicho, fecha_predicha = prediccion(numero_semanas=numero_semanas[semanas])
    print(valor_predicho)
    dia_predicho = fecha_predicha.day
    mes_predicho = fecha_predicha.month_name(locale="es_ES.utf8")
    año_predicho = fecha_predicha.year
    return html.Div([
        html.P(f"se predijeron  {numero_semanas[semanas]} semanas"),
        dmc.Stack(
            children=[ 
                html.H1("Fecha"),
                dmc.Box(f"{dia_predicho} de {mes_predicho} de {año_predicho}"),
                html.H1("Valor predicho"),
                dmc.Box([
                valor_predicho
                ],
                mt=8, p=24)],
        )
    ])