from datetime import datetime, date

def parse_published_date(raw_date: str) -> date | None:
    """Safely parse Google Books' inconsistent publishedDate values into a Python date."""
    if not raw_date:
        return None

    raw_date = raw_date.strip()

    # Try common formats
    formats = [
        "%Y-%m-%d",  # 2003-07-14
        "%Y-%m",     # 2003-07
        "%Y",        # 2003
        "%d/%m/%Y",  # 14/07/2003
        "%m/%Y",     # 07/2003
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(raw_date, fmt)
            # For partial dates (year-only, year-month), pad missing components
            if fmt == "%Y":
                return date(dt.year, 1, 1)
            if fmt == "%Y-%m" or fmt == "%m/%Y":
                return date(dt.year, dt.month, 1)
            return dt.date()
        except ValueError:
            continue

    # Couldn’t parse — just return None (or log)
    return None
