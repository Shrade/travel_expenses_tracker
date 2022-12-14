import pandas as pd
import streamlit as st
import os
import calendar
from datetime import datetime
from forex_python.converter import CurrencyRates
from streamlit_option_menu import option_menu

import database as db
import helper

authenticator = helper.main()

with st.sidebar:
    with st.sidebar:
        st.title("Quick Access")
        st.subheader('Maps')
        st.write(
            """
            Los Angeles International Airport        
            https://tinyurl.com/googlelaxca\n
            Union Station, CA          
            https://tinyurl.com/googleutca\n
            Santa Fe Depot, San Diego       
            https://tinyurl.com/googlesfsd\n
            HI San Diego, CA       
            https://tinyurl.com/googlehisd\n
            San Diego Convention Centre, CA        
            https://tinyurl.com/googlesdcc\n
            HI Los Angeles, CA       
            https://tinyurl.com/googlehila
        """
        )

        st.write("***")

        st.subheader('Bus Ticket')
        st.write("""
            FlyAway LAX          
            https://tinyurl.com/laxflyawayg
            """)

        st.write("***")

        st.subheader("eSim")
        st.write("""
            Airalo        
            https://www.airalo.com\n
            T-Mobile                  
            https://www.t-mobile.com/offers/free-trial
        """)
        
        st.write("***")

        st.subheader("Suggested Places")
        st.write("""
            Los Angeles   
            1. Santa Monica Pier
            2. 3rd Street Promenade
            3. Downtown Santa Monica  
            4. The Grove
            5. The Original Farmer's Market
            6. Rodeo Drive    
            7. Downtown LA
            8. Griffith Observatory (if applicable)      
        """)

        st.write("***")

        st.subheader("Places to eat")
        st.write("""
            1. In N Out       
            2. Chick-fil-A 
            3. Lucky's Lunch/Breakfast (SD)      
            4. Benny's Tacos (LA)     
            5. KazuNori: The Original Hand Roll Bar (LA)       
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
     
        drive_link = os.getenv("DRIVE_LINK")
        with st.expander("Travel Documents"):
            link=f'[Travel Document]({drive_link})'
            st.markdown(link,unsafe_allow_html=True)
            
        with st.expander("Maybank Amex"):
            st.write(
                    """
                **Krisflyer**           
                24-Hour Customer Service   : 1800-88-9559         
                Calls from Overseas        : 603-7844-3595        
                Global Assist              : 603-7949-0688
            """)

        dav_em_num = os.getenv("DAVID_EM_NUM")
        ryan_em_num = os.getenv("RYAN_EM_NUM")
        ckm_em_num = os.getenv("CKM_EM_NUM")
        
        with st.expander("Emergency Contact"):
            st.markdown(f"""**David's Sister**   
            {dav_em_num}
            """)
            
            st.markdown(f"""**Ryan Wong**   
            {ryan_em_num}
            """)

            st.markdown(f"""**Ryan Wong's Mom**   
            {ckm_em_num}
            """)
        
    authenticator.logout('Logout', 'main')  

elif authentication_status == False:
    st.error('Username/password is incorrect')
