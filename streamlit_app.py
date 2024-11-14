# Import necessary packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input field for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).collect()
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extract fruit names for selection

# Multi-select box for ingredients with a maximum of 5 selections
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_options,
    max_selections=5
)

# Construct the ingredients string from the selected list
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)
else:
    ingredients_string = ""

# Display the SQL statement for debugging purposes (optional)
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
"""

# Button to submit the order
time_to_insert = st.button('Submit Order')

# Insert the order into Snowflake if the button is clicked
if time_to_insert:
    if name_on_order and ingredients_list:  # Check if both fields are provided
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
    else:
        st.warning("Please enter a name and select at least one ingredient for your smoothie.")

# New section to display SmoothieRoot nutrition information
import requests
smoothieroot_response = requests.get("https://my.smoothieroot.com/api/fruit/watermelon")
# st.text(smoothieroot_response.json())
sf_df = st.dataframe(data=smoothieroot_response.json(), use_container_width=True)

