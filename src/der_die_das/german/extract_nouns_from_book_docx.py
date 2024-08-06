from pathlib import Path
import csv

import docx
from py_trans import PyTranslator

NOUN_GENDERS = {"der", "die", "das"}
OUTPUT_CSV_FIELDNAMES = ['gender', 'noun', 'plural', 'translation']


ROOT_DATA_DIR = Path("data")
DATA_FILE = "Linie1_A1-1_Kapitelwortschatz.docx"
OUTPUT_FILE = "all_chapters.csv"


def extract_german_noun_rows(path: Path=ROOT_DATA_DIR / DATA_FILE) -> dict[str, str]:
    """  """
    doc = docx.Document(path)
    extracted_noun_rows = []
    for p in doc.paragraphs:
        line = p.text.split("\t")[1:]
        if line:
            line_split = line[0].split(" ")
            if len(line_split) == 3 and "(" not in line_split[1] and line_split[0].lower() in NOUN_GENDERS:
                extracted_noun_rows.append(
                    {
                        OUTPUT_CSV_FIELDNAMES[0]: line_split[0],
                        OUTPUT_CSV_FIELDNAMES[1]: line_split[1].replace(",",""),
                        OUTPUT_CSV_FIELDNAMES[2]: line_split[2].replace('"',""),
                        OUTPUT_CSV_FIELDNAMES[3]: ""
                    }
                )
    return extracted_noun_rows

def translate_extracted_noun_rows(extracted_noun_rows: dict[str, str])->dict[str, str]:
    all_nouns_one_string = "\n".join([f"{p['gender']} {p['noun']}" for p in extracted_noun_rows])

    tr = PyTranslator()
    translation = tr.google(all_nouns_one_string, "en")
    translated_german_nouns_list = translation['translation'].split("\n")

    for extracted_noun, translated_noun in zip(extracted_noun_rows, translated_german_nouns_list):
        extracted_noun[OUTPUT_CSV_FIELDNAMES[3]] = translated_noun.split(",")[0]

    return extracted_noun_rows

if __name__ == "__main__":
    part1 = extract_german_noun_rows(ROOT_DATA_DIR / "Linie1_A1-1_Kapitelwortschatz.docx")
    part1_trans = translate_extracted_noun_rows(part1)
    part2 = extract_german_noun_rows(ROOT_DATA_DIR / "Linie1_A1-2_Kapitelwortschatz1.docx")
    part2_trans = translate_extracted_noun_rows(part2)
    all_nouns = part1_trans+part2_trans

    with open(ROOT_DATA_DIR / OUTPUT_FILE, mode='w') as csv_file:

        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=OUTPUT_CSV_FIELDNAMES)
        csv_writer.writeheader()
        csv_writer.writerows(all_nouns)
