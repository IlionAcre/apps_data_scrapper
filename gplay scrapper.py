from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import App_gstore, App, Publisher, Base
import re
from datetime import datetime as dt
import asyncio
import os
from dotenv import load_dotenv


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

PATH_GPLAY = os.getenv("PATH_GPLAY")

engine = create_engine("sqlite:///app_data.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

#Utility functions

def is_rating(tag):
    return tag.name == 'span' and tag.has_attr('aria-label') and 'Average Rating:' in tag['aria-label']


def clean_string(string, pattern):
    return re.sub(pattern, '', string)
    

def add_unique_apps(name, publisher):
    exists = session.query(App).filter_by(name=name, publisher=publisher).first()
    if not exists:
        new_app = App(name=name, publisher=publisher)
        session.add(new_app)
        session.commit()
        return new_app

def add_unique_app(instance, unique_attributes):
    model_class = type(instance)
    existing_instance = session.query(model_class).filter_by(**unique_attributes).first()

    if existing_instance:
        return existing_instance
    try:
        session.add(instance)
        session.commit()
        return instance 
    except:
        session.rollback()
        return None
    

price_pattern = r'^(In-App Purchases • )?Price: \$?'
downloads_pattern = r'[,()]'
rating_pattern = r'Average Rating: | stars'


dt_date = dt(2024, 4, 19)

async def fetch_gstore(input_date):
    date_string = input_date.strftime("%Y-%m-%d")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{PATH_GPLAY}{date_string}", wait_until='networkidle')
        content = await page.inner_html(".MuiTable-root")
        
        soup = BeautifulSoup(content, "html.parser")
        rows = soup.select(".MuiTableRow-root")

        counter = 0
        for row in rows:
            cells = row.find_all(class_="css-1e8tjqr")
            whole_row = ""
            for cell in cells:

                name = cell.find(class_="css-1wq0212").text
                publisher = cell.find(class_="css-11ovsk1").text
                price_raw = clean_string(string=cell.find(class_="css-11j76p1").text, pattern=price_pattern)
                price = 0 if price_raw == "Free" else float(price_raw)
                downloads = int(clean_string(string=cell.find(class_="css-19d5dex").text, pattern=downloads_pattern))
                rating = float(cell.find(is_rating)["aria-label"].replace("Average Rating: ", ""). replace(" stars", ""))
                rating2 = float(clean_string(string=cell.find(is_rating)["aria-label"], pattern=rating_pattern))
                position = counter
                date = date_string


                new_publisher = Publisher(name=publisher)
                new_publisher = add_unique_app(new_publisher, unique_attributes={"name":new_publisher.name})

                new_app = App(name=name, publisher=new_publisher)
                new_app = add_unique_app(new_app, unique_attributes={"name":new_app.name})

                new_app_gstore = App_gstore(
                    app=new_app,
                    price=price,
                    downloads=downloads,
                    rating=rating2,
                    position=position,
                    date=input_date
                )              
                session.add(new_app_gstore)
            
        
                
            counter += 1
         
        await browser.close()
    
    session.commit()

asyncio.run(fetch_gstore(dt_date))