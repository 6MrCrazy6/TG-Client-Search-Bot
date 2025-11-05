import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from database import Database


def parse_budver_kyiv_repairs(limit: int = 10):
    """
    Финальная версия:
    ✅ браузер открыт
    ✅ собирает ВСЕ (описание, адрес, город, цену)
    ✅ берёт текст даже из вложенных <a> (через innerText)
    ✅ ждёт появления контента
    ✅ до 10 новых заказов
    """

    base_url = (
        "https://budver.com/tasks?"
        "city[]=193&title=&price_from=&price_to=&"
        "specialization[1][]=11&my_offers=&my_favorite=&"
        "not_viewed=&quickly=&less_2_offers="
    )

    cfg = Config()
    db = Database(cfg)

    # 🟢 открытый браузер
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--lang=uk-UA")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(90)

    results = []
    seen = set()
    page = 1

    try:
        while len(results) < limit:
            if page == 1:
                list_url = f"{base_url}"
            else:
                list_url = f"https://budver.com/tasks/page-{page}?city[]=193&title=&price_from=&price_to=&" \
                           "specialization[1][]=11&my_offers=&my_favorite=&not_viewed=&quickly=&less_2_offers=&"

            print(f"🌐 Відкриваю сторінку {page}: {list_url}")
            driver.get(list_url)
            time.sleep(5)

            links = []
            for a in driver.find_elements(By.CSS_SELECTOR, "a[href^='/task/']"):
                href = a.get_attribute("href")
                if not href or "/task/add" in href:
                    continue
                m = re.search(r"/task/(\d+)$", href)
                if m:
                    full_url = f"https://budver.com/task/{m.group(1)}"
                    if full_url not in links:
                        links.append(full_url)

            if not links:
                print("⚠️ Більше немає завдань.")
                break

            print(f"✅ На сторінці {page} знайдено {len(links)} посилань.")

            for link in links:
                if len(results) >= limit:
                    break
                if link in seen or db.check_exists(link):
                    continue
                seen.add(link)

                try:
                    driver.get(link)
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    time.sleep(1.5)

                    # безопасный геттер: innerText
                    def get_inner(sel, default=""):
                        try:
                            el = driver.find_element(By.CSS_SELECTOR, sel)
                            txt = el.get_attribute("innerText").strip()
                            return re.sub(r"\s+", " ", txt)
                        except Exception:
                            return default

                    title = get_inner("h1", "Без назви")
                    if "Створити замовлення" in title:
                        continue

                    # Описание
                    desc = get_inner(".har_text", "")
                    if not desc or len(desc) < 15:
                        desc = get_inner(".task__description, .description, .task-text", "Без опису...")

                    # Город + адрес
                    loc_block = get_inner("div.one_har:nth-of-type(2) .har_text", "")
                    city = loc_block if loc_block else "Невідоме місто"

                    # Цена
                    price = get_inner(".task_offer strong", "")
                    if not price:
                        price = get_inner(".task__price, .price, .budget", "Договірна")
                    if not re.search(r"\d", price):
                        price = "Договірна"

                    task = {
                        "title": title,
                        "city": city,
                        "price": price,
                        "desc": desc,
                        "url": link
                    }

                    results.append(task)
                    db.save_order(title, desc, city, price, link)
                    print(f"📦 Нове завдання: {title}")

                except Exception as e:
                    print(f"⚠️ Помилка при обробці {link}: {e}")
                    continue

                time.sleep(3)

            page += 1
            time.sleep(3)

    except Exception as e:
        print(f"❌ Помилка при парсингу: {e}")
    finally:
        driver.quit()

    print(f"🔎 Всього знайдено {len(results)} нових замовлень.")
    return results
