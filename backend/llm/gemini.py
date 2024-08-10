import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'), transport='rest')


def chat(text):
    # 注意这行代码，官方提供的demo没有transport='rest' 会出现超时问题，因此一定要加上
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(text, stream=True)
    for chunk in response:
        print(chunk.text, end='', flush=True)
