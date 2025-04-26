import requests
import random
import time as t
from bs4 import BeautifulSoup

"""
Wikipedia web scraping code to assemble final project datasets.

Class: Data Wrangling
Professor: Fengjiao Wang
Author: Benjamin Keefer
Version: April 14th, 2025
"""

prefix = "https://en.wikipedia.org"
output_file = "Wikipedia_Mathematics.csv"
excluded_strings = ["File:", "Special:", "ISBN", "Help:", "Portal:", "Category:", "Talk:", "Wikipedia:", 
                    "wikibook", "wikiquote", "Template", "Main_Page", "wikimedia", "wikidata",
                    ".org", ".com"]
links = set()

# Return boolean: true if the given url is a valid wikipedia link, false otherwise
def is_valid(url) -> bool:
    # Ensures the url is a wikipedia link that has not been seen yet
    if url is None or links.__contains__(url) or not url.__contains__("/wiki/"): return False

    # Checks for unwanted substrings
    for phrase in excluded_strings:
        if(url.__contains__(phrase)): return False

    return True

# Processes the data from the url and writes relevant information to the dataset
def process_link(url):
    links.add(url) # Ensures this url isn't visited twice
    t.sleep(1.0 + random.random() * 4) # Prevents overwhelming the site's servers

    # Gets the webpage and loads it into bs4
    soup = BeautifulSoup(requests.get(prefix + url).text, "html.parser")
    
    # Finds the number of valid URLs in the current webpage
    num_of_valid_links = 0
    for link in [l.get("href") for l in soup.find_all("a")]:
        if not is_valid(link): continue
        num_of_valid_links += 1

    # Finds the number of supported languages for the wikipedia page.
    num_of_supported_langs = 1
    texts = soup.find_all("span",attrs={"class":"vector-dropdown-label-text"})
    for x in texts:
        if(x.text.__contains__("languages")):
            num = x.text.split(" ")[0]
            if num.isdigit():
                num_of_supported_langs = num
            break

    # Computes number of words in the wikipedia page
    word_count = 0
    for line in soup.text.split("\n"):
        if(line == "\n" or line == "" or line == "-"):
            continue
        for _ in line.split(" "):
            word_count += 1

    # Writes the url's data to the csv file
    with open(output_file, "a") as w:
        w.write(f"{prefix}{url},{num_of_valid_links},{num_of_supported_langs},{word_count}\n")
    return

def clean_dataset():
    cleaned_dataset = ""
    with open("Wikipedia_Mathematics.csv", "r") as r:
        csv = r.read().rstrip()
        dataset = csv.split("\n")[1:]
        idx = 0
        for row in dataset:
            idx += 1
            row = row.rstrip().split("https://en.wikipedia.org/wiki/")[1]
            if ",_" in row:
                cleaned_dataset += row.replace(",_", "") + "\n"
            else:
                cleaned_dataset += row + "\n"
    with open("Wikipedia_Mathematics_Clean.csv", "w") as w: w.write(cleaned_dataset.rstrip())

# Gets "root" page before processing all wikipedia pages it references
def main():
    root_page = "/wiki/Mathematics"

    with open(output_file, "a") as w: w.write("URL,#_of_valid_wiki_pages_linked,#_of_supported_languages,word_count\n")
    for url in [l.get("href") for l in BeautifulSoup(requests.get(prefix + root_page).text, "html.parser").find_all("a")]:
        if(is_valid(url)): process_link(url)
        
    clean_dataset()
    return

# Calls main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Exception: {e}")