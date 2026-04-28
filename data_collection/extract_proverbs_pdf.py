
import pdfplumber

def debug_pdf(pdf_path, label, pages=(3, 5)):
    print(f"\n{'='*60}")
    print(f"DEBUG: {label}")
    print(f"{'='*60}")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i < pages[0] or i > pages[1]:
                continue
            text = page.extract_text()
            if text:
                print(f"\n--- Page {i+1} ---")
                print(text[:2000])

debug_pdf("sources/anyabuike_2020_igbo_proverbs_worldview.pdf", "Anyabuike", pages=(2, 6))
debug_pdf("sources/onu_2018_igbo_proverbs_aesthetic.pdf",       "Onu",       pages=(3, 6))
debug_pdf("sources/ngele_2019_igbo_proverbs_translation.pdf",   "Ngele",     pages=(3, 6))
