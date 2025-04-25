"""
Module implémentant l'outil de recherche Google Scholar pour les agents Google ADK.
Permet d'effectuer des recherches académiques et de récupérer 15 résultats en français.
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Charger les variables d'environnement
load_dotenv()

# Clé API pour SerpAPI (à configurer dans le fichier .env)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def _format_scholar_results(raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Formate les résultats bruts de SerpAPI en un format standardisé.
    
    Args:
        raw_results: Réponse JSON brute de l'API SerpAPI
        
    Returns:
        Liste d'articles académiques formatés
    """
    formatted_results = []
    
    # Vérifier si les résultats contiennent des articles organiques
    if "organic_results" in raw_results:
        for article in raw_results["organic_results"]:
            # Créer un dictionnaire pour chaque article avec les informations disponibles
            article_data = {
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "snippet": article.get("snippet", ""),
                "publication_info": article.get("publication_info", {}).get("summary", ""),
                "year": article.get("publication_info", {}).get("year", ""),
                "authors": article.get("publication_info", {}).get("authors", []),
                "citations": article.get("inline_links", {}).get("cited_by", {}).get("total", 0),
                "result_id": article.get("result_id", "")
            }
            
            # Ajouter les versions PDF si disponibles
            if "resources" in article:
                for resource in article["resources"]:
                    if resource.get("file_format", "") == "PDF":
                        article_data["pdf_link"] = resource.get("link", "")
                        break
            
            formatted_results.append(article_data)
    
    return formatted_results

def scholar_search(query: str, num_results: int = 15) -> Dict[str, Any]:
    """
    Effectue une recherche sur Google Scholar en français et retourne les résultats formatés.
    
    Args:
        query: La requête de recherche académique
        num_results: Nombre de résultats à retourner (par défaut 15)
        
    Returns:
        Dictionnaire contenant les résultats formatés et des métadonnées sur la recherche
    """
    # Vérifier si la clé API est disponible
    if not SERPAPI_KEY:
        return {
            "status": "error",
            "message": "Clé API SerpAPI non configurée. Veuillez ajouter SERPAPI_KEY dans le fichier .env",
            "results": []
        }
    
    # Limiter le nombre de résultats entre 1 et 20
    num_results = max(1, min(num_results, 20))
    
    # Construire les paramètres de recherche pour SerpAPI
    params = {
        "engine": "google_scholar",
        "q": query,
        "hl": "fr",              # Langue d'interface en français
        "lr": "lang_fr",         # Limiter aux résultats en français
        "num": num_results,      # Nombre de résultats demandés
        "api_key": SERPAPI_KEY
    }
    
    try:
        # Effectuer la requête à l'API SerpAPI
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()  # Lever une exception si le statut HTTP indique une erreur
        
        # Analyser la réponse JSON
        results = response.json()
        
        # Formater les résultats
        formatted_results = _format_scholar_results(results)
        
        # Construire la réponse
        search_response = {
            "status": "success",
            "query": query,
            "langue": "français",
            "nombre_resultats": len(formatted_results),
            "resultats": formatted_results
        }
        
        # Ajouter les informations de pagination si disponibles
        if "pagination" in results:
            search_response["pagination"] = results["pagination"]
        
        # Ajouter les informations sur les filtres de recherche si disponibles
        if "search_metadata" in results:
            search_response["metadata"] = results["search_metadata"]
            
        return search_response
        
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        return {
            "status": "error",
            "message": f"Erreur lors de la requête: {str(e)}",
            "results": []
        }
    except json.JSONDecodeError:
        # Gérer les erreurs de parsing JSON
        return {
            "status": "error",
            "message": "Erreur lors du décodage de la réponse JSON",
            "results": []
        }
    except Exception as e:
        # Gérer les autres erreurs
        return {
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}",
            "results": []
        }

# Définition de l'outil au format Google ADK Agents
scholar_search_schema = {
    "name": "scholar_search",
    "description": """
    Recherche académique sur Google Scholar en français.
    
    Cet outil est conçu pour:
    - Rechercher des articles scientifiques et académiques
    - Trouver des publications évaluées par les pairs
    - Accéder à la littérature savante en français
    - Identifier des travaux de recherche sur un sujet spécifique
    - Trouver des citations et références académiques
    
    Les résultats incluent des informations détaillées sur chaque publication,
    comme les auteurs, l'année de publication, le nombre de citations, et
    des liens vers les textes intégraux lorsqu'ils sont disponibles.
    
    Utilisez cet outil pour:
    - Approfondir les recherches après avoir établi un contexte général
    - Identifier les travaux académiques de référence sur un sujet
    - Trouver des articles scientifiques récents en français
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "La requête de recherche académique"
            },
            "num_results": {
                "type": "integer",
                "description": "Nombre de résultats à retourner (entre 1 et 20)",
                "default": 15,
                "minimum": 1,
                "maximum": 20
            }
        },
        "required": ["query"]
    }
}