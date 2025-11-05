from parsers.rabotniki_parser import parse_rabotniki_search

if __name__ == "__main__":
    orders = parse_rabotniki_search(limit=5)
    for o in orders:
        print("\n─────────────────────────────")
        print(f"🏷 {o['title']}")
        print(f"📍 {o['city']}")
        print(f"💰 {o['price']}")
        print(f"🔗 {o['url']}")
        print(f"📄 {o['desc'][:120]}...")
