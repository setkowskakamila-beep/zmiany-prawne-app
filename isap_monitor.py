import os, json, google.generativeai as genai, requests
from datetime import datetime

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze(title):
    print(f"DEBUG: Wysyłam do AI: {title}")
    prompt = f"Analizuj tytuł: '{title}'. Wyodrębnij JSON z polami: 'old_text', 'new_text', 'effective_date'. Jeśli brak danych, wpisz 'Brak'. Odpowiedz tylko czystym JSON."
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace("
```json", "").replace("```", "").strip())
    except:
        return {"old_text": "Brak", "new_text": "Brak", "effective_date": "Brak"}

def main():
    print("START")
    response = requests.get(f"https://api.sejm.gov.pl/eli/acts/DU/{datetime.now().year}")
    acts = response.json().get('items', [])
    db = []
    # Przetwarzamy 1 najnowszą ustawę na test
    act = acts[-1]
    print(f"Analizuję przez AI: {act['title']}")
    ai_data = analyze(act['title'])
    db.append({"id": f"DU_{act['year']}_{act['pos']}", "title": act['title'], **ai_data})
    
    with open("zmiany_prawne.json", 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("KONIEC")

if __name__ == "__main__":
    main()
