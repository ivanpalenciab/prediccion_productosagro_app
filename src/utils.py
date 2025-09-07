import pandas as pd
from sklearn.preprocessing import MinMaxScaler

dia_inicio = "13/08/2025" #esta es la ultima fecha donde tengo datos
fecha_predecir = "19/08/2025" #dia de referencia de la semana que quiero predecir
fecha_predecir = pd.to_datetime(fecha_predecir,format='%d/%m/%Y')
dia_inicio = pd.to_datetime(dia_inicio,format='%d/%m/%Y')
dia_predicho = dia_inicio

#importamos datos futuros
proyecciones_futuro = pd.read_csv("src/data/proyecciones_futuros_maiz.csv")
proyecciones_futuro["Tiempo"]=pd.to_datetime(proyecciones_futuro["Tiempo"],dayfirst=False)
proyecciones_futuro.rename(columns={"Precio":"Futuro","Tiempo":"Fecha"},inplace=True)
proyecciones_futuro["Futuro"] = proyecciones_futuro["Futuro"]/(25.4*100)
proyecciones_futuro.set_index("Fecha", inplace=True)
proyecciones_futuro.head()

#importamos datos emd
modo_1_actualizado=pd.read_csv("src/data/EMD_modes/Modo_1.csv")
modo_2_actualizado=pd.read_csv("src/data/EMD_modes/Modo_2.csv")
residuo_actualizado=pd.read_csv("src/data/EMD_modes/Residuo.csv")
modos = [modo_1_actualizado,modo_2_actualizado,residuo_actualizado]

for i in modos:
  i["FECHA"] = pd.to_datetime(i["FECHA"],format='%Y-%m-%d')
  i.set_index("FECHA", inplace=True)


#Funcion para hallar los datos de las 7 semanas anteriores
def vector_7_semanas_anteriores(serie, fecha_objetivo):
    """
    serie: pd.Series con índice datetime (ej. modo_1["PROMEDIO"])
    fecha_objetivo: str o datetime (ej. "2025-08-19")
    return: lista de tuplas (fecha, precio) de las 7 semanas anteriores
    """
    fecha_objetivo = pd.to_datetime(fecha_objetivo)
    historial = []

    for i in range(1, 8):
        fecha_busqueda = fecha_objetivo - pd.Timedelta(weeks=i)

        # Buscar la fecha más cercana en la serie
        idx_cercano = serie.index.get_indexer([fecha_busqueda], method="nearest")[0]
        fecha_cercana = serie.index[idx_cercano]
        precio = serie.iloc[idx_cercano].item()

        historial.append((fecha_cercana, precio))

    precios_anteriores = historial
    precios_anteriores = [x[1] for x in precios_anteriores]
    input = pd.DataFrame(precios_anteriores,index=["retraso-1","retraso-2","retraso-3","retraso-4","retraso-5","retraso-6","retraso-7"]).T
    input.index = [fecha_objetivo]
    input = pd.merge( input,proyecciones_futuro,left_index=True, right_index=True, how='inner')

    return input

# función para escalar los datos 
def escalador(modo):
  modo_values = modo.values
  modo_values = modo_values.astype('float32')
  modo_scaler = MinMaxScaler(feature_range=(-1, 1))

  modo_escalado =  pd.DataFrame(modo_scaler.fit_transform(modo_values), columns=modo.columns,index=modo.index)

  return modo_scaler,modo_escalado

#escalador de datos 
escalador_modo_1,modo_1_escalado =escalador(modo_1_actualizado)
escalador_modo_2,modo_2_escalado =escalador(modo_2_actualizado)
escalador_residuo,residuo_escalado =escalador(residuo_actualizado)

#Función para predecir n semanas 
def predictor(numero_semanas,modelo_1,modelo_2,modelo_residuo,dia_predicho):
   """Esta funcion permite predecir n semanas, la funcion recibe el numero de semanas y cada uno de los modelos"""
   semanas_predichas=0
   for i in range(1,numero_semanas+1):
    input_modo_1 = vector_7_semanas_anteriores(modo_1_escalado,dia_predicho + pd.Timedelta(weeks=1))
    input_modo_2 = vector_7_semanas_anteriores(modo_2_escalado,dia_predicho + pd.Timedelta(weeks=1))
    input_residuo = vector_7_semanas_anteriores(residuo_escalado,dia_predicho + pd.Timedelta(weeks=1))
    

    prediccion_modo_1_escalado = modelo_1.predict(input_modo_1 )
    prediccion_modo_2_escalado = modelo_2.predict(input_modo_2 )
    prediccion_residuo_escalado = modelo_residuo.predict(input_residuo)


    #volvemos a escala original
    prediccion_modo_1 = escalador_modo_1.inverse_transform(prediccion_modo_1_escalado.reshape(-1, 1))
    prediccion_modo_2 = escalador_modo_2.inverse_transform(prediccion_modo_2_escalado.reshape(-1, 1))
    prediccion_residuo = escalador_residuo.inverse_transform(prediccion_residuo_escalado.reshape(-1, 1))

    prediccion = prediccion_modo_1+prediccion_modo_2+prediccion_residuo
    prediccion[0,0]
    dia_predicho = dia_predicho + pd.Timedelta(weeks=1)
    semanas_predichas = i
    print(f"fecha predicha {dia_predicho}")
    print(str(prediccion[0,0]))
    print(f"Se predijeron {semanas_predichas} semanas")

    if semanas_predichas < numero_semanas:
        modo_1_escalado.loc[dia_predicho] = prediccion_modo_1_escalado[0]
        modo_2_escalado.loc[dia_predicho] = prediccion_modo_2_escalado[0]
        residuo_escalado.loc[dia_predicho] = prediccion_residuo_escalado[0]
    print(f"lo que en realidad retorna es {str(prediccion[0,0])}")
    print(f"La verdadera fecha predicha es {dia_predicho}")

   return float(prediccion[0,0]), dia_predicho
   