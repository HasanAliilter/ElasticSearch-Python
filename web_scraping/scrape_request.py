from pyppeteer import launch
from dotenv import load_dotenv
import os
async def scrape_trendyol(page_num):
    
    load_dotenv()

    url = os.getenv("URL")

    chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    browser = await launch(headless=True, executablePath=chrome_path)
    page = await browser.newPage()
    await page.goto(f'{url}{page_num}', {'waitUntil': 'networkidle2'})

    await page.waitForSelector('.prdct-desc-cntnr-ttl')

    ids = await page.querySelectorAll('.p-card-wrppr')
    titles = await page.querySelectorAll('.prdct-desc-cntnr-ttl')
    names = await page.querySelectorAll('.prdct-desc-cntnr-name')
    prices = await page.querySelectorAll('.prc-box-dscntd')
    imgs = await page.querySelectorAll('.p-card-img')

    data = []
    for id, title, name, price, img in zip(ids, titles, names, prices, imgs):
        id_text = await page.evaluate('(element) => element.getAttribute("data-id")', id)
        title_text = await page.evaluate('(element) => element.textContent', title)
        name_text = await page.evaluate('(element) => element.textContent', name)
        price_text = await page.evaluate('(element) => element.textContent', price)
        img_url = await page.evaluate('(element) => element.src', img)
        data.append([id_text.strip(), title_text.strip(), name_text.strip(), price_text.strip(), img_url.strip()])

    await browser.close()

    return data