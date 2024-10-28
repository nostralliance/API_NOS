from mylib_montant import functions
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
import easyocr
import uvicorn

app = FastAPI()

# Modèle de requête pour recevoir le chemin du fichier
class FileRequest(BaseModel):
    docid: str

# Route pour traiter le fichier
@app.post("/process_file")
async def process_file(request: FileRequest):
    file_path = request.docid

    # Vérification que le fichier existe
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Le fichier n'existe pas")

    # Vérification du type de fichier (PDF ou image)
    file_extension = os.path.splitext(file_path)[1].lower()

    final_text = ""
    if file_extension == '.pdf':
        # Convertir le PDF en images
        images = functions.pdf2img(file_path)  # Fonction existante pour la conversion
        ocr_results = []
        reader = easyocr.Reader(['fr'])
        
        # Appliquer l'OCR sur chaque image
        for image in images:
            text = " ".join(reader.readtext(image, detail=0))  # Extraire le texte de chaque image
            # print(f'le texte est : {text}')
            ocr_results.append(text)
        final_text = " ".join(ocr_results)  # Concatenation du texte extrait

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        reader = easyocr.Reader(['fr'])
        final_text = " ".join(reader.readtext(file_path, detail=0))  # Extraire le texte

    else:
        raise HTTPException(status_code=400, detail="Type de fichier non supporté. Utilisez un PDF ou une image.")

    # Détection et suppression des éléments dans le texte extrait
    dates, final_text = functions.extract_dates(final_text)
    siren, final_text = functions.extract_siren(final_text)
    siret, final_text = functions.extract_siret(final_text)
    postal_codes, final_text = functions.extract_postal_codes(final_text)
    percentages, final_text = functions.extract_percentages(final_text)
    montants,somme_montants, final_text = functions.extract_montants(final_text)

    # Retourner les résultats dans un format JSON
    return {
        "dates": ["/".join(date) for date in dates],  # Reformater les dates pour être lisibles
        "siren": siren,  # Prendre seulement les numéros Siren
        "siret": siret,  # Prendre seulement les numéros Siret
        "postal_codes": postal_codes,
        "percentages": percentages,
        "montants": montants + [f'somme des montants :{somme_montants}']
        
    }

# Démarrage automatique de l'application avec Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
