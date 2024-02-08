from llama_index.llms import OpenAI, MistralAI

def get_model(llm, api_key=None):

    if llm.lower() == "gpt-3.5-turbo":
        return OpenAI(model = "gpt-3.5-turbo", temperature=0)

    
    if llm.lower() == "gpt-4":
        return OpenAI(model = "gpt-4", temperature=0)

    
    if llm.lower() == "mistralai":
        return MistralAI(api_key=api_key)

    