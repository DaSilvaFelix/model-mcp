from dotenv import load_dotenv
import os

load_dotenv()


def getVar(key: str) -> str:

    val = os.getenv(key)
        
    if val is None or val == "":
        raise Exception(f"No hay variable de entorno '{key}'")
        
    return val