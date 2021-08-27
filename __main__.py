import pickle
from datetime import datetime
import datetime
from twitter_api import *
import pandas as pd
import dateutil.parser
from prepro import *
from categoriza import *
import csv 

#============>Petición de los datos input
def menu():
    localidad = input("Introduzca el nombre del territorio (localidad):")
    pais = input("\nIntroduzca el nombre del país (por ej ES para España):")
    ls_words = input("\nIntroduzca la palabra clave o hashtag (por ejemplo #centenario catedral):")
    lang = input("\nIntroduzca el idioma (por ejemplo 'es' para español):")
    date_since = input("\nIntroduzca Fecha de inicio en el formato AAAA-MM-DD:")
    date_until = input("\nIntroduzca Fecha de fin en el formato AAAA-MM-DD:")
    return localidad,pais,ls_words,lang,date_since,date_until

#============>Archivos finales de resultados y consultas
def get_id_consulta(): #función para numerar las consultas
    df_consultas = pd.read_csv('data/consultas.csv',sep=',')
    if len(df_consultas)==0:
        return 1
    else:
        return int(df_consultas['Id_busqueda'].iloc[-1])+1 #paso a entero al último item de la columna id_busqueda y le sumo 1
    
def update_resultados(df_res_new): #función para tener todos los resultados de todas las consultas en un mismo df
    df_res_old = pd.read_csv('data/df_resultados.csv',sep=',')
    df_res = pd.concat([df_res_old,df_res_new])
    df_res.to_csv('data/df_resultados.csv',index = False)

def fix(df_group): 
    x = pd.DataFrame(df_group)
    idx = list(df_group.index)
    if len(idx)==3:
        return df_group
    else:
        if 'N' not in idx:
            x.loc['N'] = [0,0,0,0]
        if 'P' not in idx:
            x.loc['P'] = [0,0,0,0]
        if 'NEU' not in idx:
            x.loc['NEU'] = [0,0,0,0]
        x = x.sort_index()
        return x
    
def conteo(df_results): #función para contar el número de tweets de cada categoría por tipo de polaridad
    res = []
    df_results = df_results[['polarity','alojamientos','producto','seguridad','clima']]
    df_group = df_results.groupby('polarity').sum()
    df_group = fix(df_group)
    res.extend(list(df_group['alojamientos']))
    res.extend(list(df_group['producto']))
    res.extend(list(df_group['seguridad']))
    res.extend(list(df_group['clima']))
    return res
    
def update_consultas(new_row): #función para tener todos las consultas de todas las consultas en un mismo df
    with open('data/consultas.csv', 'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_row)
    
if __name__ == "__main__":
    id_consulta = get_id_consulta()

    # Paso 1 carga vectorizer
    file = open('data/vectorizer_class.pickle','rb')
    vectorizer_fit = pickle.load(file)
    file.close()
    
    # Paso 2 cargar los modelos
    file = open('data/clf_best.pickle','rb')
    clf = pickle.load(file)
    file.close()

    # Paso 3 Inputs para la solicitud de datos Twitter
    loc,pais1,ls_palabras,idioma,date_since,date_until = menu()
    #keyword = "#covid OR vacuna place:Madrid place_country:ES lang:es"
    start_time = date_since+"T00:00:00.000Z"
    end_time = date_until+"T00:00:00.000Z"
    ls_words = ls_palabras.replace(' ', ' OR ')
    localidad = 'place:'+loc
    pais = 'place_country:'+pais1
    lang = 'lang:'+idioma

    q = f'{ls_words} {localidad} {pais} {lang}' #definimos la query
    bearer_token = auth()
    headers = create_headers(bearer_token)
    keyword = q
    start_time = start_time
    end_time = end_time
    
    #Paso 5 Enviamos solicitud a la conexión endpoint
    url = create_url(keyword, start_time,end_time)
    json_response = connect_to_endpoint(url[0], headers, url[1])
    df_raw =  create_df_final(url, headers, json_response)#create_df(json_response) #guardamos resultados de json a df

    #Paso 6 La columna de Tweet la guardamos en una lista y la preprocesamos
    ls_tw_raw = list(df_raw['tweet'])
    ls_tw_prepro = prepro(ls_tw_raw)
    df_raw['tweet_prepro'] = ls_tw_prepro
    
    # Paso 7 A los datos preprocesados les aplicamos la clase vectorizer y predecimos la polaridad aplicando el modelo
    vect_test = vectorizer_fit.transform(ls_tw_prepro)
    yhat = clf.predict(vect_test)
    df_raw['polarity'] = yhat
    
    # Paso 8 Cargamos listas para la categorización de los tweets
    ls_producto = list(pd.read_csv('data/producto.csv',sep = ',',header=None)[0])
    ls_alojamientos = list(pd.read_csv('data/alojamientos.csv',sep = ',',header=None)[0])
    ls_seguridad = list(pd.read_csv('data/seguridad.csv',sep = ',',header=None)[0])
    ls_clima = list(pd.read_csv('data/clima.csv',sep = ',',header=None)[0])
    
    # Paso 9 Pasamos a la función categoriza la lista de tweets preprocesados y las listas de categorización
    ls_cats = categoriza(ls_tw_prepro, [ls_producto,ls_alojamientos,ls_seguridad,ls_clima])
    #Añadimos las columnas al df
    df_raw['producto'] = ls_cats[0]
    df_raw['alojamientos'] = ls_cats[1]
    df_raw['seguridad'] = ls_cats[2]
    df_raw['clima'] = ls_cats[3]
    
    # Paso Extra: Almacenar la id de la búsqueda
    df_raw['Id_busqueda'] = [id_consulta]*len(yhat)
    
    # Paso 10 Guardamos los datos obtenidos en un único archivo csv
    update_resultados(df_raw)
    
    # Paso 11: Actualizamos archivo de búsquedas
    new_fila = [id_consulta,loc,pais1,ls_palabras,idioma,date_since,date_until,date_since+' '+date_until]
    ls_cont = conteo(df_raw)
    new_fila.extend(ls_cont)
    update_consultas(new_fila)
    
    # Mostramos por pantalla el link de la visualización
    print("Accede a la visualización en: https://bit.ly/2Wq6Xl4")