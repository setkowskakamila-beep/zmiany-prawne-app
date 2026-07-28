import os, json, google.generativeai as genai, requests
from datetime import datetime

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

acts = requests.get('https://api.sejm.gov.pl/eli/acts/DU/2026').json().get('items', [])
act = acts[-1]

response = model.generate_content(f"Analizuj akt: {act['title']}. Daj wynik w JSON z polami: old_text, new_text, effective_date.")

# Używamy potrójnego cudzysłowu dla replace, aby było bezpiecznie
raw_text = response.text.replace('
```json', '').replace('```', '').strip()
data = json.loads(raw_text)

with open('zmiany_prawne.json', 'w', encoding='utf-8') as f:
    json.dump([{'id': f"DU_{act['year']}_{act['pos']}", 'title': act['title'], **data}], f, ensure_ascii=False, indent=4)
