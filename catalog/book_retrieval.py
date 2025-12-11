# using google books api

import os
import time
from pprint import pprint

import requests


def lookup_book(isbn: str) -> dict:
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    print("LUB", repr(isbn))
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"
    response = requests.get(url)
    print(response.status_code)
    print(f"API KEY = {api_key}")
    data = response.json()
    # pprint(data)
    if data['totalItems'] > 0:
        for book in data['items']:
            # try/except block necessary because, for reasons passing understanding
            # the api can search and retrieve books by isbn but will sometimes not
            # include the isbn number(s) in the response or have a 
            # len('industryIdentifiers')--a list of dictionaries with identifier/value
            # key/value pairs--less than 2, raising an IndexError when attempting to 
            # access index position 1
            try:
                if book['volumeInfo']['industryIdentifiers'][0][
                    'identifier'] == isbn or \
                        book['volumeInfo']['industryIdentifiers'][1][
                            'identifier'] == isbn:
                    return book['volumeInfo']
            except IndexError:
                return book['volumeInfo']
    else:
        return "Book not found"


def get_book(isbn: str) -> dict:
    isbn = isbn.replace("-", "").replace(" ", "")
    print("GB", repr(isbn))
    # print("GB", type(isbn))
    book = lookup_book(isbn)
    pprint(book)
    return book


if "__main__" == __name__:
    def display_book(book: dict) -> None:
        if type(book) == str:
            print(book)
            return
        title = book.get('title', "...")
        author_list = book.get('authors')
        if author_list:
            author_display = ", ".join(author_list)
        else:
            author_display = "..."
        publisher = book.get('publisher', "...")
        pub_date = book.get('publishedDate', "...")
        description = book.get('description', "...")
        page_count = book.get('pageCount', "...")
        categories_list = book.get('categories')
        if categories_list:
            categories_display = ", ".join(categories_list)
        else:
            categories_display = "..."
        image = book.get('imageLinks', "...")

        print(f"""
        Title: {title}
        Author: {author_display}
        Publisher: {publisher}
        Published {pub_date}
        Description: {description}
        Categories: {categories_display}
        Page Count: {page_count}
        Images: {image}""")


    isbn = input("Enter ISBN: ")
    start = time.perf_counter()
    book = get_book(isbn)
    stop = time.perf_counter()
    # print(type(book))
    print(f"{stop - start} seconds")
    display_book(book)
