from fastapi import FastAPI, HTTPException
import easyocr
import re
import fitz
import os
from mylib_montant import paths, functions
from typing import Tuple
import shutil
from PIL import Image
from io import BytesIO  # Pour gérer les fichiers en mémoire
import tempfile  # Pour créer un fichier temporaire



# Fonction pour traiter le fichier (PDF ou image)
def process_file(file, file_extension):
    final_text = ""
    reader = easyocr.Reader(['fr'])

    if file_extension == '.pdf':
        # Lire le fichier PDF directement depuis le tampon (BytesIO)
        pdf_bytes = BytesIO(file.read())

        # Créer un fichier temporaire pour le PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes.getvalue())
            tmp_file.flush()

            # Utiliser le fichier temporaire pour la conversion PDF -> images
            images = functions.pdf2img(tmp_file.name)  # Utiliser le chemin du fichier temporaire

        ocr_results = []
        
        # Appliquer l'OCR sur chaque image
        for image in images:
            text = " ".join(reader.readtext(image, detail=0))  # Extraire le texte de chaque image
            ocr_results.append(text)
        final_text = " ".join(ocr_results)  # Concatenation du texte extrait

        return images, final_text  # On retourne également les images pour les afficher plus tard

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        final_text = " ".join(reader.readtext(file, detail=0))  # Extraire le texte
        image = Image.open(file)  # Charger l'image pour l'afficher
        return [image], final_text  # Retourne une liste contenant l'image pour être cohérent

    return [], final_text


def pdf2img(pdfFile: str, pages: Tuple = None):
    # On charge le document
    pdf = fitz.open(pdfFile)
    # On détermine la liste des fichiers générés
    pngFiles = []
    # Pour chaque page du pdf
    pngPath = str(paths.rootPath_img) + str(paths.tmpDirImg) + os.path.basename(str(pdfFile).split('.')[0])
    
    try:
        for pageId in range(pdf.page_count):
            if str(pages) != str(None):
                if str(pageId) not in str(pages):
                    continue

            # On récupère la page courante
            page = pdf[pageId]
            # On convertit la page courante
            pageMatrix = fitz.Matrix(2, 2)
            pagePix = page.get_pixmap(matrix=pageMatrix, alpha=False)
            # On exporte la page générée

            # Si le répertoire dédié au pdf n'existe pas encore, on le crée
            if not os.path.exists(pngPath):
                os.makedirs(pngPath)

            pngFile = pngPath + "_" + f"page{pageId+1}.png"
            pagePix.save(pngFile)
            pngFiles.append(pngFile)

        pdf.close()

        # On retourne la liste des pngs générés
        return pngFiles

    finally:
        # On supprime le répertoire et son contenu après le traitement
        if os.path.exists(pngPath):
            shutil.rmtree(pngPath)



# Fonction pour extraire les dates avec regex
def extract_dates(text):
    date_regex = r'\b(0[1-9]|[12][0-9]|3[01])[\/\-.](0[1-9]|1[0-2])[\/\-.](\d{4})\b'
    dates = re.findall(date_regex, text)
    for date in dates:
        formatted_date = "/".join(date)
        text = text.replace(formatted_date, "A")  # Supprimer chaque date trouvée
    return dates, text

def extract_siren(text):
    # Expression régulière pour les numéros SIREN (9 chiffres)
    siren_regex = r'\b(\d{3}\s?\d{3}\s?\d{3})\b'
    sirens = re.findall(siren_regex, text)
    # Supprimer chaque SIREN trouvé du texte
    # for siren in sirens:
    #     text = text.replace(siren, "A")  # Remplacer par "A"
    return sirens, text

def extract_siret(text):
    # Expression régulière pour les numéros SIRET (14 chiffres : 9 chiffres SIREN + 5 chiffres supplémentaires)
    siret_regex = r'\b(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})\b'
    sirets = re.findall(siret_regex, text)
    # Supprimer chaque SIRET trouvé du texte
    for siret in sirets:
        text = text.replace(siret, "A")  # Remplacer par "A"
    return sirets, text


# Fonction pour extraire les codes postaux (français)
def extract_postal_codes(text):
    postal_code_regex = r'\b\d{5}\b'
    postal_codes = re.findall(postal_code_regex, text)
    for postal_code in postal_codes:
        text = text.replace(postal_code, "A")  # Supprimer chaque code postal trouvé
    return postal_codes, text

# Fonction pour extraire les pourcentages allant de 1% à 100% avec le symbole %
def extract_percentages(text):
    # Regex pour les pourcentages entre 1% et 100%
    percentage_regex = r'(100|[1-9]?[0-9]) ?%'
    percentages = re.findall(percentage_regex, text)
    # print(f'poucentage trouvée : {percentages}')
    
    for percentage in percentages:
        percentage_with_symbol = f"{percentage}%"  # Reformater pour inclure le symbole %
        text = text.replace(percentage_with_symbol, "A")  # Remplacer chaque pourcentage par "A%"
    
    # Retourner les pourcentages trouvés et le texte modifié
    return [f"{percentage}%" for percentage in percentages], text

# Fonction pour extraire les montants
def extract_montants(text):
    montant_regex = r'\d{1,3}(?:[ ]\d{3})*[.,]\d{2} ?[€]?'  # Regex pour détecter les montants
    montants = re.findall(montant_regex, text)
    
    # Conversion des montants en flottants et suppression des espaces et symboles inutiles
    montants_numeriques = []
    for montant in montants:
        montant_clean = montant.replace(" ", "").replace(",", ".").replace("€", "")  # Nettoyage
        try:
            montants_numeriques.append(float(montant_clean))  # Conversion en nombre
        except ValueError:
            continue  # Si un montant ne peut pas être converti, on l'ignore
    
    # Calcul de la somme des montants
    somme_montants = sum(montants_numeriques)
    
    # Suppression des doublons
    montants_uniques = list(set(montants))  # On garde seulement les montants uniques
    
    # Remplacement des montants dans le texte
    for montant in montants_uniques:
        text = text.replace(montant, "A")  # Remplacer chaque montant unique trouvé par "A"
    
    # Retourner les montants uniques, la somme, et le texte modifié
    return montants_uniques, somme_montants, text

