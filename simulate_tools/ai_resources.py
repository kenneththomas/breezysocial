from openai import OpenAI
import maricon

client = OpenAI(api_key=maricon.gptkey)

def chatgpt(prompt, gpt_version='gpt-4o-mini'):
    response = client.chat.completions.create(
        model=gpt_version,
        messages=prompt,
        max_tokens=100,
        temperature=0.9,
        presence_penalty=0.8
    )

    print(response)
    
    generated_text = response.choices[0].message.content.strip()

    return generated_text