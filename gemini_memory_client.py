import os
import json
import requests
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MEMORY_API_URL = "http://127.0.0.1:8000"

genai.configure(api_key=GEMINI_API_KEY)

# Function declarations for Gemini
memory_functions = [
    {
        "name": "add_memory",
        "description": "Store a new memory in the shared memory system",
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Project identifier (e.g., 'gemini', 'chatgpt', 'claude')"
                },
                "content": {
                    "type": "string",
                    "description": "The memory content to store"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization"
                }
            },
            "required": ["project", "content"]
        }
    },
    {
        "name": "search_memory",
        "description": "Search for memories by query string",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant memories"
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of results to return (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_memories",
        "description": "List all memories, optionally filtered by project",
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Filter by project name"
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of results (default: 50)"
                }
            }
        }
    },
    {
        "name": "update_memory",
        "description": "Update an existing memory by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "Memory ID to update"
                },
                "content": {
                    "type": "string",
                    "description": "New content"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New tags"
                }
            },
            "required": ["memory_id"]
        }
    },
    {
        "name": "delete_memory",
        "description": "Delete a memory by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "Memory ID to delete"
                }
            },
            "required": ["memory_id"]
        }
    }
]

# Execute function calls
def execute_function(function_name, function_args):
    """Execute the actual API calls"""
    
    if function_name == "add_memory":
        response = requests.post(
            f"{MEMORY_API_URL}/memory/add",
            json=function_args
        )
        return response.json()
    
    elif function_name == "search_memory":
        response = requests.get(
            f"{MEMORY_API_URL}/memory/search",
            params=function_args
        )
        return response.json()
    
    elif function_name == "list_memories":
        response = requests.get(
            f"{MEMORY_API_URL}/memory/list",
            params=function_args
        )
        return response.json()
    
    elif function_name == "update_memory":
        memory_id = function_args.pop('memory_id')
        response = requests.put(
            f"{MEMORY_API_URL}/memory/update/{memory_id}",
            json=function_args
        )
        return response.json()
    
    elif function_name == "delete_memory":
        memory_id = function_args['memory_id']
        response = requests.delete(
            f"{MEMORY_API_URL}/memory/delete/{memory_id}"
        )
        return response.json()
    
    else:
        return {"error": f"Unknown function: {function_name}"}

# Main chat function
def chat_with_memory(user_message, chat_history=None):
    """
    Chat with Gemini with memory access
    """
    if chat_history is None:
        chat_history = []
    
    # Initialize model with function declarations
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',
        tools=memory_functions
    )
    
    # Start chat session
    chat = model.start_chat(history=chat_history)
    
    # Send user message
    response = chat.send_message(user_message)
    
    # Check if function calls are needed
    while response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        print(f"🔧 Calling function: {function_name}")
        print(f"📋 Arguments: {json.dumps(function_args, indent=2)}")
        
        # Execute the function
        function_result = execute_function(function_name, function_args)
        
        print(f"✅ Result: {json.dumps(function_result, indent=2)}\n")
        
        # Send function result back to model
        response = chat.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=function_name,
                        response={"result": function_result}
                    )
                )]
            )
        )
    
    # Return final text response
    return response.text, chat.history

# Interactive chat loop
def main():
    print("🤖 Gemini Memory Assistant")
    print("Type 'quit' to exit\n")
    
    chat_history = []
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            response_text, chat_history = chat_with_memory(user_input, chat_history)
            print(f"\nGemini: {response_text}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()