from fastapi import APIRouter, HTTPException
from joblib import load
import pandas as pd
import xgboost as xgb

from src.utils import predictor

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

predecir = APIRouter()

@predecir.get("/predecir/{numero_semanas:int}")
async def prediccion(numero_semanas):
    prediccion_LGBM = predictor(numero_semanas=numero_semanas,
                                modelo_1=modelo_LGBM_M1,
                                modelo_2=modelo_LGBM_M2,
                                modelo_residuo=modelo_LGBM_residuo, 
                                dia_predicho=dia_predicho)
    
    prediccion_XGboost = predictor(numero_semanas=numero_semanas,
                                   modelo_1=modelo_XGboost_M1,
                                   modelo_2=modelo_XGboost_M2,
                                   modelo_residuo=modelo_XGboost_residuo,
                                   dia_predicho=dia_predicho)
    #usamos parametros hallados en el modelado con el ensemble a traves de PSO-CS
    prediccion_final = (0.84493549*prediccion_XGboost +
                0.15506451*prediccion_LGBM
                )
    
    return round(prediccion_final,2)