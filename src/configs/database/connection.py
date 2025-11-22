from pymongo import MongoClient
from src.configs.environment.var import getVar

def connect():
    try:
        client = MongoClient(getVar("URL_DATABASE"))
        
        client.admin.command("ping")
        
        return client[getVar("DATABASE_NAME")]
    
    except Exception as e:
    
        raise RuntimeError(f"No se pudo conectar a MongoDB: {e}") from e
