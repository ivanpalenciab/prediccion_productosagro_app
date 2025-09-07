from dash import Dash, html, dcc, callback, Output, Input
import dash
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd

from utils import modo_1_actualizado
from utils import modo_2_actualizado
from utils import residuo_actualizado

precios = modo_1_actualizado + modo_2_actualizado + residuo_actualizado

fig = px.line(precios, x=precios.index, y="PROMEDIO", title="Precios del maíz granabastos")

app = Dash(__name__, suppress_callback_exceptions=True,use_pages=True)
server = app.server 

# Dash frontend
numero_semanas = ["4 semanas","8 semanas","12 semanas","16 semanas","24 semanas"]

app.layout = dmc.MantineProvider(

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
                dcc.Dropdown(numero_semanas,"Seleccione el numero de semanas",id="seleccion-semanas")
                ],span=4,
                #style={"marginTop": "100px"}
            ),
                  dcc.Location(id="url", refresh=True),
                 dash.page_container
                ])],size="lg" ))
        
@app.callback(
    Output("url", "href"),
    Input("seleccion-semanas", "value"),
    prevent_initial_call=True
)
def ir_a_prediccion(valor):
    if valor is None:
        return dash.no_update
    return f"/prediccion?semanas={valor}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)