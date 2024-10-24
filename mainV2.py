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

    if file_extension == '.pdf':
        # Convertir le PDF en images
        images = functions.pdf2img(file_path)  # Fonction existante pour la conversion
        reader = easyocr.Reader(['fr'])
        
        results_per_page = {}
        page_number = 1  # Initialiser un compteur de page
        
        # Appliquer l'OCR et extraire les données pour chaque page
        for image in images:
            text = " ".join(reader.readtext(image, detail=0))  # Extraire le texte de chaque page
            
            # Détection et suppression des éléments dans le texte extrait pour chaque page
            page_data = {}
            raw_dates, text = functions.extract_dates(text)
            page_data['dates']= ["/".join(date) for date in raw_dates]  # Formatage des dates en "DD/MM/YYYY" 
            page_data['siren'], text = functions.extract_siren(text)
            page_data['siret'], text = functions.extract_siret(text)
            page_data['postal_codes'], text = functions.extract_postal_codes(text)
            page_data['percentages'], text = functions.extract_percentages(text)
            montants, somme_montants, text = functions.extract_montants(text)            
            page_data['montants'] = montants
            page_data['somme_montants'] = somme_montants
            
            # Ajouter les résultats de cette page dans le dictionnaire global avec un nom de page unique
            results_per_page[f"page{page_number}"] = page_data
            page_number += 1  # Incrémenter le compteur de page

        # Retourner les résultats par page dans un format JSON
        return results_per_page

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        reader = easyocr.Reader(['fr'])
        text = " ".join(reader.readtext(file_path, detail=0))  # Extraire le texte de l'image

        # Détection et suppression des éléments dans le texte extrait
        page_data = {}
        raw_dates, text = functions.extract_dates(text)
        page_data['dates']= ["/".join(date) for date in raw_dates]  # Formatage des dates en "DD/MM/YYYY"
        page_data['siren'], text = functions.extract_siren(text)
        page_data['siret'], text = functions.extract_siret(text)
        page_data['postal_codes'], text = functions.extract_postal_codes(text)
        page_data['percentages'], text = functions.extract_percentages(text)
        montants, somme_montants, text = functions.extract_montants(text)
        page_data['montants'] = montants
        page_data['somme_montants'] = somme_montants

        # Retourner les résultats pour une seule page sous le nom "page1"
        return {"page1": page_data}

    else:
        raise HTTPException(status_code=400, detail="Type de fichier non supporté. Utilisez un PDF ou une image.")

# Démarrage automatique de l'application avec Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
