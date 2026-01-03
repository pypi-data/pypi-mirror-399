import re

BOOK_TITLE_MAP = {
    "صحیح بخاری": "Sahih Bukhari",
    "صحیح مسلم": "Sahih Muslim",
    "جامع الترمذي": "Jami at-Tirmidhi",
    "سنن ابوداود": "Sunan Abu Dawood",
    "سنن نسائی": "Sunan an-Nasa'i",
    "سنن ابن ماجہ": "Sunan Ibn Majah",
    "الادب المفرد" : "Al-Adab al-Mufrad",
    "الفتح الربانی مسند احمد فقہی ترتیب" : "Fatah Al Rabani Musnad Ahmed",
    "معجم الصغير للطبراني": "Al-Mu'jam al-Saghir Tabarani",
    "مسند احمد": "Musnad Ahmad",
    "سلسله احاديث صحيحه": "Silsila_Sahiha",
    "سنن دارمی": "Sunan Darmi",
    "بلوغ المرام من أدلة الأحكام": "Bulugh al-Maram",
    "مشکوۃالمصابیح": "Mishkat al-Masabih",
    "سنن الکبری للبیھقی": "Sunan Al Kubra Bayhaqi",
    "اللؤلؤ و المرجان" : "Al-Lulu wal-Marjan",
    "المستدرك على الصحيحين":"Al Mustadrak",
    "مصنف ابن ابي شىيبه" : "Musannaf Ibn Abi Shaybah",
    "موطا امام مالک": "Muwatta Imam Malik",
    "صحیح ابن خزیمہ": "Sahih Ibn Khuzaymah",
    "شمائل ترمذی" : "Shamail-E-Tirmazi",
    "سنن الدارقطني" : "Sunan al-Daraqutni"
}

def normalize_text(text):
    """
    Normalize Arabic, Urdu, and English text for consistent searching.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[ؓؒ]", "", text)
    text = re.sub(r"رضي الله عنه|رضي الله عنها", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
