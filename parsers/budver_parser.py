from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def parse_budver_kyiv_repairs(max_pages: int = 3):
    """
    Асинхронный парсер Budver (Київ + ремонт)
    Возвращает список заказов с нескольких страниц.
    """
    base_url = (
        "https://budver.com/tasks?"
        "city[]=193&title=&price_from=&price_to=&"
        "specialization[1][]=11&my_offers=&my_favorite=&"
        "not_viewed=&quickly=&less_2_offers="
    )

    results = []
    unique_urls = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="uk-UA", user_agent="Mozilla/5.0")
        page = await context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}&page={page_num}"
            print(f"🌐 Завантажую сторінку {page_num}: {url}")

            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")

                # Проверим, что Budver не перенаправил на главную
                if "tasks" not in page.url:
                    print(f"⚠️ Budver перенаправив на іншу сторінку: {page.url}")
                    break

                # Ждем появления карточек
                try:
                    await page.wait_for_selector(".task-item, .tasks__item", timeout=10000)
                except:
                    print(f"⚠️ На сторінці {page_num} не знайдено замовлень.")
                    break

                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                cards = soup.select(".task-item, .tasks__item")
                if not cards:
                    print(f"⚠️ На сторінці {page_num} немає карток.")
                    break

                print(f"✅ Знайдено {len(cards)} карток на сторінці {page_num}")

                for card in cards:
                    title_el = card.select_one("h3, h4, a")
                    desc_el = card.select_one("p")
                    city_el = card.select_one(".city, .location")
                    price_el = card.select_one(".price, .budget")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    desc = desc_el.get_text(strip=True) if desc_el else ""
                    city = city_el.get_text(strip=True) if city_el else ""
                    price = price_el.get_text(strip=True) if price_el else ""
                    href = link_el["href"] if link_el else ""

                    if href and not href.startswith("http"):
                        href = "https://budver.com" + href

                    if href in unique_urls or not title:
                        continue  # пропускаем дубликаты или пустые

                    unique_urls.add(href)
                    results.append({
                        "title": title,
                        "desc": desc,
                        "city": city,
                        "price": price,
                        "url": href
                    })

            except Exception as e:
                print(f"❌ Помилка при обробці сторінки {page_num}: {e}")
                break

        await browser.close()

    print(f"🔎 Всього знайдено {len(results)} унікальних замовлень.")
    return results
