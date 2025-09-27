import dash
from dash import Dash, html, dcc, callback, Output, Input
from dash import html, dcc
import dash_mantine_components as dmc
from dash import dash_table
import pandas as pd
import numpy as np
import plotly.express as px
from joblib import load

from utils import modo_1_actualizado
from utils import modo_2_actualizado
from utils import residuo_actualizado

from utils import predictor , prediccion

dash.register_page(__name__, path="/", name="Inicio")

#preparamos la predicción
modelo_LGBM_M1 = load("modelo_reentrenado/LGBM/LGBM_m1.joblib")
modelo_LGBM_M2 = load("modelo_reentrenado/LGBM/LGBM_m2.joblib")
modelo_LGBM_residuo = load("modelo_reentrenado/LGBM/LGBM_residuo.joblib")

modelo_XGboost_M1 = load("modelo_reentrenado/XG_boost/XG_boost_m1.joblib")
modelo_XGboost_M2 = load("modelo_reentrenado/XG_boost/XG_boost_m2.joblib")
modelo_XGboost_residuo = load("modelo_reentrenado/XG_boost/XG_boost_residuo.joblib")

precios = modo_1_actualizado + modo_2_actualizado + residuo_actualizado
precios.rename(columns={"PROMEDIO":"Precio"},inplace=True)

decodificador = {"1 semana": 1,"4 semanas":4 ,"8 semanas":8, "12 semanas":12 ,"16 semanas": 16 ,"24 semanas":24}

fig = px.line(precios, x=precios.index, y="Precio", title="Precios del maíz granabastos")
numero_semanas = ["1 semana","4 semanas","8 semanas","12 semanas","16 semanas","24 semanas"]

layout = dmc.MantineProvider(

    dmc.Container([

        dmc.Group([
            html.H1("Predicción de precios de maíz"),
        ]),
        dmc.Grid([
            dmc.GridCol(
                children=[
                dcc.Graph(
                    id="precios-maiz-granabastos",
                    figure=fig,
                    style={"width": "100%", "height": "500px"})
                    ], span=8 ),
            dmc.GridCol(
                children=[
                dmc.Text("¿Cuántas semanas quieres predecir?", size="sm", fw=500),
                dcc.Dropdown(numero_semanas,"",id="seleccion-semanas"),
                html.Div(id="resultado-prediccion")
                ],span=4,
                #style={"marginTop": "100px"}
            ),
                ])],size="lg" ))

@callback(
    Output("precios-maiz-granabastos", "figure"),
    Output("resultado-prediccion", "children"),
    Input("seleccion-semanas", "value")
)
def actualizar_prediccion(semanas):
    if semanas is None:
        raise dash.exceptions.PreventUpdate
    
    # Generar nueva figura con las predicciones
    valor_predicho, fecha_predicha, datos_predicciones = prediccion(numero_semanas=decodificador[semanas])
    dia_predicho = fecha_predicha.day
    mes_predicho = fecha_predicha.month_name(locale="es_ES.utf8")
    año_predicho = fecha_predicha.year

    #Graficamos
    fig = px.line(precios, x=precios.index, y="Precio", title="Precios del maíz granabastos")
    fig.add_scatter(x=datos_predicciones["fecha"], y=datos_predicciones["Precio"],
                mode="lines", name="Predicción")

    # Formatear salida debajo del dropdown
    valor_formateado = f"{valor_predicho:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    resultado = dmc.Stack(
                        children=[ 
                            html.H3("Fecha"),
                            dmc.Button(f"{dia_predicho} de {mes_predicho} de {año_predicho}"),
                            html.H3("Precio"),
                            dmc.Button(valor_formateado),
                        ],
                    )
    return fig, resultado