import os
import json
import google.generativeai as genai
import requests

# Konfiguracja klucza API
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

# Pobieranie listy ustaw
url = "https://api.sejm.gov.pl/eli/acts/DU/2026"
acts = requests.get(url).json().get('items', [])
act = acts[-1]

# Prompt dla AI
prompt = f"Analizuj akt prawny: {act['title']}. W odpowiedzi podaj tylko czysty JSON z polami: old_text, new_text, effective_date."
response = model.generate_content(prompt)

# Ekstrakcja czystego JSON-a (usuwamy zbędne znaczniki, jeśli AI je dodało)
text = response.text.replace('json', '').replace('
```', '').strip()

# Zapis do pliku
try:
    data = json.loads(text)
    final_data = [{
        'id': f"DU_{act['year']}_{act['pos']}",
        'title': act['title'],
        'old_text': data.get('old_text', 'Brak danych'),
        'new_text': data.get('new_text', 'Brak danych'),
        'effective_date': data.get('effective_date', 'Brak danych')
    }]
    with open('zmiany_prawne.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("Sukces: Dane zapisane do zmiany_prawne.json")
except Exception as e:
    print(f"Błąd parsowania JSON: {e}")
