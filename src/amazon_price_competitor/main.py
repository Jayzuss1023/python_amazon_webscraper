import streamlit as st

from amazon_price_competitor.db import Database
from amazon_price_competitor.oxylabs_client import scraped_product_details
from amazon_price_competitor.services import scrape_and_store_product

def render_header():
    st.title("Amazon Competitor Analysis")
    st.caption("Enter your ASIN to get product insights.")

# UI input fields and submit button
def render_inputs():
    asin = st.text_input("ASIN", placeholder="e.g., B0CX23VSAS")
    geo = st.text_input("Zip/Postal Code", placeholder="e.g, 83980")
    domain = st.selectbox("Domain", [
        "com", "ca", "co.uk", "de", "fr", "it", "ae"
    ])
    return asin.strip(), geo.strip(), domain

# UI for individual product
def render_product_card(product):
    with st.container(border=True):
        # Creating 2 columns for UI
        cols = st.columns([1,2])

        # Try: Get images and load into image block within first column if any
        try:
            images = product.get("images", [])
            if images and len(images) > 0:
                cols[0].image(images[0], width=200)
            else:
                cols[0].write("No image found.")
        except:
            cols[0].write("Error loading images")

        with cols[1]:
            st.subheader(product.get("title") or product["asin"])
            # Create 3 columns within to display data
            info_cols = st.columns(3)
            currency = product.get("currency", "")
            price = product.get("price", "-")
            info_cols[0].metric("Price", f"{currency} {price}" if currency else price)
            info_cols[1].write(f"Brand: {product.get('brand', '-')}")
            info_cols[2].write(f"Product: {product.get('product', '-')}")

            domain_info = f"amazon.{product.get('amazon_domain', '-')}"
            geo_info = product.get("geo_location", "")
            st.caption(f"Domain: {domain_info} | Geo Location: {geo_info}")

            st.write(product.get("url", ""))
            # Key must be assigned to button. The front-end will render a list of procuct cards
            if st.button("Start analyzing competitors", key=f"fanalyze_{product['asin']}"):
                st.session_state["analyzing_asin"] = product["asin"]

def main():
    st.set_page_config(page_title="amazon Competitor Analysis", page_icon="📚", layout="wide")
    render_header()
    asin, geo, domain = render_inputs()

    if st.button("Scrape Product") and asin:
        with st.spinner("Scraping product..."):
            scrape_and_store_product(asin, geo, domain)
        st.success("Product scraped successfully!")

    db = Database()
    products = db.get_all_products()
    print("PRODUCTS", products)
    print("HELLO WORLD")
    if products:
        st.divider()

if __name__ == "__main__":
    main()