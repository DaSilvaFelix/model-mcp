from langchain_core.messages import HumanMessage, AIMessage

def convertMemoryToMessages(memory_data):
    messages = []
    for item in memory_data:
        role = item.get("role")
        text = item.get("text")
        
        if role == "user":
            messages.append(HumanMessage(content=text))
        elif role == "ai":
            # Handle nested dictionary for AI messages if present
            if isinstance(text, dict) and "message" in text:
                content = text["message"]
            else:
                content = str(text)
            messages.append(AIMessage(content=content))
            
    return messages
