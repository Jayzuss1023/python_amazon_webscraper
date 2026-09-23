# Amazon Price Competitor

A small Streamlit app that scrapes an Amazon product by ASIN, finds similar listings, and uses an LLM to summarize how the product stacks up on price, positioning, and ratings.

I built this to make competitor research less manual. Instead of searching Amazon by hand, you drop in an ASIN, pick a marketplace and zip code, and the app handles scraping, storage, and analysis.

## What it does

1. **Scrape a product** — enter an ASIN, zip/postal code, and Amazon domain (`.com`, `.ca`, `.co.uk`, `.de`, `.fr`, `.it`, `.ae`).
2. **Store it locally** — product details go into a TinyDB file so you can come back to them later.
3. **Find competitors** — searches Amazon using the product title and category, then pulls details for up to 20 related listings.
4. **Analyze with GPT-4** — LangChain runs a structured comparison (summary, positioning, top competitors, recommendations).

## How it works

Amazon product pages aren't straightforward to scrape directly, so the app uses [Oxylabs](https://oxylabs.io/) as a scraping API. Two query types are used:

- `amazon_product` — full product details for a given ASIN
- `amazon_search` — related listings, sorted by featured and price, optionally filtered by category

To keep results relevant (and avoid extra API calls), competitor search:

- shortens long Amazon titles before searching
- uses the product's categories as search context
- skips duplicate ASINs
- stops once it has about 20 unique competitors

Scraped data is saved in TinyDB. If competitors for a product already exist, the app reuses them instead of scraping again. There's a refresh button if you want a fresh pull.

The LLM step uses LangChain plus a Pydantic schema so the output stays consistent: summary, market positioning, a short competitor list, and a few recommendations. Prices are passed through with their original currency so comparisons don't mix marketplaces.

## Tech stack

| Piece | What it's for |
| --- | --- |
| Python 3.12 | Runtime |
| Streamlit | UI |
| Oxylabs Realtime API | Amazon product + search scraping |
| TinyDB | Local JSON database |
| LangChain + OpenAI (GPT-4) | Competitor analysis |
| Pydantic | Structured LLM output |
| python-dotenv | API keys from `.env` |
| uv | Dependency / project management |

**`main.py`** — page layout, ASIN/geo/domain inputs, product cards, pagination, and the analyze/refresh buttons.

**`oxylabs_client.py`** — posts queries to Oxylabs, normalizes product/search payloads, and scrapes competitor ASINs with a progress bar.

**`services.py`** — glue between the UI, Oxylabs, and the database. Handles category-based competitor search and storing results with a `parent_asin` link.

**`llm.py`** — loads the product plus competitors, asks GPT-4 for a structured analysis, and formats it for the UI.

**`db.py`** — insert/get/search products. Duplicate ASINs are skipped on insert.

## Usage

1. Enter an ASIN (e.g. `B0CX23VSAS`), a zip/postal code, and a domain.
2. Click **Scrape Product**. The listing shows up as a card with image, price, brand, and marketplace info.
3. Click **Start analyzing competitors** on a card. The app searches Amazon and stores related products.
4. Click **Analyze with LLLM** to generate the GPT-4 writeup. Use **Refresh Competitors** if you want to scrape again.

Scraped products are paginated (10 per page) so the list stays usable as it grows.

## Notes

- This is a personal/learning project, not a production tool. API usage (Oxylabs plus OpenAI) can add up if you scrape a lot of products.
- Don't commit `.env` or `data.json` if they contain keys or scraped data you don't want public.
- Competitor matching is based on title plus category search, so results are "similar listings," not a guaranteed same SKU match.
- Geo location matters. Amazon prices and availability change by zip code and marketplace.
