# Wikidata Entity Extraction for CAB-Igbo Dataset
# Extracts Igbo cultural entities across domains using SPARQL queries
# Run: python extract_entities_wikidata.py

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import time

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.addCustomHttpHeader("User-Agent", "CAB-Igbo-Research/1.0")

def run_query(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    time.sleep(1)  # avoid hitting Wikidata rate limit
    return sparql.query().convert()

def extract(query, domain, subcategory):
    print(f"Extracting {subcategory} from {domain}...")
    results = run_query(query)
    rows = []
    for r in results["results"]["bindings"]:
        label = list(r.values())[0].get("value", "").strip()
        if label and len(label) > 1:
            rows.append({
                "entity":      label,
                "domain":      domain,
                "subcategory": subcategory,
                "source":      "wikidata",
                "language":    "en"
            })
    print(f"  {len(rows)} entities found")
    return rows


# Food and Cuisine
# Q2095 = food, Q1033 = Nigeria
FOOD_QUERY = """
SELECT DISTINCT ?itemLabel WHERE {
  ?item wdt:P31/wdt:P279* wd:Q2095 .
  ?item wdt:P495 wd:Q1033 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ig". }
}
"""

# Family and Kinship — person names
# Q5 = human, Q27 = country of citizenship Nigeria, Q33578 = Igbo language
NAMES_QUERY = """
SELECT DISTINCT ?personLabel WHERE {
  ?person wdt:P31 wd:Q5 .
  ?person wdt:P27 wd:Q1033 .
  ?person wdt:P103 wd:Q33578 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ig". }
}
LIMIT 2000
"""

# Festivals and Religion — festivals
# Q132241 = festival, Q1033 = Nigeria
FESTIVALS_QUERY = """
SELECT DISTINCT ?itemLabel WHERE {
  ?item wdt:P31/wdt:P279* wd:Q132241 .
  ?item wdt:P17 wd:Q1033 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ig". }
}
"""

# Festivals and Religion — deities
# Q178885 = deity, Q1033 = Nigeria
DEITIES_QUERY = """
SELECT DISTINCT ?itemLabel WHERE {
  ?item wdt:P31/wdt:P279* wd:Q178885 .
  ?item wdt:P17 wd:Q1033 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ig". }
}
"""


all_entities = []
all_entities += extract(FOOD_QUERY,      "food_and_cuisine",   "dish")
all_entities += extract(NAMES_QUERY,     "family_and_kinship", "person_name")
all_entities += extract(FESTIVALS_QUERY, "festivals_religion", "festival")
all_entities += extract(DEITIES_QUERY,   "festivals_religion", "deity")

df = pd.DataFrame(all_entities).drop_duplicates(subset=["entity"])
df.to_csv("entities/wikidata_igbo_entities.csv", index=False)

print(f"\nTotal unique entities: {len(df)}")
print(df["domain"].value_counts())
