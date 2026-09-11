import streamlit as st

from amazon_price_competitor.oxylabs_client import scraped_product_details

def render_header():
    st.title("Amazon Competitor Analysis")
    st.caption("Enter your ASIN to get product insights.")

def render_inputs():
    asin = st.text_input("ASIN", placeholder="e.g., B0CX23VSAS")
    geo = st.text_input("Zip/Postal Code", placeholder="e.g, 83980")
    domain = st.selectbox("Domain", [
        "com", "ca", "co.uk", "de", "fr", "it", "ae"
    ])
    return asin.strip(), geo.strip(), domain

def main():
    st.set_page_config(page_title="amazon Competitor Analysis", page_icon="📚", layout="wide")
    render_header()
    asin, geo, domain = render_inputs()

    if st.button("Scrape Product") and asin:
        with st.spinner("Scraping product..."):
            product = scraped_product_details(asin, geo, domain)
        st.success("Product scraped successfully!")
        st.write(product)

if __name__ == "__main__":
    main()