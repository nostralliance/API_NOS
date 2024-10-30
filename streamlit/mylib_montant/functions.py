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
    reader = easyocr.Reader(['fr'])  # Initialiser le lecteur OCR

    if file_extension == '.pdf':
        # Lire le fichier PDF directement depuis le tampon (BytesIO)
        pdf_bytes = BytesIO(file.read())

        # Créer un fichier temporaire pour le PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes.getvalue())
            tmp_file.flush()

            # Utiliser le fichier temporaire pour la conversion PDF -> images
            images = functions.pdf2img(tmp_file.name)  # Utiliser le chemin du fichier temporaire

        # Initialiser une chaîne pour le texte brut
        ocr_text = ""

        # Appliquer l'OCR sur chaque image et concaténer le texte
        for image in images:
            text = " ".join(reader.readtext(image, detail=0))  # Extraire le texte de chaque image
            ocr_text += text + " "  # Ajouter le texte à la chaîne principale

        return images, ocr_text.strip()  # Retourner les images et le texte brut

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        ocr_text = " ".join(reader.readtext(file, detail=0))  # Extraire le texte
        image = Image.open(file)  # Charger l'image pour l'afficher
        return [image], ocr_text.strip()  # Retourner l'image et le texte brut

    return [], ""

# Fonction pour traiter le fichier (PDF ou image)
def process_file_page_per_page(file, file_extension):
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
            ocr_results.append(text)  # Conserver le texte pour chaque page

        return images, ocr_results  # Retourne aussi les images

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        final_text = " ".join(reader.readtext(file, detail=0))  # Extraire le texte
        image = Image.open(file)  # Charger l'image pour l'afficher
        return [image], [final_text]  # Retourne une liste contenant l'image et le texte

    return [], []


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
    # Convertir en un ensemble pour supprimer les doublons, puis en liste
    unique_dates = list(set(dates))
    for date in unique_dates:
        formatted_date = "/".join(date)
        text = text.replace(formatted_date, "A")  # Supprimer chaque date trouvée
    return unique_dates, text

def extract_siret(text):
    siret_regex = r'\b(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})\b'
    sirets = re.findall(siret_regex, text)
    unique_sirets = list(set(sirets))  # Supprimer les doublons
    for siret in unique_sirets:
        text = text.replace(siret, "A")  # Remplacer par "A"
    return unique_sirets, text

def extract_siren_from_siret(sirets):
    # Extraire les SIREN uniques
    unique_sirens = list(set(siret.replace(" ", "")[:9] for siret in sirets))
    print("Les SIREN trouvés sont :", unique_sirens)
    return unique_sirens

def extract_adeli(text):
    adeli_regex = r'\b(\d{3}\s?\d{3}\s?\d{3})\b'
    adelis = re.findall(adeli_regex, text)
    # Suppression des doublons et normalisation des espaces
    unique_adelis = list(set(adeli.replace(" ", "") for adeli in adelis))
    for adeli in unique_adelis:
        text = text.replace(adeli, "A")
    return unique_adelis, text

def extract_rpps(text):
    rpps_regex = r'\b(\d{3}\s?\d{3}\s?\d{3}\s?\d{2})\b'
    rpps_numbers = re.findall(rpps_regex, text)
    unique_rpps = list(set(rpps.replace(" ", "") for rpps in rpps_numbers))
    for rpps in unique_rpps:
        text = text.replace(rpps, "A")
    return unique_rpps, text

def extract_postal_codes(text):
    postal_code_regex = r'\b\d{5}\b'
    postal_codes = re.findall(postal_code_regex, text)
    unique_postal_codes = list(set(postal_codes))
    for postal_code in unique_postal_codes:
        text = text.replace(postal_code, "A")
    return unique_postal_codes, text

def extract_percentages(text):
    percentage_regex = r'(100|[1-9]?[0-9]) ?%'
    percentages = re.findall(percentage_regex, text)
    unique_percentages = list(set(f"{percentage}%" for percentage in percentages))
    for percentage in unique_percentages:
        text = text.replace(percentage, "A")
    return unique_percentages, text

def extract_montants(text):
    montant_regex = r'\d{1,3}(?:[ ]\d{3})*[.,]\d{2} ?[€]?'
    montants = re.findall(montant_regex, text)
    montants_numeriques = []

    for montant in montants:
        montant_clean = montant.replace(" ", "").replace(",", ".").replace("€", "")
        try:
            montants_numeriques.append(float(montant_clean))
        except ValueError:
            continue

    somme_montants = sum(montants_numeriques)
    unique_montants = list(set(montants))
    for montant in unique_montants:
        text = text.replace(montant, "A")
    return unique_montants, somme_montants, text

def extract_telephone(text):
    num_tel_regex = r'\b0[1-9](?:\.\d{2}){4}\b'
    num_tels = re.findall(num_tel_regex, text)
    unique_num_tels = list(set(num_tels))
    for num_tel in unique_num_tels:
        text = text.replace(num_tel, "A")
    return unique_num_tels, text