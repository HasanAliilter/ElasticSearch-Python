import asyncio
import pandas as pd

from csv_cut import clean_ids
from scrape_request import scrape_trendyol

async def main():
    all_data = []

    for page_num in range(1, 2):
        print(f"Scraping page {page_num}...")
        data = await scrape_trendyol(page_num)
        all_data.extend(data)

    df = pd.DataFrame(all_data, columns=["Id", "Title", "Name", "Price", "Image"])

    with open("Trendyol.csv", mode='a', newline='') as f:
        df.to_csv(f, index=False, header=f.tell()==0)
        clean_ids("Trendyol.csv")
        print(df)
   

asyncio.get_event_loop().run_until_complete(main())
