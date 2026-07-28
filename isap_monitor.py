import os, json, google.generativeai as genai, requests
from datetime import datetime

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

DB_FILE = "zmiany_prawne.json"

def analyze_with_ai(title):
    prompt = f"Analizuj akt prawny: '{title}'. Wyodrębnij JSON z polami: 'old_text', 'new_text', 'effective_date'. Jeśli brak danych, wpisz 'Brak danych'. Odpowiedz TYLKO czystym JSON-em."
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("
```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {"old_text": "Brak danych", "new_text": "Brak danych", "effective_date": "Nieznana"}

def main():
    # Pobierz listę ustaw
    response = requests.get(f"https://api.sejm.gov.pl/eli/acts/DU/{datetime.now().year}")
    acts = response.json().get('items', [])
    
    # Wczytaj bazę
    db = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = []
            
    existing_ids = {i['id'] for i in db}
    
    # Przetwórz tylko 5 najnowszych (żeby nie przekroczyć limitów AI na start)
    for act in acts[-10:]: 
        act_id = f"DU_{act['year']}_{act['pos']}"
        if act_id not in existing_ids and "zmieniająca" in act['title'].lower():
            print(f"Analizuję przez AI: {act['title']}")
            ai_data = analyze_with_ai(act['title'])
            db.append({
                "id": act_id,
                "title": act['title'],
                "source_url": f"https://eli.gov.pl/eli/DU/{act['year']}/{act['pos']}/ogl",
                **ai_data
            })
            
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
