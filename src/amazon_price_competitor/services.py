import streamlit as st
from .db import Database
from .oxylabs_client import scrape_multiple_products, scraped_product_details, search_competitors

# scrape and store the product into the DB
# return to render onto the UI
def scrape_and_store_product(asin, geo, domain):
    data = scraped_product_details(asin, geo, domain)
    db = Database()
    db.insert_product(data)
    return data

def fetch_and_store_competitors(parent_asin, domain, geo_location, pages=2):
    db = Database()
    parent = db.get_product(parent_asin)
    if not parent:
        return []

    search_domain = parent.get("amazon_domain", domain)
    search_geo = parent.get("geo_location", geo_location)
    st.write(f"🌍 Using domain: {search_domain} | Geo Location: {search_geo}")

    # Extract the categories a product is tied to
    # A category is a searchable context used to expand search results for related products of product in Amazon
    # Example: Glasses, Electronics, Wearable Technologiy, etc....
    search_categories = []
    if parent.get("categories"):
        search_categories.extend(str(cat) for cat in parent["categories"] if cat)
    if parent.get("category_path"):
        search_categories.extend(str(cat) for cat in parent["category_path"] if cat)

    # Make each category unique. Prevent duplicates and strip away white spaces
    search_categories = list(set(
        cat.strip()
        for cat in search_categories
        if cat and isinstance(cat, str) and cat.strip()
    ))

    all_results = []
    # Search for related categories from OXYLAB by passing in said category
    for category in search_categories[:3]:
        search_results = search_competitors(
            query_title=parent["title"],
            domain=search_domain,
            categories=[category],
            pages=pages,
            geo_location=search_geo
        )

        all_results.extend(search_results)

    # List all unique asins
    competitor_asins = list(set(
        r.get("asin") for r in all_results
        if r.get("asin") and r.get("asin") != parent_asin and r.get("title")
    ))

    scrape_multiple_products(competitor_asins[:20], geo_location, domain)

