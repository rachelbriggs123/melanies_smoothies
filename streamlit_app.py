# Import necessary packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input field for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")
    session = None

# Fetch available fruit options from the database, if connected
if session:
    try:
        my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name')).collect()
        fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extract fruit names for selection
    except Exception as e:
        st.error(f"Failed to fetch fruit options: {e}")
        fruit_options = []
else:
    fruit_options = []

# Multi-select box for ingredients with a maximum of 5 selections
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_options,
    max_selections=5
)

# Construct the ingredients string from the selected list
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Example API request to get nutrition information for the first selected ingredient
    first_ingredient = ingredients_list[0]
    try:
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{first_ingredient.lower()}")
        smoothiefroot_data = smoothiefroot_response.json()

        # Display the nutrition information in a DataFrame
        sf_df = st.dataframe(data=smoothiefroot_data, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to retrieve data from Smoothiefroot API: {e}")

# Display the SQL statement for debugging purposes (optional)
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
"""

# Button to submit the order
time_to_insert = st.button('Submit Order')

# Insert the order into Snowflake if the button is clicked
if time_to_insert:
    if session and name_on_order and ingredients_list:  # Check if session, name, and ingredients are provided
        try:
            # Using parameterized query for safe SQL execution
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"Failed to insert order: {e}")
    else:
        st.warning("Please enter a name and select at least one ingredient for your smoothie.")




