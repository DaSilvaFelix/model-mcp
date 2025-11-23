import os
import importlib
import inspect
from pathlib import Path
from langchain_core.tools import BaseTool

tools_dir = Path(__file__).parent

mainTools = []

for file in tools_dir.glob("*Tools.py"):
    module_name = file.stem
    
    try:
        module = importlib.import_module(f"src.tools.{module_name}")
        
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, BaseTool):
                mainTools.append(obj)
                print(f"✅ Herramienta '{obj.name}' implementada correctamente. El modelo ya puede usar esta herramienta.")
    
    except Exception as e:
        print(f"❌ Error al cargar herramientas desde {module_name}: {e}")

print(f"\n📦 Total de herramientas cargadas: {len(mainTools)}")
