from catalog.utils.fuzzy_matching import name_match, normalize_name

from catalog.integrations.google_books_provider import GoogleBooksProvider
from catalog.models import Author, AuthorAlias


def perform_isbn_lookup(isbn):
    result = GoogleBooksProvider.lookup(isbn)

    author_name = result.get("author")
    title = result.get("title")

    if not (author_name and title):
        raise ValueError(f"Incomplete data returned for ISBN {isbn}: {result}")

    author = resolve_author(author_name)
    # work = resolve_work(title, author)

    return {"result": result, "author": author} #, "work": work}


def resolve_author(name: str):
    """Return best-matching Author instance, accounting for aliases and fuzzy similarity."""
    if not name:
        return Author.objects.filter(full_name="Unknown Author").first()

    normalized_target = normalize_name(name)

    # Step 1: Check aliases first (direct or fuzzy)
    for alias in AuthorAlias.objects.select_related("author"):
        if name_match(alias.alias, normalized_target) >= 90:
            return alias.author

    # Step 2: Check direct author names
    for author_instance in Author.objects.all():
        if name_match(author_instance.match_name, normalized_target) >= 90:
            return author_instance

    # Step 3: Fallback
    return Author.objects.filter(full_name="Unknown Author").first()


# all_aliases = AuthorAlias.objects.all()
    #         for alias in all_aliases:
    #             # if authors == alias.alias:
    #             if name_match(authors, alias.alias) >= 90:
    #                 authors = alias.author.full_name
    #                 print(f"{alias} for {alias.author}")
    #                 break


def resolve_work(title: str, author: Author):
    # Fuzzy match or create Work
    ...
