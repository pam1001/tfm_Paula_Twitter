# Creamos una función con dos bucles, el primero recorre cada lista y el segundo cada uno de los tweets.
# Para cada lista se recorre cada tweet y si este contiene alguna palabra de la lista añade 1 a la lista vacía aux 
# y si no contiene ninguna se añade un 0
# Finalmente nos devuelve una lista de listas, es decir, una lista por cada lista de palabras que contiene un 0 o un 1 por cada tweet
def categoriza(ls_tw, listas):
  res = []
  for ls in listas:
      aux = []
      for tw in ls_tw:
          if any(w in tw.split(' ') for w in ls):
              aux.append(1)
          else:
              aux.append(0)
      res.append(aux)
  return res