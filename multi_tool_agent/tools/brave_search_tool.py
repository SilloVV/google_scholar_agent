from langchain_community.tools import BraveSearch
from dotenv import load_dotenv
import json
from typing import Dict, Any, List, Optional

load_dotenv()
import os

# Charger la clé API depuis les variables d'environnement
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

# Initialiser l'outil de recherche BraveSearch sous-jacent
_brave_search_engine = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, 
    search_kwargs={"count": 10}  # 10 résultats par défaut
)

def _extract_search_results(response_text: str) -> List[Dict[str, str]]:
    """
    Extrait et normalise les résultats de recherche à partir de la réponse.
    Gère à la fois les formats JSON et texte.
    """
    try:
        # Tenter de parser comme JSON
        results_data = json.loads(response_text)
        
        # Format possible 1: Liste directe de résultats
        if isinstance(results_data, list):
            return [
                {
                    "title": item.get("title", ""),
                    "link": item.get("url", "") or item.get("link", ""),
                    "snippet": item.get("description", "") or item.get("snippet", ""),
                }
                for item in results_data
                if isinstance(item, dict)
            ]
            
        # Format possible 2: Objet avec clé "web" contenant "results"
        elif isinstance(results_data, dict) and "web" in results_data and "results" in results_data["web"]:
            return [
                {
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("description", ""),
                }
                for item in results_data["web"]["results"]
            ]
            
        # Format inconnu mais valide JSON
        return [{"raw_result": str(results_data)}]
        
    except json.JSONDecodeError:
        # Si ce n'est pas du JSON, on renvoie le texte brut
        return [{"raw_result": response_text}]

def brave_search(query: str, count: int = 10) -> Dict[str, Any]:
    """
    Effectue une recherche web via l'API Brave Search et renvoie les résultats formatés.
    
    Args:
        query: La requête de recherche
        count: Nombre de résultats à retourner (max 20)
        
    Returns:
        Dictionnaire contenant les résultats de recherche formatés
    """
    # Ajuster count pour respecter les limites
    count = min(max(1, count), 20)
    
    try:
        # Effectuer la recherche avec l'outil BraveSearch sous-jacent
        raw_results = _brave_search_engine.run(query, search_kwargs={"count": count})
        
        # Extraire et normaliser les résultats
        formatted_results = _extract_search_results(raw_results)
        
        # Construire la réponse finale
        response = {
            "query": query,
            "results": formatted_results,
            "totalResults": len(formatted_results),
            "status": "success"
        }
    except Exception as e:
        # Gérer les erreurs potentielles
        response = {
            "query": query,
            "results": [],
            "totalResults": 0,
            "status": "error",
            "error": str(e)
        }
    
    return response

# Définition de l'outil au format Google ADK Agents
brave_search_schema = {
    "name": "brave_search",
    "description": """
    Recherche d'informations générales sur le web avec Brave Search.
    
    Cet outil est idéal pour:
    - Obtenir des informations générales sur un sujet
    - Rechercher des articles récents et de l'actualité
    - Trouver des articles de vulgarisation scientifique
    - Identifier les sites web pertinents pour un sujet donné
    - Explorer la littérature grise et les ressources non académiques
    
    Utilisez cet outil en premier pour établir le contexte général avant d'approfondir 
    avec des recherches académiques plus spécifiques.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "La requête de recherche à effectuer"
            },
            "count": {
                "type": "integer", 
                "description": "Nombre de résultats à retourner (entre 1 et 20)",
                "default": 10,
                "minimum": 1,
                "maximum": 20
            }
        },
        "required": ["query"]
    }
}