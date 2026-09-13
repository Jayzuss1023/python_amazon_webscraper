import json
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OXYLABS_BASE_URL = "https://realtime.oxylabs.io/v1/queries"

# Post to OXYLABS which will return our Amazon search result
def post_query(payload):
    username = os.getenv("OXYLABS_USERNAME")
    password = os.getenv("OXYLABS_PASSWORD")

    response = requests.post(OXYLABS_BASE_URL, auth=(username, password), json=payload)
    response.raise_for_status()
    response_json = response.json()

    return response_json

def extract_content(payload):
    # search possible areas for "content" and return "content"
    if isinstance(payload, dict):
        if "results" in payload and isinstance(payload["results"], list) and payload["results"]:
            first = payload["results"][0]
            if isinstance(first, dict) and "content" in first:
                return first["content"] or {}
        if "content" in payload:
            return payload.get("content", {})
    
    return payload

# Return only the needed data from extracted_content
def normalize_product(content):
    category_path = []
    if content.get("category_path"):
        category_path = [cat.strip() for cat in content["category_path"] if cat]
    return {
        "asin": content.get("asin"),
        "url" : content.get("url"),
        "brand": content.get("brand"),
        "price": content.get("price"),
        "stock": content.get("stock"),
        "title": content.get("title"),
        "rating": content.get("rating"),
        "images": content.get("images", []),
        "categories": content.get("category", []) or content.get("categories", []),
        "category_path": category_path,
        "currency": content.get("currency"),
        "buybox": content.get("buybox", []),
        "product_overview": content.get("product_overview", [])
    }

# Amazon product names are usually long.
# This is just a quick method to return a shorter name
def clean_product_name(title):
    if "-" in title:
        title = title.split("-")[0]
    if "|" in title:
        title = title.split("|")[0]
    return title.strip()

# Pull extra related results from search
def extract_search_results(content):
    items = []
    if not isinstance(content, dict):
        return items
    
    if "results" in content:
        results = content["results"]
        if isinstance(results, dict):
            if "organic" in results:
                items.extend(results["organic"])
            if "paid" in results:
                items.extend(results["paid"])
    elif "products" in content and isinstance(content["products", list]):
        items.extend(content["products"])
        
    return items

# Scrape the searched product from Amazon
def scraped_product_details(asin, geo_location, domain):
    payload = {
        "source": "amazon_product",
        "query": asin,
        "geo_location": geo_location,
        "domain": domain,
        "parse": True
    }

    raw = post_query(payload)
    content = extract_content(raw)
    normalized = normalize_product(content)
    
    if not normalized.get("asin"):
        normalized["asin"] = asin
    normalized["geo_location"] = geo_location
    normalized["domain"] = domain
    
    return normalized


# Retrieving only the necessary information needed from the searched item
def normalize_search_result(item):
    asin = item.get("asin") or item.get("product_asin")
    title = item.get("title")

    if not (title or asin):
        return None
    
    return {
        "asin": asin,
        "title": title,
        "category": item.get("category"),
        "price": item.get("price"),
        "rating": item.get("rating")
    }



def search_competitors(query_title, domain, categories, pages=1, geo_location=""):

    st.write("🔎 Searching for competitors")

    search_title = clean_product_name(query_title)
    results = []
    seen_asins = set()

    strategies = ["featured", "price_asc", "price_desc", "avg_ratings"]

    # Create the payload and post to  OXYLABS to generate a search
    for sort_by in strategies:
        for page in range(1, max(1, pages) + 1):
            payload = {
                "source": "amazon_search",
                "query": search_title,
                "parse": True,
                "domain": domain,
                "page": page,
                "sory_by": sort_by,
                "geo_location": geo_location
            }

            if categories and categories[0]:
                payload["refinements"] = {"category": categories[0]}
            
            content = extract_content(post_query(payload))
            # Return "organic" and "paid" results only
            items = extract_search_results(content)

            for item in items:
                # Reduce/restructure - Pull data and return needed data only
                result = normalize_search_result(item)
                if result and result["asin"] not in seen_asins:
                    seen_asins.add(result["asin"])
                    results.append(result)
            
            time.sleep(0.1)
            
    st.write(f"✅ Found {len(results)} competitors")
    return results

