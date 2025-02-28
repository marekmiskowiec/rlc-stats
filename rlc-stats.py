import re
import requests
import gspread
import json
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import pytz

# 1. Wczytaj zmienne środowiskowe z .env (lokalnie)
load_dotenv()

# 2. Pobierz klucz z .env lub GitHub Secrets
google_credentials = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

if not google_credentials:
    raise ValueError("❌ Nie znaleziono zmiennej GOOGLE_SHEETS_CREDENTIALS!")

# 3. Parsowanie klucza (z string na dict)
creds_dict = json.loads(google_credentials)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
print(creds_dict["private_key"] )
print(creds_dict)

# 4. Połączenie z Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(credentials)

# 5. Połączenie z odpowiednim arkuszem
SHEET_ID = "1SkXqSNhEj7gm_Ts71-opjp3Gga682un-pvlP4QaJ79I"
workbook = client.open_by_key(SHEET_ID)
sheet = workbook.worksheet("RLC-stats")

# 6. Znalezienie pierwszego wolnego wiersza
column_values = sheet.col_values(1)
first_empty_row = len(column_values) + 1

# 7. Lista URL-i do sprawdzenia
urls = [
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-2006-bmw-m3-jcp11",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-71-lamborghini-hwf11",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1985-audi-sport-quattro-s1-hwf08",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1964-dodge-w200-power-wagon-hwf09"
]

# 8. Nagłówek przeglądarki do requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# 9. Przygotowanie danych - aktualna data
dataa = []
# Ustawienie strefy czasowej na "Europe/Warsaw"
warsaw_tz = pytz.timezone("Europe/Warsaw")
now = datetime.now(warsaw_tz)

# Formatowanie daty
formatted_date = now.strftime("%d-%m-%Y %H:%M")

print(f"Aktualna data i godzina: {formatted_date}")
dataa.append(formatted_date)

# 10. Funkcja do pobierania danych z pojedynczego URL-a
def fetch_product_data(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        html = response.text

        # Szukanie productVariantId
        variant_id_match = re.search(r'SDG\.Data\.productVariantId\s*=\s*(\d+)', html)

        if variant_id_match:
            variant_id = variant_id_match.group(1)

            # Szukanie inventoryQty dla tego productVariantId
            inventory_qty_match = re.search(fr'"{variant_id}":\s*(\d+)', html)
            inventory_qty = inventory_qty_match.group(1) if inventory_qty_match else "Brak danych"

            dataa.append(inventory_qty)
        else:
            print(f"❌ URL: {url} - Nie znaleziono productVariantId")
            dataa.append("Brak danych")
    except requests.exceptions.RequestException as e:
        print(f"🚨 URL: {url} - Błąd pobierania strony: {e}")
        dataa.append("Błąd")

# 11. Pobierz dane dla wszystkich URL-i
for url in urls:
    fetch_product_data(url)

# 12. Zapis danych do arkusza Google Sheets
sheet.insert_row(dataa, index=first_empty_row)
print(f"✅ Dane zapisane do Google Sheets w wierszu {first_empty_row}")
