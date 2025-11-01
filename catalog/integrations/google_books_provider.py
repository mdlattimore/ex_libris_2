import requests
import os

class GoogleBooksProvider:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    @classmethod
    def lookup(cls, isbn: str) -> dict:
        url = f"{cls.BASE_URL}?q=isbn:{isbn}&key={cls.key}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data["totalItems"] == 0:
            raise LookupError("No results found")

        item = data["items"][0]["volumeInfo"]

        return {
            "title": item.get("title"),
            "subtitle": item.get("subtitle"),
            "author": ", ".join(item.get("authors", [])),
            "publisher": item.get("publisher"),
            "published_date": item.get("publishedDate"),
            "page_count": item.get("pageCount"),
            "cover_url": item.get("imageLinks", {}).get("thumbnail"),
            "isbn_10": cls._get_isbn(item, "ISBN_10"),
            "isbn_13": cls._get_isbn(item, "ISBN_13"),
            "description": item.get("description"),
        }

    @staticmethod
    def _get_isbn(item, kind):
        for identifier in item.get("industryIdentifiers", []):
            if identifier["type"] == kind:
                return identifier["identifier"]
