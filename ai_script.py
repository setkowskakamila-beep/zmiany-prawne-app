import os, json, google.generativeai as genai, requests
from datetime import datetime

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

acts = requests.get('https://api.sejm.gov.pl/eli/acts/DU/2026').json().get('items', [])
act = acts[-1]
response = model.generate_content(f"Analizuj akt: {act['title']}. Daj JSON: old_text, new_text, effective_date.")
data = json.loads(response.text.replace('
```json','').replace('```','').strip())

with open('zmiany_prawne.json', 'w', encoding='utf-8') as f:
    json.dump([{'id': 'DU_2026', 'title': act['title'], **data}], f, ensure_ascii=False, indent=4)
