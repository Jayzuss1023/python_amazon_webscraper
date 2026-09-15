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

    search_domain = parent.get("domain", domain)
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

    TARGET_COMPETITORS = 20
    competitor_asins = []
    seen_asins = {parent_asin}

    # Search one category at a time; stop once we have enough unique ASINs
    # Monitor TARGET_COMPETITORS. Provide evaluated reasoning to break loop. Increase performance
    categories_to_try = search_categories[:3] or [None]
    for category in categories_to_try:
        if len(competitor_asins) >= TARGET_COMPETITORS:
            break

        needed = TARGET_COMPETITORS - len(competitor_asins)
        # Make a call to OXYLABS and
        # Return related products from related batches - "featured" and "price_asc"
        search_results = search_competitors(
            query_title=parent["title"],
            domain=search_domain,
            categories=[category] if category else [],
            pages=pages,
            geo_location=search_geo,
            max_results=needed,
            exclude_asins=seen_asins,
        )

        for result in search_results:
            asin = result.get("asin")
            if asin and asin not in seen_asins and result.get("title"):
                seen_asins.add(asin)
                competitor_asins.append(asin)
                if len(competitor_asins) >= TARGET_COMPETITORS:
                    break

    # Enrich the product data from the returned results
    # by making a separate call to OXYLABS for each product
    product_details = scrape_multiple_products(competitor_asins, search_geo, domain)

    st.write("📈 Competitor Summary")
    # Save product to database
    for comp in product_details:
        comp["parent_asin"] = parent_asin
        db.insert_product(comp)

        price = comp.get("price", "-")
        currency = comp.get("currency", "-")
        if isinstance(price, (int, float)):
            price_str = f"{currency} {price:,.2f}" if currency else f"{price:,.2f}"
        else:
            price_str = str(price)
        
        st.write(f"- {comp.get('title')} - {price_str}")
    st.write("---")    

    return product_details


