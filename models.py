import pandas as pd
from prepro import *
import pickle
from sklearn.model_selection import train_test_split
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import *


# Paso 1 cargamos los datos de testeo y entrenamiento
df_train = pd.read_csv('data/general-train-tagged-3l.csv', encoding='utf-8')
df_test = pd.read_csv('data/general-test-tagged-3l.csv', encoding='utf-8')


# Paso 2 LIMPIAR: quitamos aquellos tweets con polarity igual a NONE
df_train = df_train.query('polarity != "NONE"')
df_test = df_test.query('polarity != "NONE"')

# Paso 3 Unimos los datos en un mismo dataset
df = pd.concat([df_train, df_test])

"""
# Paso 4 Aplicamos el preprocesado a los conjuntos de entrenamiento y testeo y lo guardamos
ls_tw_prepro = prepro(list(df['content']))


with open('data/ls_tw_prepro.pickle', 'wb') as handle:
    pickle.dump(ls_tw_prepro, handle)

# Como el preprocesado lleva mucho tiempo, abrimos el archivo con los datos guardados preprocesados para hacer las pruebas correspondientes
"""

file = open('data/ls_tw_prepro.pickle','rb')
ls_tw_prepro = pickle.load(file)
file.close()


df_prepro = df
df_prepro['content'] = ls_tw_prepro

#Paso 5 Separa el dataset en dos partes (entrenamiento y test) con la proporción 70-30.
X_train, X_test, y_train, y_test = train_test_split(df_prepro['content'], df_prepro['polarity'],test_size=0.30, random_state=40)

print(f"Training target statistics: {Counter(y_train)}")
print(f"Testing target statistics: {Counter(y_test)}")

#Paso 6 A continuación debemos utilizar el método de bolsas de palabras y transformar los documentos en una document term matrix.
vectorizer = TfidfVectorizer(min_df=0.05, max_df=0.95, max_features= 10000)
vectorizer_fit = vectorizer.fit(ls_tw_prepro)

#Paso 7 Guardamos el vectorizer
with open('data/vectorizer_class.pickle', 'wb') as handle:
    pickle.dump(vectorizer_fit, handle)

# Paso 8 Aplicamos la clase vectorizer a ambos conjuntos
vect_train = vectorizer_fit.transform(X_train)
vect_test = vectorizer_fit.transform(X_test)

#Paso 9 Encontramos los mejores hiperparámetros para el clasificador
"""
clf = LinearSVC(loss='squared_hinge',multi_class='ovr',random_state=None,penalty='l2',tol=0.0001)
parameters = {'C':[0.2,1,10,100,1000], 'max_iter':[1000,2000,3000]}        
grid_search = GridSearchCV(clf, parameters, scoring='accuracy',n_jobs=-1, cv=10)

"""
clf = MultinomialNB()
parameters = {'alpha': [0.001, 0.01, 0.1, 0.5, 1.0, 10.0]}      
grid_search = GridSearchCV(clf, parameters, scoring='accuracy',n_jobs=-1, cv=10)


grid_fit = grid_search.fit(vect_train.toarray(), y_train)
clf_best = grid_fit.best_estimator_
best_params = grid_fit.best_params_
print("El clasificador usado es:", clf_best)
print("Los hiperparámetros del mejor modelo son:",best_params)

# Paso 10 Realizamos la predicción sobre los datos del test y evaluamos el resultado
yhat = clf_best.predict(vect_test.toarray())

# Paso 11 Guardamos el modelo 
with open('data/clf_best.pickle', 'wb') as handle:
    pickle.dump(clf_best, handle)
    
# Paso 12 Evaluamos el resultado de la predicción comparándolo con las etiquetas reales
#Matriz de confusión
confmat = multilabel_confusion_matrix(y_true=y_test, y_pred=yhat, labels=["P", "N", "NEU"])
print('Matriz de confusión:', confmat)

#Tasa de acierto
accu = accuracy_score(y_test, yhat)
print('Accuracy: ', accu)

"""
#AUC
auc= roc_auc_score(y_test, yhat, multi_class='ovr')
print('Accuracy: ', auc)

#F1-Score
f1=f1_score(y_test, yhat, average=micro)
print('\tF1 score micro: ',f1)
"""



