# API de Traitement de Fichiers

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

Lancer l'api a l'aide de la commande : python main.py  

## Tester avec POSTman  

Sélectionner la requete : POST  
Entrez l'url: http://localhost:8000/process_file  
Cliquer sur "body" puis "raw"  
puis entrez votre fichier a analyser sous ce format :   
{  
    "file_path": "chemin_de_votre_fichier_PDF"  
}