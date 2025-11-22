from fastapi import FastAPI 
from src.configs.database.connection import connect
from rich import print

app = FastAPI()

try:
	connect()
	print("\n ✅ coneccion de la base de datos realizadas correctamente \n")
except Exception as e:
	print(e)