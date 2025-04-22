# Import python package
import streamlit as st
from snowflake.snowpark.functions import col,when_matched
import requests
import pandas as pd

# Write directly to the app
st.title(f" :cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

import streamlit as st

name_on_order = st.text_input("Name on the smoothie:")
st.write("The name on the smoothie will be:",name_on_order)


option = st.selectbox(
    "What is your favorite fruit?",
    ("Banana", "Strawberries", "Peaches"),
)

st.write("You selected:", option)



conn = st.connection("snowflake")
Session = conn.session()
my_dataframe = Session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('choose upto four ingredients:'
                                 , my_dataframe
                                  ,max_selections=5
                                )
if ingredients_list:
    
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen + ''
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://www.fruityvice.com/api/fruit/all"+ search_on)
        sf_df = st.dataframe(data=fruityvice_response.json(),use_container_width = True)

        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')"""


    #st.write(my_insert_stmt)
    time_to_insert = st.button('submit order')
    if time_to_insert:
        Session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
