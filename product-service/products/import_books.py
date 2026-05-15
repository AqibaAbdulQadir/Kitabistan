import requests
import time
from products.models import Book, Category

# Google Books API Key
API_KEY = "AIzaSyBms0wigV76_h5rWQqnKt9KMuozfEmjGkE"

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


def fetch_with_retry(url, retries=5, delay=3):
    for i in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )

            print("Status:", response.status_code)

            # Success
            if response.status_code == 200:
                return response

            # Rate limit handling
            elif response.status_code == 429:
                print("Rate limit hit. Waiting 15 seconds...")
                time.sleep(15)

            else:
                print("Unexpected status:", response.status_code)

        except Exception as e:
            print("Error:", e)

        print(f"Retrying... ({i + 1}/{retries})")
        time.sleep(delay)

    return None


def import_books(query="self help", max_results=20):

    
    url = (
    f"https://www.googleapis.com/books/v1/volumes"
    f"?q={query}"
    f"&maxResults={max_results}"
    f"&key={API_KEY}"
)
    

    response = fetch_with_retry(url)

    if not response:
        print("Failed after retries")
        return

    data = response.json()
    items = data.get("items", [])

    print("Items found:", len(items))

    added_count = 0
    skipped_count = 0

    for item in items:

        try:
            volume = item.get("volumeInfo", {})

            title = volume.get("title", "").strip()

            if not title:
                continue

            # Duplicate check
            if Book.objects.filter(title__iexact=title).exists():
                print("Skipping duplicate:", title)
                skipped_count += 1
                continue

            authors = volume.get("authors", [])
            description = volume.get("description", "")

            categories = volume.get("categories", ["General"])

            mapped_category = map_category(categories[0])

            category, _ = Category.objects.get_or_create(
                name=mapped_category
            )

            image_links = volume.get("imageLinks", {})
            image_url = image_links.get("thumbnail", "")

            if image_url:
                image_url = image_url.replace("http://", "https://")
                image_url = image_url.replace("&zoom=1", "&zoom=2")

            # Price handling
            sale_info = item.get("saleInfo", {})
            price_info = sale_info.get("listPrice", {})

            price = price_info.get("amount")

            if price:
                price = float(price) * 280
            else:
                price = 1000

            Book.objects.create(
                title=title,
                author=", ".join(authors) if authors else "Unknown",
                description=description,
                image_url=image_url,
                price=round(price, 2),
                stock=10,
                category=category
            )

            added_count += 1

            print(f"Added: {title}")

            # Delay to avoid rate limiting
            time.sleep(2)

        except Exception as e:
            print("Failed to import one book:", e)

    print("\nImport completed")
    print("Books added:", added_count)
    print("Duplicates skipped:", skipped_count)