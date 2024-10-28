# API de Traitement de Fichiers

# Fichier main.py  

## Description  
Cette API permet de traiter des fichiers PDF ou image (JPG, JPEG, PNG) en extrayant certaines informations spécifiques grâce à la bibliothèque OCR `easyocr` et à d'autres fonctions définies dans un module externe `mylib_montant`. Elle extrait les éléments suivants :

- Dates
- Numéros SIREN/SIRET
- Codes postaux
- Pourcentages
- Montants et somme totale des montants

Le traitement est effectué via une requête POST, et les résultats sont retournés sous forme de réponse JSON.  

## Prérequis

Avant de commencer, assurez-vous que les dépendances suivantes sont installées dans votre environnement :

1. Python 3.7 ou supérieur
2. Les bibliothèques Python nécessaires (FastAPI, EasyOCR, Uvicorn, Pydantic, etc.), pour ceci télécharger le requirements.txt via la commande : pip install -r requirements.txt

## Lancement API  

Lancer l'api a l'aide de la commande : `python main.py`  

## Tester avec POSTman  

Sélectionner la requete : POST  
Entrez l'url: http://localhost:8000/process_file  
Cliquer sur `body` puis `raw`  
puis entrez votre fichier a analyser sous ce format :   
{  
    "file_path": "chemin_de_votre_fichier_PDF"  
}

## Résultat attendu  

Le résultat sont les informations générales sur le fichier pdf/image choisis.


# Fichier mainV2.py  

## Description  
Cette API permet de traiter des fichiers PDF ou image (JPG, JPEG, PNG) en extrayant certaines informations spécifiques grâce à la bibliothèque OCR `easyocr` et à d'autres fonctions définies dans un module externe `mylib_montant`. Elle extrait les éléments suivants :

- Dates
- Numéros SIREN/SIRET
- Codes postaux
- Pourcentages
- Montants et somme totale des montants

Le traitement est effectué via une requête POST, et les résultats sont retournés sous forme de réponse JSON.  

## Prérequis

Avant de commencer, assurez-vous que les dépendances suivantes sont installées dans votre environnement :

1. Python 3.7 ou supérieur
2. Les bibliothèques Python nécessaires (FastAPI, EasyOCR, Uvicorn, Pydantic, etc.), pour ceci télécharger le requirements.txt via la commande : pip install -r requirements.txt

## Lancement API  

Lancer l'api a l'aide de la commande : `python mainV2.py`  

## Tester avec POSTman  

Sélectionner la requete : POST  
Entrez l'url: http://localhost:8000/process_file  
Cliquer sur `body` puis `raw`  
puis entrez votre fichier a analyser sous ce format :   
{  
    "file_path": "chemin_de_votre_fichier_PDF"  
}

## Résultat attendu  

Le résultat sont les informations générales sur le fichier pdf/image choisis, les données sont triées page par pages afin de faciliter la prise d'information.


# Fichier stream.py  

## Description
Cette application **Streamlit** permet de traiter des fichiers PDF ou image (JPG, JPEG, PNG) en extrayant diverses informations spécifiques via un processus d'OCR (reconnaissance optique de caractères) utilisant **EasyOCR** et les fonctions d'analyse de texte du module externe `mylib_montant`.

L'application permet d'extraire les éléments suivants :
- Dates
- Numéros SIREN/SIRET
- Codes postaux
- Pourcentages
- Montants et somme totale des montants

L'interface propose le téléchargement d'un fichier, le traitement OCR, et l'affichage des résultats selon les critères sélectionnés par l'utilisateur.

## Prérequis

Avant de démarrer, vous devez installer les dépendances suivantes dans votre environnement Python :

1. **Python 3.7** ou supérieur
2. Les bibliothèques Python nécessaires (Streamlit, EasyOCR, Pillow, etc.)

Installez les dépendances en exécutant la commande suivante : `pip install -r requirements.txt`  

## Lancement de l'application Streamlit  

Lancer l'api a l'aide de la commande : `streamlit run stream.py`  

## Tester l'application  

Une fois lancer il suffit de se rendre sur l'url fournit par streamlit (localhost:8000), une fois sur l'application choisir un document a analyser, attendre que la barre de chargement soit terminer, puis cocher les éléments que l'on souhaite faire ressortir.