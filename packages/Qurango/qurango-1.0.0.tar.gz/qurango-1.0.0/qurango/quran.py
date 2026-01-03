import json
import pandas as pd
from importlib import resources


class Quran:
    def __init__(self):
        # AUTO LOAD DATA FROM PACKAGE
        with resources.open_text(
            "qurango.data.quran", "Quran.json", encoding="utf-8"
        ) as f:
            self.data = json.load(f)

        if not isinstance(self.data, list):
            raise ValueError("Quran JSON must be a list of ayahs")

        self.languages = self._extract_languages()

    # ----------------------------
    # Utility
    # ----------------------------
    def _extract_languages(self):
        if len(self.data) == 0:
            return []
        return list(self.data[0].keys())

    def total_ayahs(self):
        return len(self.data)

    def total_languages(self):
        return len(self.languages)

    def get_languages(self):
        return self.languages

    # ----------------------------
    # Ayah Access
    # ----------------------------
    def get_ayah(self, ayah_number):
        if ayah_number < 1 or ayah_number > len(self.data):
            raise ValueError("Invalid ayah number")

        ayah = self.data[ayah_number - 1]
        return {
            "ayah_number": ayah_number,
            "translations": ayah
        }

    def get_ayah_by_language(self, ayah_number, language):
        if language not in self.languages:
            raise ValueError(f"Language not found: {language}")

        ayah = self.get_ayah(ayah_number)
        return {
            "ayah_number": ayah_number,
            "language": language,
            "text": ayah["translations"][language]
        }

    # ----------------------------
    # Search
    # ----------------------------
    def search_by_keyword(self, keyword, language=None):
        keyword = keyword.lower()
        results = []

        for idx, ayah in enumerate(self.data):
            ayah_number = idx + 1

            if language:
                if language not in ayah:
                    continue
                text = ayah[language]
                if keyword in text.lower():
                    results.append({
                        "ayah_number": ayah_number,
                        "language": language,
                        "text": text
                    })
            else:
                for lang, text in ayah.items():
                    if keyword in text.lower():
                        results.append({
                            "ayah_number": ayah_number,
                            "language": lang,
                            "text": text
                        })

        return results

    # ----------------------------
    # DataFrame Support (NLP)
    # ----------------------------
    def to_dataframe(self):
        rows = []
        for idx, ayah in enumerate(self.data):
            row = {"ayah_number": idx + 1}
            row.update(ayah)
            rows.append(row)

        return pd.DataFrame(rows)