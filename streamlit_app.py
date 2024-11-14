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

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extract fruit names for selection
# st.stop()


# Multi-select box for ingredients with a maximum of 5 selections
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_options,
    max_selections=5
)

# Construct the ingredients string from the selected list
ingredients_string = ''  # Initialize the string to avoid NameError
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        # Display each fruit's nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/watermelon")
            if smoothiefroot_response.status_code == 200:
                smoothiefroot_data = smoothiefroot_response.json()
                # Display the nutrition information in a DataFrame
                st.dataframe(data=smoothiefroot_data, use_container_width=True)
            else:
                st.error(f"Sorry, data for {fruit_chosen} is not available in the Fruitvice database.")
        except Exception as e:
            st.error(f"Failed to retrieve data for {fruit_chosen}: {e}")

# Display the SQL statement for debugging purposes (optional)
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
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




