import pandas as pd
import streamlit as st

import calendar
from datetime import datetime
from forex_python.converter import CurrencyRates
from streamlit_option_menu import option_menu

import database as db

page_title = 'Travel Expenses Tracker'
page_icon = ':money_with_wings:'

st.set_page_config(page_title=page_title, page_icon=page_icon)
st.title(page_title + " " + page_icon)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

years = [datetime.today().year]

expenses = ["Cost","Tax Amount"]

locations = ['San Diego','Los Angeles']
category = ['Food','Transportation','Accommodation','Internet Plan','Merchandise','Event Ticket','Miscellaneous',]

data = db.fetch_all_data()

total_expenses = sum([sum(i.get("expenses").values()) for i in data])

c = CurrencyRates()
conversion_rate = round(c.get_rate('USD','MYR'),3)

expenses_myr = round(total_expenses*conversion_rate,2)

col1,col2,col3 = st.columns(3)
col1.metric("Total Expenses(MYR)", f'RM {expenses_myr}')
col2.metric("Total Expenses(USD)", f'{total_expenses} $')
col3.metric("Conversion Rate", f'{conversion_rate}')

with st.form("entry_form", clear_on_submit=True):
    period = str(st.date_input("Date"))
    col1, col2 = st.columns(2)
    col1.selectbox("Category:",category, key="category")
    col2.selectbox("Location:", locations, key="locations")
    
    # with st.expander("Tap Here to Input"):
    item_name = st.text_input("Item Name")
    for expense in expenses:
        st.number_input(f'{expense}', min_value=0, format="%i", step=1,key=expense)
    
    comment = st.text_area("", placeholder="Enter a comment here")

    "---"

    submitted = st.form_submit_button("Submit")

    if submitted:

        category = str(st.session_state["category"])
        location = str(st.session_state["locations"])
        expenses = {expense: st.session_state[expense] for expense in expenses}

        db.insert_data(period,category,location,item_name,expenses,comment)
        st.success("Submitted")
    
st.dataframe(pd.DataFrame(data))
