import requests
import time
from products.models import Book, Category


def map_category(raw):
    raw = raw.lower()

    if "self" in raw:
        return "Self Help"
    elif "business" in raw:
        return "Business"
    elif "education" in raw:
        return "Education"
    elif "technology" in raw or "programming" in raw:
        return "Technology"
    elif "religion" in raw or "islam" in raw:
        return "Religious"
    elif "fiction" in raw or "story" in raw or "novel" in raw:
        return "Story"
    else:
        return "General"



def fetch_with_retry(url, retries=3, delay=2):
    for i in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            print("Status:", response.status_code)

            if response.status_code == 200:
                return response

        except Exception as e:
            print("Error:", e)

        print(f"Retrying... ({i+1}/{retries})")
        time.sleep(delay)

    return None


def import_books(query="self help"):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"

    response = fetch_with_retry(url)

    if not response:
        print("Failed after retries")
        return

    data = response.json()
    items = data.get("items", [])
    print("Items found:", len(items))

    for item in items:
        volume = item.get("volumeInfo", {})

        title = volume.get("title", "").strip()
        authors = volume.get("authors", [])
        description = volume.get("description", "")

        categories = volume.get("categories", ["General"])
        mapped_category = map_category(categories[0])
        category, _ = Category.objects.get_or_create(name=mapped_category)

        
        image_links = volume.get("imageLinks", {})
        image_url = image_links.get("thumbnail", "")

        if image_url:
            image_url = image_url.replace("http://", "https://")
            image_url = image_url.replace("&zoom=1", "&zoom=2")

    
        sale_info = item.get("saleInfo", {})
        price_info = sale_info.get("listPrice", {})

        price = price_info.get("amount")
        price = float(price) * 280 if price else 1000

        if not title:
            continue

        if Book.objects.filter(title__iexact=title).exists():
            print("Skipping duplicate:", title)
            continue

        Book.objects.create(
            title=title,
            author=", ".join(authors) if authors else "Unknown",
            description=description,
            image_url=image_url,
            price=price,
            stock=10,
            category=category
        )

        
        time.sleep(0.2)

    print(f"Books imported successfully for query: {query}")


