from mylib_montant import functions
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
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

    results_by_page = {}
    if file_extension == '.pdf':
        # Convertir le PDF en images
        images = functions.pdf2img(file_path)  # Fonction existante pour la conversion
        reader = easyocr.Reader(['fr'])

        # Appliquer l'OCR sur chaque image
        for index, image in enumerate(images):
            final_text = " ".join(reader.readtext(image, detail=0))  # Extraire le texte de chaque image

            # Détection et suppression des éléments dans le texte extrait
            dates, final_text = functions.extract_dates(final_text)
            siren, final_text = functions.extract_siren(final_text)
            siret, final_text = functions.extract_siret(final_text)
            postal_codes, final_text = functions.extract_postal_codes(final_text)
            percentages, final_text = functions.extract_percentages(final_text)
            montants, somme_montants, final_text = functions.extract_montants(final_text)

            # Stocker les résultats dans une structure par page
            results_by_page[f"page{index + 1}"] = {
                "dates": ["/".join(date) for date in dates],  # Reformater les dates pour être lisibles
                "siren": siren,  # Prendre seulement les numéros Siren
                "siret": siret,  # Prendre seulement les numéros Siret
                "postal_codes": postal_codes,
                "percentages": percentages,
                "montants": montants + [f'somme des montants : {somme_montants}']
            }

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # Appliquer l'OCR sur une image
        reader = easyocr.Reader(['fr'])
        final_text = " ".join(reader.readtext(file_path, detail=0))  # Extraire le texte

        # Détection et suppression des éléments dans le texte extrait
        dates, final_text = functions.extract_dates(final_text)
        siren, final_text = functions.extract_siren(final_text)
        siret, final_text = functions.extract_siret(final_text)
        postal_codes, final_text = functions.extract_postal_codes(final_text)
        percentages, final_text = functions.extract_percentages(final_text)
        montants, somme_montants, final_text = functions.extract_montants(final_text)

        # Ajouter les résultats dans une seule page
        results_by_page["page1"] = {
            "dates": ["/".join(date) for date in dates],  # Reformater les dates pour être lisibles
            "siren": siren,
            "siret": siret,
            "postal_codes": postal_codes,
            "percentages": percentages,
            "montants": montants + [f'somme des montants : {somme_montants}']
        }

    else:
        raise HTTPException(status_code=400, detail="Type de fichier non supporté. Utilisez un PDF ou une image.")

    # Retourner les résultats dans un format JSON organisé par pages
    return results_by_page  # Renvoie les résultats avec des clés page1, page2, etc.

# Démarrage automatique de l'application avec Uvicorn
if __name__ == "__main__":
    uvicorn.run("mainV2:app", host="0.0.0.0", port=8001, reload=True)
