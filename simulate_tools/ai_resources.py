import openai
import maricon

openai.api_key = maricon.gptkey

def chatgpt(prompt,gpt_version='gpt-4o-mini'):

    #full_prompt = [{"role": "user", "content": f"{prompt}"}]

    response = openai.ChatCompletion.create(
    model=gpt_version,
    max_tokens=100,
    temperature=.9,
    presence_penalty=0.8,

    messages = prompt)

    print(response)
    
    generated_text = response.choices[0].message.content.strip()

    return generated_text