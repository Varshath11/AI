import google.generativeai as genai

API_KEY = "AQ.Ab8RN6LBu3QPY0yZTOrr0xMrZZJgEO2lQkd-PYtrHQvLnGZ83g"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content(
    "Give a roadmap for a first year ECE student interested in AI."
)

print(response.text)