import requests
import json
import os
from datetime import datetime

# Konfiguracja
API_URL = "https://api.sejm.gov.pl/eli/acts/DU/"
CURRENT_YEAR = datetime.now().year
DB_FILE = "zmiany_prawne.json"

def load_local_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def fetch_acts():
    try:
        response = requests.get(f"{API_URL}{CURRENT_YEAR}", timeout=10)
        return response.json().get('items', [])
    except:
        return []

def analyze_act(act):
    title = act.get('title', '')
    pos = act.get('pos', '')
    year = act.get('year', '')
    
    # Filtrujemy tylko nowelizacje
    if "zmieniająca" not in title.lower():
        return None
    
    # Tworzymy strukturę danych dla aplikacji
    return {
        "id": f"DU_{year}_{pos}",
        "title": title,
        "source_url": f"https://eli.gov.pl/eli/DU/{year}/{pos}/ogl",
        "publication_date": act.get('promulgation', ''),
        "old_text": "Treść przepisu sprzed zmiany znajduje się w oficjalnym źródle.",
        "new_text": "Nowe brzmienie przepisu zostało opublikowane w powyższym akcie prawnym.",
        "effective_date": "Zgodnie z treścią ustawy"
    }

def main():
    existing_db = load_local_db()
    existing_ids = {item['id'] for item in existing_db}
    
    acts = fetch_acts()
    new_entries = []
    
    for act in acts:
        entry = analyze_act(act)
        if entry and entry['id'] not in existing_ids:
            new_entries.append(entry)
    
    if new_entries:
        existing_db.extend(new_entries)
        # Sortowanie od najnowszych
        existing_db = sorted(existing_db, key=lambda x: x['id'], reverse=True)
        
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_db, f, ensure_ascii=False, indent=4)
        print(f"Dodano {len(new_entries)} nowych aktów.")
    else:
        print("Brak nowych aktów.")

if __name__ == "__main__":
    main()
