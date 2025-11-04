import requests
from bs4 import BeautifulSoup

class BudverParser:
    """Парсер Budver: отвечает только за извлечение данных"""

    BASE_URL = "https://budver.com"

    def fetch_orders(self):
        url = f"{self.BASE_URL}/orders"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"⚠️ Помилка завантаження Budver: {e}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".order-item, .project-item, .orders-list .order")

        results = []
        for c in cards:
            title = c.select_one(".title, .order-title, h3, h4")
            desc = c.select_one(".description, .order-desc, p")
            city = c.select_one(".city, .location")
            price = c.select_one(".price, .budget")
            link = c.select_one("a[href]")

            title = title.get_text(strip=True) if title else "Без назви"
            desc = desc.get_text(strip=True) if desc else ""
            city = city.get_text(strip=True) if city else ""
            price = price.get_text(strip=True) if price else ""
            href = link["href"] if link else ""
            if href and not href.startswith("http"):
                href = self.BASE_URL + href

            # фильтр по Киеву и ремонту
            text_all = f"{title} {desc}".lower()
            if "ремонт" in text_all and ("київ" in city.lower() or "киев" in city.lower()):
                results.append({
                    "title": title,
                    "desc": desc,
                    "city": city,
                    "price": price,
                    "url": href
                })
        return results
