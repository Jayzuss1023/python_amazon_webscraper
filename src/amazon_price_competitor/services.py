import streamlit as st
from .db import Database
from .oxylabs_client import scraped_product_details

# scrape and store the product into the DB
# return to render onto the UI
def scrape_and_store_product(asin, geo, domain):
    data = scraped_product_details(asin, geo, domain)
    db = Database()
    db.insert_product(data)


    return data