import os, json, google.generativeai as genai, requests
from datetime import datetime

# Konfiguracja AI
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

DB_FILE = "zmiany_prawne.json"

def analyze_act_with_ai(title):
    prompt = f"Analizuj akt prawny o tytule: '{title}'. Wyodrębnij: 'old_text' (brzmienie przed zmianą), 'new_text' (brzmienie po zmianie), 'effective_date' (data wejścia w życie). Odpowiedz WYŁĄCZNIE czystym JSON-em bez formatowania markdown."
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace("
```json", "").replace("```", ""))
    except:
        return {"old_text": "Brak danych", "new_text": "Brak danych", "effective_date": "Nieznana"}

# ... (Reszta logiki pobierania aktów z ISAP tak jak wcześniej)
# W pętli głównej skryptu dodaj:
# ai_data = analyze_act_with_ai(act['title'])
# entry.update(ai_data)
