from pathlib import Path 
from itertools import takewhile
import csv

import PyPDF2
from py_trans import PyTranslator

NOUN_GENDERS = {"der", "die", "das"}
OUTPUT_CSV_FIELDNAMES = ['gender', 'noun', 'plural', 'translation']


ROOT_DATA_DIR = Path("data")
PDF_FILE = "Linie1_A1-1_Kapitelwortschatz.pdf"
OUTPUT_FILE = "chapter1_8.csv"


def read_pdf_file(file: Path):
    reader = PyPDF2.PdfReader(file)
    page = reader.pages[0].extract_text()
    print(page)
    return reader

def extract_nouns(reader: PyPDF2.PdfReader, noun_genders: set[str]=NOUN_GENDERS) -> set[str]:

    nouns = set()
    for p in range(len(reader.pages)):
        page = reader.pages[p]
        lines =  page.extract_text().split("\n")
        for line in lines:
            noun_in_line = False

            line = line.rstrip()
            words = line.split(" ")
            noun_index=[w in noun_genders for w in words]
            try:
                i = noun_index.index(True)
                noun_gender = words[i]
                updated_line = "".join(words[i+1:])
                line_split = updated_line.split(",")
                noun_ploural = line_split[-1]
                noun_ploural = "".join([s for s in takewhile(lambda x: x not in {"(",")"}, noun_ploural) if s.isalpha()])#line_split[-1]
                noun = line_split[0]
                if noun.isalpha() and noun.istitle() and len(noun) > 1:
                    if noun == "Land":
                        print("d")
                    nouns.add((noun_gender, noun, noun_ploural))

            except ValueError:
                print(f"No noun found in line: '{line}'")
                continue
    print(nouns)
    return nouns


# import csv
# from pathlib import Path

# OUTPUT_FILE = Path("data") / "chapter1_8.csv"
# fieldnames = ['Gender', 'Noun', 'Plural']

# with open(OUTPUT_FILE, mode='w') as csv_file:

#     csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)
#     csv_writer.writeheader()
#     for gender, noun, plural in nouns:
#         csv_writer.writerow({'Gender': gender, 'Noun': noun, 'Plural': plural})

# with open(OUTPUT_FILE, newline='', encoding='utf-8') as f:
#     reader = csv.DictReader(f)
#     rows = list(reader)


# import csv
# p = Path("data") / "nouns_extracted_chapter1_8_google_translated_py_trans.csv"

# fieldnames = ['Gender', 'Noun', 'Plural', 'Translation']

# with open(p, mode='w') as csv_file:
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

#     writer.writeheader()
#     for new_row in new_rows:
#        print(new_row)
#        writer.writerow(new_row)

def translate_nouns(german_nouns: set[str]) -> tuple[list[str], list[str]]:
    german_nouns_list = list(german_nouns)
    all_nouns_one_string = "\n".join([" ".join(n[:2]) for n in german_nouns_list])

    tr = PyTranslator()
    translation = tr.google(all_nouns_one_string, "en")
    print(translation)
    translated_german_nouns_list = trans = translation['translation'].split("\n")
    return german_nouns_list, translated_german_nouns_list

def save_to_csv(german_nouns_list,translated_german_nouns_list, output_file: Path = ROOT_DATA_DIR / OUTPUT_FILE):

    with open(output_file, mode='w') as csv_file:

        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=OUTPUT_CSV_FIELDNAMES)
        csv_writer.writeheader()
        for (gender, noun, plural), translation in zip(german_nouns_list, translated_german_nouns_list):
            csv_writer.writerow(
                {OUTPUT_CSV_FIELDNAMES[0]: gender, 
                 OUTPUT_CSV_FIELDNAMES[1]: noun, 
                 OUTPUT_CSV_FIELDNAMES[2]: plural,
                 OUTPUT_CSV_FIELDNAMES[3]: translation,
                 })

    # with open(output_file, newline='', encoding='utf-8') as f:
    #     reader = csv.DictReader(f)
    #     rows = list(reader)

if __name__ == "__main__":
    pdf_reader = read_pdf_file(file=ROOT_DATA_DIR / PDF_FILE)
    german_nouns = extract_nouns(pdf_reader)

    german_nouns_list, translated_german_nouns_list = translate_nouns(german_nouns)
    save_to_csv(german_nouns_list, translated_german_nouns_list)
    # all_nouns_one_string = "\n".join([" ".join(n[:2]) for n in german_nouns_list])
    # print(german_nouns)
    # from py_trans import PyTranslator

    # tr = PyTranslator()
    # translation = tr.google(all_nouns_one_string, "en")
    # print(translation)
    # translated_german_nouns_list = trans = translation['translation'].split("\n")

    # for (gender, noun, plural), translation in zip(german_nouns_list, translated_german_nouns_list):
    #     print(gender, noun, plural, translation)


    # OUTPUT_FILE = ROOT_DATA_DIR / OUTPUT_FILE

    # with open(OUTPUT_FILE, mode='w') as csv_file:

    #     csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=OUTPUT_CSV_FIELDNAMES)
    #     csv_writer.writeheader()
    #     for (gender, noun, plural), translation in zip(german_nouns_list, translated_german_nouns_list):
    #         csv_writer.writerow(
    #             {OUTPUT_CSV_FIELDNAMES[0]: gender, 
    #              OUTPUT_CSV_FIELDNAMES[1]: noun, 
    #              OUTPUT_CSV_FIELDNAMES[2]: plural,
    #              OUTPUT_CSV_FIELDNAMES[3]: translation,
    #              })

    # with open(OUTPUT_FILE, newline='', encoding='utf-8') as f:
    #     reader = csv.DictReader(f)
    #     rows = list(reader)