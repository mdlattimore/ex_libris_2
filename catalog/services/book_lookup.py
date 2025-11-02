from catalog.utils.fuzzy_matching import (name_match, normalize_name,
                                          normalize_title, title_match)

from catalog.integrations.google_books_provider import GoogleBooksProvider
from catalog.models import Author, AuthorAlias, Work

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



def resolve_work(title: str):
    """Return best-matching Work instance (or Unknown Work), using fuzzy title matching."""
    if not title:
        return Work.objects.filter(title="Unknown Work").first()

    normalized_title = normalize_title(title)
    best_match = None
    best_score = 0

    for work_instance in Work.objects.all():
        score = title_match(work_instance.title, normalized_title)
        if score > best_score:
            best_score = score
            best_match = work_instance

    if best_match and best_score >= 80:
        return best_match

    # No sufficiently close match found — create or fallback
    return Work.objects.filter(title="Unknown Work").first()

def perform_isbn_lookup(isbn):
    result = GoogleBooksProvider.lookup(isbn)

    author_name = result.get("author")
    title = result.get("title")

    if not (author_name and title):
        raise ValueError(f"Incomplete data returned for ISBN {isbn}: {result}")

    author = resolve_author(author_name)
    work = resolve_work(title)

    return {"result": result, "author": author, "work": work}



