#pip install stanza
#pip install nltk
import re
import nltk
from nltk.corpus import stopwords
#nltk.download('stopwords') # descargar stopwords
import stanza
#stanza.download('es') # descargar 
from tqdm import tqdm
import pickle

# TODAS LAS FUNCIONES QUE SIRVEN PARA EL PREPROCESADO Y UNA FUNCIÓN QUE ENCAPSULA A TODAS LAS DEMÁS PARA
# SER APLICADA A LA LISTA DE TWEETS 

# Creamos variable para descargar y cargar procesadores por defecto en una pipeline para español
NLP = stanza.Pipeline('es',verbose=False)

# Eliminar menciones
def rmMencion(text):        
        return re.sub(r'@\w+', '', text)
    
# Eliminar retweets
def rmRt(text):
    return re.sub(r"RT",'',text)

# Convertimos caracteres del tweet en minúsculas
def aMinuscula(text):
    return text.lower()

# Eliminar URLs
def rmUrl(text):        
    return re.sub(r'http.?://[^\s]+[\s]?', '', text)

# Eliminamos caracteres que no sean letras
def soloLetras(text):
    return re.sub('[^a-zA-Z\s\ñ\á\é\í\ó\ú]', ' ', text)

# Sustituimos abreviaturas y risa
def risa(text):
    text=re.sub(r"q\b", "que", text)
    text=re.sub(r"tb\b", "también", text)
    text=re.sub(r"tqm\b", "te quiero mucho", text)
    text=re.sub(r"\b(?:a*(?:ja)+j?)\b", "risa", text)
    text=re.sub(r"\b(?:e*(?:je)+j?)\b", "risa", text)
    text=re.sub(r"\b(?:i*(?:ji)+j?)\b", "risa", text)
    #text=re.sub(r"\b(?:lol?)\b", "risa", text) #sustituye cuando hay lol
    text=re.sub(r"lol\b", "risa", text)
    return text

# Stemmer: Esta función divide el tweet en una lista de palabras y elimina aquellas que no aportan informacion
def remove_sw(text): 
    return ' '.join(i for i in text.split() if i not in set(stopwords.words('spanish')))

# Lemmatizer: 
def lemmatiza(text):
  res = []
  #nlp = stanza.Pipeline('es',verbose=False)
  doc = NLP(text)
  for sent in doc.sentences:
    for word in sent.words:
      res.append(word.lemma)
  return' '.join(res)

#Definimos función para preprocesar tweets formada por las funciones anteriores
def prepro(ls_tw):
  results =[]
  for tw in tqdm(ls_tw):
    texto = rmMencion(tw)
    texto = rmRt(texto)
    texto = aMinuscula(texto)
    texto = rmUrl(texto)
    texto = soloLetras(texto)
    texto = risa(texto)
    texto = remove_sw(texto)
    texto = lemmatiza(texto)
    results.append(texto)
  return results