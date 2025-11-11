from parsers.kabanchik_parser import login_kabanchik, parse_kabanchik_orders
from config import Config

cfg = Config()
driver = login_kabanchik(cfg.KABANCHIK_LOGIN, cfg.KABANCHIK_PASSWORD)

if driver:
    orders = parse_kabanchik_orders(driver, max_orders=3)

    print("\n📋 Знайдені замовлення:")
    for o in orders:
        print(f"- {o['title']} → {o['url']}")

    input("\nНатисни Enter, щоб закрити браузер...")
    driver.quit()
