# Proverb Extraction from Academic PDFs
# Extracts Igbo proverbs from three source papers into a unified CSV
# Run: python extract_proverbs_pdf.py

import pdfplumber
import pandas as pd
import re

def extract_anyabuike(pdf_path):
    # 60 numbered proverbs in two-column format (Igbo + English)
    proverbs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            matches = re.findall(
                r'\d+\.\s+([A-Za-zÀ-ÿ][^\n]+)\n\s+([A-Z][^\n]+(?:\n[^\n]+)*)',
                text
            )
            for igbo, english in matches:
                proverbs.append({
                    "igbo_text":           igbo.strip(),
                    "english_translation": english.strip(),
                    "theme":               "",
                    "source":              "Anyabuike (2020)"
                })
    return proverbs

def extract_onu(pdf_path):
    # 30 proverbs with theme labels before each one
    proverbs = []
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    blocks = re.findall(
        r'Theme of ([^\n:]+)[:\n]+Proverb \d+\s+([A-Za-zÀ-ÿ][^\n]+)\s+([A-Z][^\n]+)',
        full_text
    )
    for theme, igbo, english in blocks:
        proverbs.append({
            "igbo_text":           igbo.strip(),
            "english_translation": english.strip(),
            "theme":               theme.strip(),
            "source":              "Onu (2018)"
        })
    return proverbs

def extract_ngele(pdf_path):
    # 20 proverbs in trilingual table: Igbo | English | French
    proverbs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    igbo    = row[0]
                    english = row[1] if len(row) > 1 else ""
                    french  = row[2] if len(row) > 2 else ""
                    if igbo and len(igbo) > 10 and igbo[0].isupper():
                        proverbs.append({
                            "igbo_text":           igbo.strip(),
                            "english_translation": english.strip() if english else "",
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
df = df.drop_duplicates(subset=["igbo_text"])
df.to_csv("entities/igbo_proverbs.csv", index=False)

print(f"Total proverbs extracted: {len(df)}")
print(df["source"].value_counts())
