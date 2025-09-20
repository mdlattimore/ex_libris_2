def isbn10_to_isbn13(isbn10: str):
    isbn10 = isbn10.replace('-', '').replace(' ', '')
    if len(isbn10) != 10:
        raise ValueError('Invalid ISBN10')
    strip_num = isbn10[:9]
    prepended_num = "978" + strip_num
    total = 0
    for idx, digit in enumerate(prepended_num):
        if idx % 2 == 0:
            total += int(digit)
        else:
            total += 3 * int(digit)
    check_digit = (10 - (total % 10)) % 10
    return prepended_num + str(check_digit)


def isbn13_to_isbn10(isbn13: str) -> str:
    """Convert ISBN-13 to ISBN-10 (only if prefix is 978)."""
    s = isbn13.replace("-", "").replace(" ", "")
    if len(s) != 13 or not s.isdigit():
        raise ValueError("ISBN-13 must be 13 digits")
    if not s.startswith("978"):
        raise ValueError(
            "Only ISBN-13s with prefix 978 can be converted to ISBN-10")

    core = s[3:12]

    # compute ISBN-10 check digit
    total = 0
    for i, ch in enumerate(core, 1):
        total += i * int(ch)
    remainder = total % 11
    check = "X" if remainder == 10 else str(remainder)
    return core + check


if __name__ == '__main__':
    print(isbn10_to_isbn13('0395257301')) # should be 9780395257302
    print(isbn13_to_isbn10('9780395257302')) # should be 0395257301