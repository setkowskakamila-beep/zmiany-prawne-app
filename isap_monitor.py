import os
import json
import google.generativeai as genai
import requests
from datetime import datetime

# Konfiguracja API - używamy oryginalnych angielskich komend
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

DB_FILE = "zmiany_prawne.json"

def analyze_act_with_ai(title):
    prompt = f"Analizuj akt prawny: '{title}'. Wyodrębnij JSON z polami: 'old_text', 'new_text', 'effective_date'. Odpowiedz tylko czystym JSONem."
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("
```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"old_text": "Analiza AI nie powiodła się", "new_text": "Sprawdź źródło", "effective_date": "Nieznana"}

def main():
    response = requests.get(f"https://api.sejm.gov.pl/eli/acts/DU/{datetime.now().year}")
    acts = response.json().get('items', [])
    
    db = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)
            
    existing_ids = {i['id'] for i in db}
    
    for act in acts[-5:]: 
        act_id = f"DU_{act['year']}_{act['pos']}"
        if act_id not in existing_ids and "zmieniająca" in act['title'].lower():
            ai_data = analyze_act_with_ai(act['title'])
            db.append({
                "id": act_id,
                "title": act['title'],
                "source_url": f"https://eli.gov.pl/eli/DU/{act['year']}/{act['pos']}/ogl",
                "old_text": ai_data.get('old_text'),
                "new_text": ai_data.get('new_text'),
                "effective_date": ai_data.get('effective_date')
            })
            
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
