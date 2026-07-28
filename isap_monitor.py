import requests
import json
import os
import re
from datetime import datetime

# Konfiguracja podstawowa
API_URL = "https://api.sejm.gov.pl/eli/acts/DU/" # Baza Dziennika Ustaw poprzez ELI API
CURRENT_YEAR = datetime.now().year # Dynamicznie pobiera obecny rok (np. 2026)
DB_FILE = "zmiany_prawne.json" # Plik, z którego będzie korzystać aplikacja mobilna

# Słownik do przechowywania pobranych zmian
legal_changes_db = []

# Funkcja pomocnicza do ładowania istniejącej lokalnej bazy
def load_local_db():
    global legal_changes_db
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                legal_changes_db = json.load(f)
                print(f"[*] Załadowano lokalną bazę: {len(legal_changes_db)} wpisów.")
        except json.JSONDecodeError:
            print("[!] Błąd odczytu bazy lokalnej, tworzę nową pusto bazę.")
            legal_changes_db = []
    else:
        print("[*] Nie znaleziono lokalnej bazy, zaczynamy od zera.")

def fetch_recent_acts():
    """
    Pobiera najnowsze akty prawne z Dziennika Ustaw z bieżącego roku, 
    korzystając z oficjalnego API Sejmowego.
    """
    print(f"[*] Odpytuję bazę ISAP (Dziennik Ustaw) dla roku {CURRENT_YEAR}...")
    
    url = f"{API_URL}{CURRENT_YEAR}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        items = data.get('items', [])
        print(f"[*] Pobrano listę {len(items)} dokumentów z {CURRENT_YEAR} r.")
        return items
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Błąd połączenia z API ISAP: {e}")
        return []

def analyze_and_extract(act):
    """
    Analizuje pojedynczy akt prawny, aby zdecydować czy jest to "zmiana/nowelizacja".
    """
    title = act.get('title', '')
    pos = act.get('pos', '')
    year = act.get('year', '')
    
    # Filtrujemy tylko akty zmieniające przepisy
    if "zmieniająca ustawę" not in title.lower() and "zmieniające rozporządzenie" not in title.lower():
        return None 
    
    source_url = f"https://eli.gov.pl/eli/DU/{year}/{pos}/ogl"
    
    change_entry = {
        "id": f"DU_{year}_{pos}", 
        "title": title,
        "source_url": source_url,
        "publication_date": act.get('promulgation', ''),
        "old_text": "Trwa analiza starego brzmienia...",
        "new_text": "Zarejestrowano nowelizację. Wejdź w link źródłowy, aby zapoznać się ze szczegółami dokumentu opublikowanego przez rząd.",
        "effective_date": "Sprawdź źródło (zazwyczaj 14 dni)"
    }
    return change_entry

def update_database(new_items):
    """
    Porównuje pobrane akty z lokalną bazą i zapisuje tylko nowe.
    """
    global legal_changes_db
    
    existing_ids = {entry['id'] for entry in legal_changes_db}
    added_count = 0
    
    for item in new_items:
        extracted = analyze_and_extract(item)
        if extracted and extracted['id'] not in existing_ids:
            legal_changes_db.append(extracted)
            added_count += 1
            print(f" -> Nowa nowelizacja: {extracted['title'][:60]}...")
            
    if added_count > 0:
        legal_changes_db = sorted(legal_changes_db, key=lambda x: x['id'], reverse=True)
        
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(legal_changes_db, f, ensure_ascii=False, indent=4)
        print(f"[*] Baza zaktualizowana! Zapisano do pliku {DB_FILE}. Dodano {added_count} nowych pozycji.")
    else:
        print("[*] Brak nowych nowelizacji od ostatniego sprawdzenia.")


def main():
    print("--- Uruchamianie monitora ISAP (ELI) ---")
    load_local_db()
    recent_acts = fetch_recent_acts()
    
    if recent_acts:
        update_database(recent_acts)
        
    print("--- Zakończono ---")

if __name__ == "__main__":
    main()
