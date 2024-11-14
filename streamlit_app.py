# Import necessary packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input field for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruit options with SEARCH_ON column from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()
fruit_df = pd.DataFrame(my_dataframe)  # Convert to DataFrame for easy manipulation
fruit_options = fruit_df['FRUIT_NAME'].tolist()  # Extract fruit names for selection

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

        # Retrieve the corresponding SEARCH_ON value
        search_on = fruit_df.loc[fruit_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display each fruit's nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Use SEARCH_ON value for the API request to my.smoothiefroot.com
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if smoothiefroot_response.status_code == 200:
                smoothiefroot_data = smoothiefroot_response.json()
                
                # Extract general information (non-nutrition details)
                general_info = {
                    'family': smoothiefroot_data.get('family', 'Unknown'),
                    'genus': smoothiefroot_data.get('genus', 'Unknown'),
                    'id': smoothiefroot_data.get('id', 'Unknown'),
                    'name': smoothiefroot_data.get('name', 'Unknown'),
                    'order': smoothiefroot_data.get('order', 'Unknown')
                }
                
                # Define the specific order of nutrients to display
                nutrition_order = ["carbs", "fat", "protein", "sugar"]
                
                # Prepare the nutrition data for display, ensuring the specified order
                nutrition_data = []
                if 'nutrition' in smoothiefroot_data and isinstance(smoothiefroot_data['nutrition'], dict):
                    for nutrient in nutrition_order:
                        # Check if nutrient exists in the data, else set it to None
                        row_data = {
                            'family': general_info['family'],
                            'genus': general_info['genus'],
                            'id': general_info['id'],
                            'name': general_info['name'],
                            'nutrition': smoothiefroot_data['nutrition'].get(nutrient, None),
                            'order': general_info['order']
                        }
                        nutrition_data.append(row_data)
                
                # Convert list of dictionaries to DataFrame
                nutrition_df = pd.DataFrame(nutrition_data)
                
                # Ensure the DataFrame has the correct columns in the specified order
                nutrition_df = nutrition_df[['family', 'genus', 'id', 'name', 'nutrition', 'order']]
                
                # Set the index to nutrition type for row labels
                nutrition_df.index = nutrition_order
                
                # Display the formatted DataFrame
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.error(f"Sorry, data for {fruit_chosen} is not available in the Smoothiefroot database.")
        except Exception as e:
            st.error(f"Failed to retrieve data for {fruit_chosen}: {e}")
else:
    st.warning("Please select at least one ingredient.")

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





