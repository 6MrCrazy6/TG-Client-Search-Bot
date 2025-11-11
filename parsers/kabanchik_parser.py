import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COOKIES_FILE = str(BASE_DIR / "kabanchik_cookies.json")
print(f"📂 Cookies path: {COOKIES_FILE}")

def login_kabanchik(email: str, password: str):
    """Авторизация на kabanchik.ua с автоподгрузкой cookies.
    Если cookies есть — использует их.
    Если нет — делает ручной логин и сохраняет."""
    opts = Options()
    opts.add_argument("--headless=new")  # 🧠 полностью скрывает окно браузера
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # 👉 Если хочешь использовать свой профиль Chrome (ускоряет вход):
    # opts.add_argument(r'--user-data-dir=C:\Users\38095\AppData\Local\Google\Chrome\User Data')
    # opts.add_argument(r'--profile-directory=Default')

    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 30)

    def save_cookies():
        """Сохраняет cookies после авторизации"""
        try:
            cookies = driver.get_cookies()
            with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("💾 Cookies сохранены.")
        except Exception as e:
            print(f"⚠️ Не удалось сохранить cookies: {e}")

    def load_cookies():
        """Подгружает cookies, если они есть"""
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            driver.get("https://kabanchik.ua/")
            time.sleep(2)  # дождаться загрузки
            for cookie in cookies:
                cookie.pop("sameSite", None)
                cookie.pop("expiry", None)
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    pass
            print("🍪 Cookies подгружены.")
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке cookies: {e}")

    try:
        # ============================
        # 1️⃣ Пытаемся войти через cookies
        # ============================
        if os.path.exists(COOKIES_FILE):
            driver.get("https://kabanchik.ua/")
            load_cookies()
            driver.get("https://kabanchik.ua/ua/cabinet/kyiv/category/remont-kvartyr")
            time.sleep(3)
            if "cabinet" in driver.current_url or "remont-kvartyr" in driver.current_url:
                print("✅ Успешный вход по cookies.")
                return driver
            else:
                print("⚠️ Cookies не активны, выполняем ручной вход...")

        # ============================
        # 2️⃣ Ручной логин
        # ============================
        print("🔐 Выполняем ручной вход...")
        driver.get("https://kabanchik.ua/ua/auth/login")

        email_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder,'Email') or contains(@placeholder,'телефон')]"))
        )
        email_field.clear()
        email_field.send_keys(email)

        pwd_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        pwd_field.clear()
        pwd_field.send_keys(password)

        # стабильный клик по кнопке "Увійти"
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Увійти')]]"))
        )
        time.sleep(0.8)
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
            driver.execute_script("arguments[0].click();", login_btn)
        except Exception as e:
            print("⚠️ JS-click fallback:", e)
            login_btn.click()

        print("📱 Якщо просить код — введи його вручну у браузері...")
        input("⏳ Після входу у кабінет натисни Enter, щоб зберегти cookies...")

        # Проверка успешного входа
        current_url = driver.current_url
        if "cabinet" not in current_url:
            print("⚠️ Вхід не підтверджено. Можливо, не ввів код?")
        else:
            save_cookies()
            print("✅ Логін успішний, cookies збережені.")

        driver.get("https://kabanchik.ua/ua/cabinet/kyiv/category/remont-pid-kliuch")
        return driver

    except Exception as e:
        print(f"❌ Помилка входу: {e}")
        driver.save_screenshot("kabanchik_login_error.png")
        driver.quit()
        return None

def parse_kabanchik_orders(driver, max_orders: int = 10):
    """
    Парсит заказы Kabanchik: 'Очікує фахівця'.
    Скроллит страницу, убирает дубли, и прекращает при 'Закрито...' или 'В роботі'.
    """
    wait = WebDriverWait(driver, 40)

    try:
        print("⏳ Завантаження сторінки з замовленнями...")
        driver.get("https://kabanchik.ua/ua/cabinet/kyiv/category/remont-kvartyr")
        time.sleep(10)

        # Динамический скролл вниз для подгрузки всех заказов
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(6):  # ~6 прокруток (можно увеличить)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Ждём появления карточек
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'kb-dashboard-performer')]")))

        cards = driver.find_elements(By.XPATH, "//div[contains(@class,'kb-dashboard-performer')]")
        print(f"🔍 Завантажено {len(cards)} елементів DOM (можуть бути дублікати)...")

        orders = []
        seen_urls = set()

        for card in cards:
            try:
                # Пропускаем скрытые или пустые карточки
                if not card.is_displayed():
                    continue

                title_el = card.find_element(By.XPATH, ".//a[contains(@class,'kb-dashboard-performer__title')]")
                title = title_el.text.strip()
                link = title_el.get_attribute("href")

                price = card.find_element(By.XPATH, ".//div[contains(@class,'kb-dashboard-performer__cost')]").text.strip()
                city = card.find_element(By.XPATH, ".//div[contains(@class,'kb-dashboard-performer__line') and not(contains(text(),'Виконати'))]").text.strip()
                status = card.find_element(By.XPATH, ".//div[contains(@class,'kb-dashboard-performer__status')]").text.strip()

                # пропускаем дубли
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                print(f"🔎 {title} | {price} | {city} | [{status}]")

                if any(stop in status for stop in ["В роботі", "Закрито автоматично", "Закрито замовником"]):
                    print("⛔ Зустрів завершене замовлення — парсинг зупинено.")
                    break

                if "Очікує фахівця" in status:
                    orders.append({
                        "title": title,
                        "price": price,
                        "city": city,
                        "status": status,
                        "url": link
                    })

                if len(orders) >= max_orders:
                    print("📦 Досягнуто ліміт по кількості замовлень.")
                    break

                time.sleep(2.5)

            except Exception:
                continue

        print(f"\n✅ Знайдено {len(orders)} унікальних актуальних 'Очікує фахівця'.")
        return orders

    except Exception as e:
        print(f"❌ Помилка під час парсингу: {e}")
        driver.save_screenshot("kabanchik_parse_error.png")
        return []