# 📖 Qurango -- Hadith Module

Qurango is a Python library that provides **fast, structured, and
searchable access to authentic Hadith collections** using JSON data
bundled directly inside the package.\
It is optimized for **research, data analysis, NLP, and educational
use**.

This README explains **how the Hadith system works internally** and
**how to use it step by step**.

------------------------------------------------------------------------

## ✨ Key Highlights

-   📚 Loads Hadith data directly from packaged JSON files
-   ⚡ Preprocessed and optimized for **fast searching**
-   🔍 Search Hadith by:
    -   Keyword
    -   Narrator
    -   Book name
    -   Hadith number
-   📊 Outputs results as **Pandas DataFrames**
-   🌐 Supports Urdu & English text normalization
-   🧠 Ideal for NLP, ML, and text analytics

------------------------------------------------------------------------

## 📦 Installation

``` bash
pip install Qurango
```

------------------------------------------------------------------------

## 🚀 Quick Start

``` python
from Qurango.hadith import HadithLoader, HadithSearch
```

------------------------------------------------------------------------

## 📘 Loading Hadith Data

The `HadithLoader` class automatically loads **all Hadith JSON files**
from the package data directory and preprocesses them.

``` python
loader = HadithLoader()
``>

### ✔ What happens internally?

- Loads JSON files from `qurango.data`
- Converts data to a Pandas DataFrame
- Normalizes Urdu & English text
- Maps Arabic book titles to English names
- Prepares searchable columns for fast queries

---

## 📊 Accessing the DataFrame

```python
df = loader.get_dataframe()
print(df.head())
```

### Total Hadith & Books

``` python
loader.total_hadiths()
loader.total_books()
```

------------------------------------------------------------------------

## 📚 Available Hadith Books

### Get as List

``` python
books = loader.get_available_books()
print(books)
```

### Get as DataFrame

``` python
books_df = loader.get_available_books(as_dataframe=True)
print(books_df)
```

### Print Books Nicely

``` python
loader.show_available_books()
```

------------------------------------------------------------------------

## 🔍 Searching Hadith

Create the search engine:

``` python
search = HadithSearch(df)
```

------------------------------------------------------------------------

### 🔎 Search by Keyword

``` python
results = search.search_by_keyword("iman")
print(results)
```

Search works across: - Hadith title - Urdu translation - English
translation

------------------------------------------------------------------------

### 🧑 Search by Narrator

``` python
results = search.search_by_narrator("Abu Huraira")
print(results)
```

Language options: - `"urdu"` - `"english"` - `"auto"` (default)

------------------------------------------------------------------------

### 📖 Search by Book

``` python
results = search.search_by_book("Sahih Bukhari")
print(results)
```

Search by book + hadith number:

``` python
results = search.search_by_book("Sahih Bukhari", hadith_number=1)
print(results)
```

------------------------------------------------------------------------

### 🔢 Search by Hadith Number

``` python
results = search.search_by_hadith_number(5)
print(results)
```

------------------------------------------------------------------------

## 📊 Output Format

All search methods return:

-   ✅ Pandas DataFrame
-   ✅ Easy export to CSV / JSON
-   ✅ Ready for NLP pipelines

Example:

``` python
results.to_csv("hadith_results.csv", index=False)
```

------------------------------------------------------------------------

## 🧠 Use Cases

-   Islamic research & academia
-   NLP on religious texts
-   Machine learning datasets
-   Search engines & chatbots
-   Educational software

------------------------------------------------------------------------

## 🛠 Requirements

-   Python 3.8+
-   pandas

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

## 🙏 Acknowledgment

This Hadith module is built to make **authentic Islamic knowledge
accessible** for developers, researchers, and the global community using
modern data tools.
