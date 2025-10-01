from dash import Dash, html, dcc, callback, Output, Input
import dash
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
import os 

app = Dash(__name__, suppress_callback_exceptions=True,use_pages=True)
server = app.server 

# Dash frontend
app.layout = dmc.MantineProvider(

    dmc.Container([
        dash.page_container,

        ],size="lg" ))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)