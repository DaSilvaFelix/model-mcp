from langchain_core.tools import tool

@tool
def calcLen(text: str) -> int:
    """Calcula longitud de texto. Úsala siempre."""
    print(f"   🛠️ [Tool] Midiendo: '{text}'")
    return len(text)

# Lista exportable de herramientas
toolList = [calcLen]