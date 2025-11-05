import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def parse_rabotniki_search(limit: int = 10):
    """
    💪 Стабільний парсер rabotniki.ua без webdriver.common.exceptions.
    Перевіряє всі замовлення на сторінці.
    """

    base_url = "https://www.rabotniki.ua/uk/tenders?search=Ремонт&page="

    # 🔧 Налаштування браузера
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--lang=uk-UA")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(60)

    results = []
    seen = set()
    page = 1

    try:
        while len(results) < limit:
            list_url = f"{base_url}{page}"
            print(f"🌐 Відкриваю сторінку {page}: {list_url}")

            # Спроба відкрити сторінку
            for _ in range(3):
                try:
                    driver.get(list_url)
                    break
                except Exception:
                    print("⚠️ Не вдалося відкрити сторінку, повтор через 3 секунди...")
                    time.sleep(3)

            time.sleep(2)

            # Знаходимо всі картки
            cards = driver.find_elements(By.CSS_SELECTOR, "div.list-view div[data-key]")
            if not cards:
                print("⚠️ Замовлень не знайдено.")
                break

            print(f"✅ На сторінці {page} знайдено {len(cards)} посилань.")

            # ⚙️ Спочатку зберігаємо всі посилання
            links = []
            for card in cards:
                try:
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    if link and link not in seen:
                        seen.add(link)
                        links.append(link)
                except Exception:
                    continue

            # 🔁 Тепер проходимось по кожній силці
            for idx, link in enumerate(links):
                if len(results) >= limit:
                    break

                try:
                    driver.get(link)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    time.sleep(1)

                    # Перевіряємо, чи не закритий тендер
                    if "Тендер закритий" in driver.page_source:
                        print(f"❌ Тендер {link} закритий, пропускаємо.")
                        continue

                    # Назва
                    try:
                        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
                    except Exception:
                        title = "Без назви"

                    # Опис
                    try:
                        desc = driver.find_element(By.CSS_SELECTOR, "div.mt-3").text.strip()
                    except Exception:
                        desc = "Без опису..."

                    # Ціна
                    try:
                        # шукаємо блок, у якому згадується слово "Бюджет"
                        price_blocks = driver.find_elements(By.CSS_SELECTOR, "div.mt-3")
                        price = "Договірна"
                        for block in price_blocks:
                            txt = block.text.strip()
                            if "Бюджет" in txt and "грн" in txt:
                                price = txt
                                break
                    except Exception:
                        price = "Договірна"

                    city = "Київ"

                    results.append({
                        "title": title,
                        "desc": desc,
                        "city": city,
                        "price": price,
                        "url": link
                    })

                    print(f"📦 {idx + 1}. {title}")

                except Exception as e:
                    print(f"⚠️ Помилка при обробці {link}: {e}")
                    continue

            page += 1
            time.sleep(1)

    except Exception as e:
        print(f"❌ Критична помилка: {e}")
    finally:
        driver.quit()

    print(f"🔎 Всього знайдено {len(results)} нових замовлень.")
    return results


