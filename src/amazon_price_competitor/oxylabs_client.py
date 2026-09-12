import json
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OXYLABS_BASE_URL = "https://realtime.oxylabs.io/v1/queries"


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
    print(raw)
    content = extract_content(raw)
    normalized = normalize_product(content)
    print("NORMALIZED PRODUCT------------", normalized)
    
    if not normalized.get("asin"):
        normalized["asin"] = asin
    normalized["geo_location"] = geo_location
    normalized["domain"] = domain
    return normalized