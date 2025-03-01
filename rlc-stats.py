import re
import requests
import gspread
import json
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import pytz


class RLCScraper:
    def __init__(self):
        load_dotenv()
        self.google_credentials = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not self.google_credentials:
            raise ValueError("❌ Nie znaleziono zmiennej GOOGLE_SHEETS_CREDENTIALS!")

        # Parsowanie credentials
        self.creds_dict = json.loads(self.google_credentials)
        self.creds_dict["private_key"] = self.creds_dict["private_key"].replace("\\n", "\n")

        # Połączenie z Google Sheets
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(self.creds_dict, scopes=scopes)
        self.client = gspread.authorize(credentials)

        # Połączenie z odpowiednim arkuszem
        self.SHEET_ID = "1SkXqSNhEj7gm_Ts71-opjp3Gga682un-pvlP4QaJ79I"
        self.workbook = self.client.open_by_key(self.SHEET_ID)
        self.sheet = self.workbook.worksheet("RLC-stats")

        # Lista URL-i
        self.urls = [
            "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-2006-bmw-m3-jcp11",
            "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-71-lamborghini-hwf11",
            "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1985-audi-sport-quattro-s1-hwf08",
            "https://creations.mattel.com/en-pl/products/hot-wheels-rlc-1964-dodge-w200-power-wagon-hwf09"
        ]

        # User-Agent
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }

        # Inicjalizacja danych
        self.data_row = []

    def get_current_date(self):
        warsaw_tz = pytz.timezone("Europe/Warsaw")
        now = datetime.now(warsaw_tz)
        return now.strftime("%d-%m-%Y %H:%M")

    def find_first_empty_row(self):
        column_values = self.sheet.col_values(1)
        return len(column_values) + 1

    def fetch_inventory_qty(self, url):
        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            html = response.text

            variant_id_match = re.search(r'SDG\.Data\.productVariantId\s*=\s*(\d+)', html)

            if variant_id_match:
                variant_id = variant_id_match.group(1)

                inventory_qty_match = re.search(fr'"{variant_id}":\s*(\d+)', html)
                inventory_qty = inventory_qty_match.group(1) if inventory_qty_match else "Brak danych"

                return inventory_qty
            else:
                print(f"❌ URL: {url} - Nie znaleziono productVariantId")
                return "Sold Out"
        except requests.exceptions.RequestException as e:
            print(f"🚨 URL: {url} - Błąd pobierania strony: {e}")
            return "Błąd"

    def run(self):
        # Data na początek wiersza
        self.data_row.append(self.get_current_date())

        # Pobranie danych z wszystkich URL-i
        for url in self.urls:
            qty = self.fetch_inventory_qty(url)
            self.data_row.append(qty)

        # Zapis do Google Sheets
        first_empty_row = self.find_first_empty_row()
        self.sheet.insert_row(self.data_row, index=first_empty_row)
        print(f"✅ Dane zapisane do Google Sheets w wierszu {first_empty_row}")


# Uruchomienie scrappera
if __name__ == "__main__":
    scraper = RLCScraper()
    scraper.run()