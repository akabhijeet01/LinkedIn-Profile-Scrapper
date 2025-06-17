#!/usr/bin/env python3
import json
import sys
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from collections import OrderedDict

import requests
import re
from dotenv import load_dotenv
import os

load_dotenv()

# Access AZURE_ENDPOINT and AZURE_API_KEY
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

def generate_queries(person):
    prompt = f"""
You are a search engine assistant. Based on the details below, generate *5 distinct, focused search queries* to help locate this person online, specifically on platforms like LinkedIn. 
Each query should be tailored with different combinations of details to increase the chance of finding the right match.

Use the following guidelines:
1. Query with full name and intro.
2. Query with name only.
3. Query with name and all available details.
4. Query with name and timezone.
5. Query with intro and everything else except the name.

Add the word "LinkedIn" to all queries to focus the search.

Person Details:
- Full Name: {person.get("name", "")}
- Intro / Bio: {person.get("intro", "")}
- Timezone / Location: {person.get("timezone", "")}
- Industry: {person.get("company_industry", "")}
- Company Size: {person.get("company_size", "")}
- Known Social Profiles: {', '.join(person.get("social_profile", []))}

Only return the 5 queries, each on a new line, without numbering or extra explanation.
"""

    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_API_KEY
        }

        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(AZURE_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        output = response.json()["choices"][0]["message"]["content"].strip()

        # Remove <think> blocks and split into lines
        output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
        queries = [line.strip() for line in output.splitlines() if line.strip()]

    except Exception as e:
        print(f"Failed to generate queries for {person.get('name', 'unknown')}: {e}")
        queries = [person.get("name", "") + " LinkedIn"]

    print(f"Generated queries for {person.get('name', '')}:\n" + "\n".join(queries))
    return queries

def init_driver():
    options = Options()
    #options.add_argument("--headless=new")  # Run headless
    #options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    return driver


def safe_search_duckduckgo(driver, query, max_results=15):
    search_url = "https://duckduckgo.com/"
    driver.get(search_url)
    time.sleep(random.uniform(4, 15))

    # Perform search
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(query + Keys.ENTER)
    time.sleep(3)

    urls = set()
    page = 1

    while len(urls) < max_results and page <= 10:
        print(f"🟦 Page {page} — results so far: {len(urls)}")

        links = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="result-title-a"]')
        for link in links:
            url = link.get_attribute("href")
            print(url)
            if url and url.startswith("https://www.linkedin.com/in/"):
                urls.add(url)
            if len(urls) >= max_results:
                break
        time.sleep(5)
        # Try to go to next page
        try:
            more_btn = driver.find_element(By.ID, "more-results")
            driver.execute_script("arguments[0].click();", more_btn)
            page += 1
            time.sleep(random.uniform(3, 5))
        except Exception:
            print("No 'More results' button found or clickable.")
            break

    return list(urls)

def main():
    if len(sys.argv) != 3:
        print("Usage: python duckduckbot.py <input_json> <output_json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    driver = init_driver()
    I_dont_want_queries_regen = 1
    final_output = []

    for person in data:
        if I_dont_want_queries_regen:
            if "query" in person and isinstance(person["query"], list) and person["query"]:
                queries = person["query"]
            else:
                try:
                    queries = generate_queries(person)
                    person["query"] = queries
                except Exception as e:
                    print(f"Skipping record: {e}")
                    continue
        else:
            try:
                queries = generate_queries(person)
                person["query"] = queries
            except Exception as e:
                print(f"Skipping record: {e}")
                continue

        all_results = set()
        for query in queries:
            print(f"Searching: {query}")
            try:
                search_results = safe_search_duckduckgo(driver, query)
                all_results.update(search_results)
            except Exception as e:
                print(f"Search failed for {person.get('name', 'unknown')}: {e}")
            time.sleep(random.uniform(3, 6))

        person["search_results"] = list(all_results)

        # Append result to the output file as JSONL
        final_output.append(person)


        time.sleep(random.uniform(3, 6))  # Sleep between requests

    driver.quit()
    
    # ensure key order and pretty‑print once
    key_order = [
        "name", "image", "intro", "timezone",
        "company_industry", "company_size", "social_profile",
        "query", "search_results"
    ]
    ordered_list = []
    for p in final_output:
        od = OrderedDict()
        for k in key_order:
            od[k] = p.get(k, None)
        ordered_list.append(od)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ordered_list, f, ensure_ascii=False, indent=4)

    print(f"[INFO] Final JSON written to {output_file}")



if __name__ == "__main__":
    main()
