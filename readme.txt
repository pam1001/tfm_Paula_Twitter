=================================================== PREPARACI�N DEL PROYECTO ===================================================================================
Como requisitos iniciales debes tener instalado Python. Este proyecto se ha creado con Python 3.8.5 por lo tanto recomendamos esta versión.
https://www.python.org/downloads/

Para poder descargar paquetes de Python, debes instalar la herramienta PyPi.
Antes de instalar PIP en Windows, compruebe si PIP ya está instalado.
1. Inicie la ventana del símbolo del sistema:
2. Escriba el siguiente comando en el símbolo del sistema:
>>pip help
Si PIP responde, entonces PIP est� instalado. 
Si responde pero no est� actualizado.
>>python -m pip install --upgrade pip
En caso contrario, aparecer� un error diciendo que no se ha podido encontrar el programa.
Entonces deber� instalarlo con:
>>pip install pip

En primer lugar debes instalar los siguientes paquetes:
>>pip install -U scikit-learn
>>pip install pandas
>>pip install stanza
>>pip install nltk
>>pip install tqdm

Luego, importa estas librerías para descargar datos de ellas.
>>python
>>import stanza
>>import nltk
>>stanza.download('es')
>>nltk.download('stopwords')
>>exit()

En tercer lugar, introduce las claves de la API de Twitter en el archivo "claves.py". Recuerda que deben ser claves asociadas a un proyecto
Research Academic.

=================================================================== PARA EJECUTAR EL PROYECTO =====================================================================

1. Accedemos a l�nea de comandos (cmd)
2. Accedemos al directorio donde se encuentra la carpeta del proyecto
>>D:
>>cd D:\Usuario\Descargas\TFM_Paula_Spyder
3. Ejecutamos con los scripts del proyecto con el comando python
>>python __main__.py
