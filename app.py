import pandas as pd
import streamlit as st

import calendar
from datetime import datetime
from forex_python.converter import CurrencyRates
from streamlit_option_menu import option_menu

import database as db
import helper

authenticator = helper.main()
st.title('Quick Access')
with st.expander("Information"):
    st.write("""
        [Los Angeles International Airport](https://www.google.com/maps/search/lax+ca/@33.9445676,-118.4037581,15.25z) \n
        [Union Station, CA](https://www.google.com/maps/place/Union+Station/@36.7867511,-118.9325625,4z/data=!4m9!1m2!2m1!1sunion+station+CA!3m5!1s0x80c2c72866bdd1c1:0x2a8810a25b3877cf!8m2!3d34.056183!4d-118.2365887!15sChB1bmlvbiBzdGF0aW9uIENBkgENdHJhaW5fc3RhdGlvbuABAA) \n
        [Santa Fe Depot](https://www.google.com/maps/place/San+Diego/@32.7168578,-117.1717344,17z/data=!3m1!4b1!4m10!3m9!1s0x80deab355386aaab:0x98e321e1679bd391!5m4!1s2022-10-10!2i3!4m1!1i2!8m2!3d32.7168533!4d-117.1695457) \n
        [HI San Diego](https://www.google.com/maps/place/HI+San+Diego+Downtown/@32.7113366,-117.1642744,17z/data=!3m1!4b1!4m10!3m9!1s0x80d95359bceddd73:0x1c4d3c69c0923875!5m4!1s2022-10-10!2i3!4m1!1i2!8m2!3d32.71137!4d-117.1598052) \n
        [San Diego Convention Centre](https://www.google.com/maps/place/San+Diego+Convention+Center/@32.7055022,-117.1622915,17z/data=!3m2!4b1!5s0x80d9535a81657f0b:0x4a731a310e109ee5!4m10!3m9!1s0x80d953574be55d8b:0x568846370a748ca5!5m4!1s2022-10-10!2i3!4m1!1i2!8m2!3d32.7054977!4d-117.1601028)\n
        [HI Los Angeles](https://www.google.com/maps/place/HI+Los+Angeles+Santa+Monica+Hostel/@34.0141165,-118.49856,17z/data=!3m1!4b1!4m10!3m9!1s0x80c2a4d03b9d770b:0x3bc48de3c7234862!5m4!1s2022-10-10!2i3!4m1!1i2!8m2!3d34.0141201!4d-118.4964023)\n
        """)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    
    page_title = 'Travel Expenses Tracker'
    page_icon = ':money_with_wings:'
    st.title(page_title + " " + page_icon)

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Expenses","Summary","Documents"],
        icons=["credit-card","bar-chart","folder"],
        menu_icon="cast", 
        default_index=0,
        orientation='horizontal'
    )
    
    if selected == 'Expenses':
        
        years = [datetime.today().year]
        expenses = ["Price(USD)","Tax Amount"]
        locations = ['San Diego','Los Angeles']
        category = ['Food','Transportation','Accommodation','Internet Plan','Merchandise','Event Ticket','Miscellaneous',]

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
        
    elif selected == 'Summary':
        
        def flatten_dict(elements):

            filter_list = ['Price(USD)', 'Tax Amount']
            filtered = {key: val for key, val in elements.items() if key in filter_list}
            return pd.Series(filtered)

        data = db.fetch_all_data()

        df = pd.DataFrame(data)

        flatten_df = pd.concat([df, df['expenses'].apply(flatten_dict)], axis=1)
        flatten_df = flatten_df[['date','item_name','category','location','Price(USD)']]

        c = CurrencyRates()
        conversion_rate = round(c.get_rate('USD','MYR'),3)

        total_expenses = flatten_df['Price(USD)'].sum()
        expenses_myr = round(total_expenses*conversion_rate,2)

        col1,col2,col3 = st.columns(3)
        col1.metric("Total Expenses(MYR)", f'RM {expenses_myr}')
        col2.metric("Total Expenses(USD)", f'{total_expenses} $')
        col3.metric("Conversion Rate", f'{conversion_rate}')

        st.dataframe(flatten_df)
        
        @st.cache
        def convert_df(df):
            return df.to_csv().encode('utf-8')

        csv = convert_df(flatten_df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='travel_expenses.csv',
            mime='text/csv',
        )
        
    elif selected == 'Documents':
        
        drive_link = st.secrets["DRIVE_LINK"]
        with st.expander("Travel Documents"):
            link=f'[Travel Document]({drive_link})'
            st.markdown(link,unsafe_allow_html=True)
            
        with st.expander("Maybank Amex"):
            st.markdown('''Krisflyer\n
            24-Hour Customer Service   : 1800-88-9559
    Calls from Overseas        : 603-7844-3595
    Global Assist              : 603-7949-0688
            ''')

        dav_em_num = st.secrets["DAVID_EM_NUM"]
        with st.expander("Emergency Contact"):
            st.markdown(f'''David's Sister\n
            {dav_em_num}
            ''')
        
    authenticator.logout('Logout', 'main')  

elif authentication_status == False:
    st.error('Username/password is incorrect')
