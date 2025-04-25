from langchain_community.tools import BraveSearch
from dotenv import load_dotenv

load_dotenv()
import os

# Charger la clé API depuis les variables d'environnement
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
# Initialiser l'outil de recherche BraveSearch
search_tool = BraveSearch.from_api_key(
    api_key=BRAVE_API_KEY, 
    search_kwargs={"count": 10}  # 10 résultats par défaut
)