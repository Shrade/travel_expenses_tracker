from deta import Deta
import os
from dotenv import load_dotenv

load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

deta = Deta(DETA_KEY)

db = deta.Base("travel_expenses")

def insert_data(date,category,location,item_name,expenses,comment):
    return db.put({
        'date': date,
        'category': category,
        'location': location,
        'item_name': item_name,
        'expenses': expenses,
        'comment': comment,
        }
    )

def fetch_all_data():
    res = db.fetch()
    return res.items