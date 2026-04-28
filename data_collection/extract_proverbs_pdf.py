# Proverb Extraction from Academic PDFs
# Sources: Anyabuike (2020), Onu (2018), Ngele et al.
# Run: python extract_proverbs_pdf.py

import pdfplumber
import pandas as pd
import re

def clean(text):
    text = re.sub(r'\(TFA[^)]*\)', '', text)
    text = re.sub(r'\(TIP[^)]*\)', '', text)
    text = re.sub(r'\(Our translation[^)]*\)', '', text)
    text = re.sub(r'DOI:[^\n]+', '', text)
    text = re.sub(r'www\.[^\s]+', '', text)
    return text.strip()

def extract_anyabuike(pdf_path):
    # 60 numbered proverbs, two-column layout
    # pdfplumber merges columns: "N. Igbo text   English text" on same line
    proverbs = []
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    pattern = r'(?<!\d)(\d{1,2})\.\s+(.+?)(?=(?<!\d)\d{1,2}\.\s+[A-Z]|$)'
    matches = re.findall(pattern, all_text, re.DOTALL)

    seen = set()
    for num_str, content in matches:
        num = int(num_str)
        if num < 1 or num > 60 or num in seen:
            continue
        seen.add(num)

        content = clean(content)
        lines = [l.strip() for l in content.split('\n') if l.strip()]

        igbo, english = "", ""
        if lines:
            parts = re.split(r'\s{2,}', lines[0], maxsplit=1)
            if len(parts) == 2:
                igbo    = parts[0].strip()
                english = parts[1].strip()
                if len(lines) > 1:
                    english += " " + " ".join(lines[1:])
            else:
                igbo    = lines[0]
                english = " ".join(lines[1:]) if len(lines) > 1 else ""

        if igbo and len(igbo) > 5:
            proverbs.append({
                "igbo_text":           igbo,
                "english_translation": english.strip(),
                "theme":               "",
                "source":              "Anyabuike (2020)"
            })

    return proverbs

def extract_onu(pdf_path):
    # 30 proverbs with "Theme of X: / Proverb N / Igbo / English" format
    proverbs = []
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    pattern = r'Theme of\s+([^\n:]+)[:\n]+\s*Proverb\s+\d+\s*\n\s*([^\n]{5,})\s*\n\s*([A-Z][^\n]+)'
    blocks = re.findall(pattern, all_text)

    for theme, igbo, english in blocks:
        igbo    = clean(igbo)
        english = clean(english)
        if igbo and len(igbo) > 5:
            proverbs.append({
                "igbo_text":           igbo,
                "english_translation": english,
                "theme":               theme.strip(),
                "source":              "Onu (2018)"
            })

    return proverbs

def extract_ngele(pdf_path):
    # Trilingual table: Igbo | English | French
    # Igbo column has font encoding issues — English and French only
    proverbs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    english = row[1] if len(row) > 1 else ""
                    french  = row[2] if len(row) > 2 else ""
                    if not english or len(english.strip()) < 10:
                        continue
                    english = english.strip()
                    if english[0].isupper():
                        proverbs.append({
                            "igbo_text":           "",
                            "english_translation": english,
                            "french_translation":  french.strip() if french else "",
                            "theme":               "",
                            "source":              "Ngele et al."
                        })
    return proverbs


all_proverbs = []
all_proverbs += extract_anyabuike("sources/anyabuike_2020_igbo_proverbs_worldview.pdf")
all_proverbs += extract_onu("sources/onu_2018_igbo_proverbs_aesthetic.pdf")
all_proverbs += extract_ngele("sources/ngele_2019_igbo_proverbs_translation.pdf")

df = pd.DataFrame(all_proverbs)
df = df.drop_duplicates(subset=["english_translation"])
df = df[df["english_translation"].str.len() > 5]
df.to_csv("entities/igbo_proverbs.csv", index=False)

print(f"Total proverbs extracted: {len(df)}")
print(df["source"].value_counts())
