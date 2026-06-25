import google.generativeai as genai

API_KEY = "AQ.Ab8RN6LBu3QPY0yZTOrr0xMrZZJgEO2lQkd-PYtrHQvLnGZ83g"

genai.configure(api_key=API_KEY)

for model in genai.list_models():
    print(model.name)