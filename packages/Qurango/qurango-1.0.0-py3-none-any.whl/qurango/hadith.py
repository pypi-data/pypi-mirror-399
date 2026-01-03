import json
import pandas as pd
from importlib import resources
from .utils import BOOK_TITLE_MAP, normalize_text


class HadithLoader:
    """
    Loads Hadith data from JSON files inside the package,
    preprocesses it, and stores it in a Pandas DataFrame.
    """

    def __init__(self):
        # Auto-load all JSON files from package data
        self.df = self._load_and_preprocess()

    def _load_and_preprocess(self) -> pd.DataFrame:
        records = []

        # Use importlib.resources to access package data
        hadith_dir = resources.files("qurango.data")

        for file in hadith_dir.iterdir():
            if file.name.endswith(".json"):
                with file.open(encoding="utf-8") as f:
                    records.extend(json.load(f))

        df = pd.DataFrame(records)

        # Remove unwanted column if present
        df = df.drop(columns=["english_hadith_title"], errors="ignore")

        # Map English book titles
        df["book_title_english"] = df["book_title"].map(BOOK_TITLE_MAP)

        # Normalize text once for fast searching
        df["norm_title"] = df["hadith_title"].apply(normalize_text)
        df["norm_urdu"] = df["urdu_translation"].apply(normalize_text)
        df["norm_english"] = df["english_translation"].apply(normalize_text)

        return df

    def total_hadiths(self):
        return len(self.df)

    def total_books(self):
        return self.df["book_title"].nunique()

    def get_available_books(self, as_dataframe=False):
        books = (
            self.df[["book_title", "book_title_english"]]
            .drop_duplicates()
            .sort_values("book_title_english", na_position="last")
            .reset_index(drop=True)
        )
        return books if as_dataframe else books.to_dict(orient="records")

    def show_available_books(self):
        books = self.get_available_books()
        print(f"\n📚 Total Available Books: {len(books)}\n")
        for i, book in enumerate(books, start=1):
            print(f"{i}. {book['book_title_english']} ({book['book_title']})")

    def get_dataframe(self):
        return self.df.copy()


# ----------------------------------------
# Hadith Search Engine (FAST)
# ----------------------------------------
class HadithSearch:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def search_by_keyword(self, keyword: str) -> pd.DataFrame:
        key = normalize_text(keyword)
        mask = (
            self.df["norm_title"].str.contains(key, na=False)
            | self.df["norm_urdu"].str.contains(key, na=False)
            | self.df["norm_english"].str.contains(key, na=False)
        )
        return self.df[mask]

    def search_by_narrator(self, narrator: str, language="auto") -> pd.DataFrame:
        name = normalize_text(narrator)
        if language == "urdu":
            mask = (
                self.df["norm_title"].str.contains(name, na=False)
                | self.df["norm_urdu"].str.contains(name, na=False)
            )
        elif language == "english":
            mask = self.df["norm_english"].str.contains(name, na=False)
        else:
            mask = (
                self.df["norm_title"].str.contains(name, na=False)
                | self.df["norm_urdu"].str.contains(name, na=False)
                | self.df["norm_english"].str.contains(name, na=False)
            )
        return self.df[mask]

    def search_by_book(self, book_name: str, hadith_number=None) -> pd.DataFrame:
        book = book_name.lower()
        mask = (
            self.df["book_title"].str.lower().str.contains(book, na=False)
            | (self.df["book_title_english"].str.lower() == book)
        )
        if hadith_number is not None:
            mask &= self.df["hadith_number"] == hadith_number
        return self.df[mask]

    def search_by_hadith_number(self, number: int) -> pd.DataFrame:
        return self.df[self.df["hadith_number"] == number]
