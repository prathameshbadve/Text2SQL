
from ollama import chat
from ollama import ChatResponse

def query_llm(user_prompt, model='llama3.2'):

  response: ChatResponse = chat(model=model, messages=[
    {
      'role': 'user',
      'content': f'{user_prompt}. Only give the sql query and no other explanation. I only want one query, no other plain text',
    },
  ])

  return response



# or access fields directly from the response object
# print(response.message.content)