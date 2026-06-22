"""Reference data for North Dakota Supreme Court justices.

Derived from https://www.ndcourts.gov/about-us/history/north-dakota-supreme-court-since-statehood
Each entry: canonical last name, full name, start year, end year (None = present).
"""

# Elected justices in order of first service
JUSTICES = [
    # Court 1–3 (1889–1902)
    ("Corliss", "Guy C. H. Corliss", 1889, 1898),
    ("Bartholomew", "Joseph Bartholomew", 1889, 1900),
    ("Wallin", "Alfred Wallin", 1889, 1902),
    # Court 2–5
    ("Young", "Newton C. Young", 1898, 1904),
    ("Morgan", "David Morgan", 1901, 1911),
    ("Cochrane", "John M. Cochrane", 1903, 1904),
    ("Engerud", "Edward Engerud", 1904, 1907),
    ("Knauf", "John Knauf", 1906, 1906),
    ("Spalding", "Burleigh F. Spalding", 1907, 1914),
    # Court 8–9
    ("Fisk", "Charles Fisk", 1907, 1916),
    ("Ellsworth", "Sidney E. Ellsworth", 1909, 1910),
    ("Carmody", "John Carmody", 1909, 1910),
    # Court 10–12
    ("Goss", "Evan B. Goss", 1911, 1916),
    ("Burke_ET", "Edward T. Burke", 1911, 1916),
    ("Bruce", "Andrew A. Bruce", 1912, 1918),
    ("Christianson", "Adolph M. Christianson", 1912, 1934),
    # Court 13–14
    ("Grace", "Richard Grace", 1917, 1922),
    ("Robinson", "James Robinson", 1918, 1922),
    ("Bronson", "Harrison A. Bronson", 1918, 1924),
    ("Birdzell", "Luther E. Birdzell", 1918, 1933),
    # Court 15–16
    ("Johnson_S", "Sveinbjorn Johnson", 1923, 1926),
    # Court 17–21
    ("Burke_J", "John Burke", 1919, 1937),
    ("Nuessle", "William Nuessle", 1920, 1950),
    ("Burr", "Alexander Burr", 1933, 1949),
    ("Morris", "James Morris", 1933, 1962),
    ("Moellring", "George Moellring", 1933, 1934),
    # Court 20–22
    ("Sathre", "Peter O. Sathre", 1937, 1938),
    ("Sathre", "Peter O. Sathre", 1951, 1962),
    ("Grimson", "Gudmunder Grimson", 1949, 1958),
    # Court 23–24
    ("Burke_T", "Thomas J. Burke", 1951, 1966),
    ("Johnson_N", "Nels Johnson", 1954, 1958),
    # Court 25–29
    ("Strutz", "Alvin C. Strutz", 1951, 1973),
    ("Teigen", "Obert C. Teigen", 1951, 1973),
    ("Erickstad", "Ralph J. Erickstad", 1966, 1992),
    ("Murray", "William S. Murray", 1966, 1966),
    ("Knudson", "Harvey B. Knudson", 1967, 1978),
    ("Paulson", "William L. Paulson", 1967, 1978),
    # Court 30–32
    ("Vogel", "Robert Vogel", 1974, 1978),
    ("Sand", "Paul M. Sand", 1978, 1984),
    ("Pederson", "Vernon R. Pederson", 1978, 1984),
    ("VandeWalle", "Gerald W. VandeWalle", 1978, 2023),
    # Court 34–35
    ("Gierke", "H. F. Gierke III", 1978, 1991),
    ("Meschke", "Herbert L. Meschke", 1985, 1998),
    ("Levine", "Beryl J. Levine", 1992, 2005),
    # Court 36
    ("Johnson_JP", "J. Philip Johnson", 1974, 1975),
    ("Johnson_JP", "J. Philip Johnson", 1992, 1992),
    # Court 37–39
    ("Neumann", "William A. Neumann", 1993, 2005),
    ("Sandstrom", "Dale V. Sandstrom", 1996, 2016),
    ("Maring", "Mary Muehlen Maring", 1996, 2013),
    ("Kapsner", "Carol Ronning Kapsner", 1998, 2017),
    # Court 40–47
    ("Crothers", "Daniel J. Crothers", 2005, 2026),
    ("McEvers", "Lisa K. Fair McEvers", 2014, None),
    ("Tufte", "Jerod E. Tufte", 2017, None),
    ("Jensen", "Jon J. Jensen", 2017, None),
    ("Bahr", "Douglas A. Bahr", 2023, None),
    ("Friese", "Mark A. Friese", 2026, None),
]

# Build lookup structures

# Canonical name by last name (for simple cases)
# Note: multiple Burkes and Johnsons exist — these need date-based disambiguation
JUSTICE_BY_LAST_NAME: dict[str, list[tuple[str, int, int | None]]] = {}
for key, full_name, start, end in JUSTICES:
    # Use the last name from the full name (last token, or special cases)
    last = full_name.split()[-1]
    if last == "III":
        last = full_name.split()[-2]
    if last not in JUSTICE_BY_LAST_NAME:
        JUSTICE_BY_LAST_NAME[last] = []
    JUSTICE_BY_LAST_NAME[last].append((full_name, start, end))

# All known last names (lowercase) for fuzzy matching
KNOWN_LAST_NAMES = {name.split()[-1].lower() for _, name, _, _ in JUSTICES}
# Fix Gierke
KNOWN_LAST_NAMES.discard("iii")
KNOWN_LAST_NAMES.add("gierke")


def resolve_justice(name: str, year: int | None = None) -> str | None:
    """Try to resolve an author name to a canonical justice last name.

    Returns the canonical last name or None if not recognized.
    """
    if not name:
        return None

    clean = name.strip()

    # Direct match
    for key, full_name, start, end in JUSTICES:
        last = key.split("_")[0]  # Strip disambiguation suffix
        if clean.lower() == last.lower():
            if year is None:
                return last
            end_y = end or 2100
            if start - 1 <= year <= end_y + 1:
                return last
    return None


def is_known_justice(name: str) -> bool:
    """Check if a name matches any known justice last name."""
    return name.strip().lower() in KNOWN_LAST_NAMES
