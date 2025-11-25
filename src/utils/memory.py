from langchain_core.messages import HumanMessage, AIMessage

def convertMemoryToMessages(memory_data):
    messages = []
    for item in memory_data:
        role = item.get("role")
        text = item.get("text")
        
        if role == "user":
            messages.append(HumanMessage(content=text))
        elif role == "ai":
            messages.append(AIMessage(content=text))
            
    return messages
