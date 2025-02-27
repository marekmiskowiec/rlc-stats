import re
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


# SHEET
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(credentials)

sheet_id = "1SkXqSNhEj7gm_Ts71-opjp3Gga682un-pvlP4QaJ79I"

workbook = client.open_by_key(sheet_id)

sheet = workbook.worksheet("RLC-stats")

# Pobierz całą kolumnę A (możesz zmienić na inną kolumnę)
column_values = sheet.col_values(1)

# Znajdź pierwszy pusty wiersz (indeks + 1, bo indeksy są od 0)
first_empty_row = len(column_values) + 1

# print(f"Pierwszy pusty wiersz: {first_empty_row}")

# List of URLs to process
urls = [
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-2006-bmw-m3-jcp11",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-71-lamborghini-hwf11",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1985-audi-sport-quattro-s1-hwf08",
    "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1964-dodge-w200-power-wagon-hwf09"
]

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

dataa = []
now = datetime.now()  # Pobranie aktualnej daty i godziny
formatted_date = now.strftime("%d-%m-%Y %H:%M")  # Formatowanie
# print(f"Aktualna data i godzina: {formatted_date}")
dataa.append(formatted_date)

def fetch_product_data(url):
    try:
        # Fetch the page content
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        html = response.text

        # Extract the product title (fallback to regex if needed)
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Brak tytułu"

        # Find the productVariantId
        variant_id_match = re.search(r'SDG\.Data\.productVariantId\s*=\s*(\d+)', html)

        if variant_id_match:
            variant_id = variant_id_match.group(1)

            # Find inventory quantity for the identified productVariantId
            inventory_qty_match = re.search(fr'"{variant_id}":\s*(\d+)', html)
            inventory_qty = inventory_qty_match.group(1) if inventory_qty_match else "Brak danych"

            # print(f"✅ URL: {url}")
            # print(f"📌 Title: {title}")
            # print(f"🆔 Product Variant ID: {variant_id}")
            # print(f"📦 Inventory Quantity: {inventory_qty}")
            # print("-" * 60)
            dataa.append(inventory_qty)
        else:
            print(f"❌ URL: {url} - Nie znaleziono productVariantId")
    except requests.exceptions.RequestException as e:
        print(f"🚨 URL: {url} - Błąd pobierania strony: {e}")

# Process each URL
for url in urls:
    fetch_product_data(url)

# print(dataa)
sheet.insert_row(dataa, index=first_empty_row)  # Wstawia wiersz na 3. miejscu








