import requests # Para enviar solicitudes GET desde la API
import os # Para guardar los tokens de acceso y para la gestión de archivos al crear y añadir al conjunto de datos
import pandas as pd # Para mostrar los datos después
# Para parsear las fechas recibidas de twitter en formatos legibles
import dateutil.parser
import claves #Importar claves
import time

CONSUMER_KEY = claves.CONSUMER_KEY
CONSUMER_SECRET = claves.CONSUMER_SECRET
BEARER_TOKEN = claves.BEARER_TOKEN
ACCESS_TOKEN = claves.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = claves.ACCESS_TOKEN_SECRET

# guardaremos el token en una "variable de entorno"
os.environ['TOKEN'] = BEARER_TOKEN

#crearemos nuestra función auth () , que recupera el token del entorno
def auth():
    return os.getenv('TOKEN')

#A continuación, definiremos una función que tomará nuestro token de portador, 
#lo pasará para su autorización y devolverá los encabezados que usaremos para acceder a la API.
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# Ahora que podemos acceder a la API, crearemos la solicitud para el punto final que vamos a usar y los parámetros que queremos pasar.
def create_url(keyword, start_date, end_date, max_results=500):
    
    #Cuál es el enlace del endpoint al que queremos acceder para recoger datos
    search_url = "https://api.twitter.com/2/tweets/search/all"

    """Los parámetros que ofrece el endpoint y que podemos usar para personalizar la solicitud que queremos enviar."""
    
    query_params = {'query': keyword, 
                    'start_time': start_date, #AAAA-MM-DDTHH: mm: ssZ (ISO 8601 / RFC 3339)
                    'end_time': end_date, ##AAAA-MM-DDTHH: mm: ssZ (ISO 8601 / RFC 3339)
                    'max_results': max_results, #El número de resultados de búsqueda devueltos por una solicitud está limitado entre 10 y 500 resultados.
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)

#Ahora que tenemos la URL, los encabezados y los parámetros que queremos, crearemos una función que unirá todo esto y se conectará al punto final.
#La función a continuación enviará la solicitud "GET" y si todo es correcto (código de respuesta 200), devolverá la respuesta en formato "JSON".
def connect_to_endpoint(url, headers, params, next_token = None): #next_token está configurado en "Ninguno" de forma predeterminada, ya que solo nos importa si existe.
    params['next_token'] = next_token   #objeto params recibido de la función create_url
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def create_df(json_response): # Función para crear df de respuesta a partir del json 
    res = []
    #Recorrer en bucle cada uno de los tweets del json
    for tweet in json_response['data']:
        
        # creará una variable para cada uno ya que algunas de las claves podrían no existir para algunos tweets

        # 1. Author ID
        if ('author_id' in tweet): 
            author_id = tweet['author_id']
        else:
            author_id = " "
        
        # 2. Time created
        if ('created_at' in tweet): 
            created_at = dateutil.parser.parse(tweet['created_at'])
        else:
            created_at = " "
            
        # 3. Geolocation
        if ('place_id' in tweet):
            geo = tweet['geo']['place_id']
        else:
            geo = " "

        # 4. Tweet ID
        if ('id' in tweet):
            tweet_id = tweet['id']
        else: 
            id = " "

        # 5. Language
        if ('lang' in tweet):
            lang = tweet['lang']
        else: 
            lang = " "

        # 6. Tweet metrics
        if ('retweet_count' in tweet):
            retweet_count = tweet['public_metrics']['retweet_count']
        else:
            retweet_count = " "
        
        if ('reply_count' in tweet):
            reply_count = tweet['public_metrics']['reply_count']
        else:
            reply_count = " "
        
        if ('like_count' in tweet):
            like_count = tweet['public_metrics']['like_count']
        else:
            like_count = " "
        
        if ('quote_count' in tweet):
            quote_count = tweet['public_metrics']['quote_count']
        else:
            quote_count = " "
            
        # 7. source
        if ('source' in tweet):
            source = tweet['source']
        else:
            source = " "
            
        # 8. Tweet text
        if ('text' in tweet): 
            text = tweet['text']
        else:
            text = " "
    
        # Reunir todos los datos en una lista
        res.append([author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text])
    
    df_res = pd.DataFrame(data = res, columns=['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet'])
    # Imprime el número de tweets de esta iteración
    return df_res

def create_df_final(url, headers, json_response): #función para obtener todos los tweets de cada consulta
  df_res = create_df(json_response) #paso como parámetro
  print("Número de Tweets añadidos de esta respuesta: ",len(df_res))
  while 'next_token' in json_response["meta"]:
    # Guarda el token para usarlo en la siguiente llamada
    next_token = json_response['meta']['next_token']
    if ('data' in json_response) and len(df_res)< 499500:
        json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
        df_aux = create_df(json_response)
        df_res = pd.concat([df_res,df_aux])
        time.sleep(2) #Se agrega un time.sleep () entre llamadas para asegurarse de que no solo está enviando spam a la API con solicitudes.
        print("Número de Tweets añadidos de esta respuesta: ",len(df_res))
    else:
        break
  return df_res    
