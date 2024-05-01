import streamlit as st
import requests
import random

# Function to get recipes from Edamam API
def get_recipes(ingredients, count=5):
    app_id = "5fd0dac0"
    app_key = "334eca2560aea27a4839d48cde7aeb12"
    url = f"https://api.edamam.com/search?q={'+'.join(ingredients)}&app_id={app_id}&app_key={app_key}&to={count}"

    response = requests.get(url)
    data = response.json()

    recipes = []
    if 'hits' in data:
        hits = data['hits']
        for hit in hits:
            recipes.append(hit['recipe'])
    
    return recipes

# Streamlit app layout
st.title("Recipe Generator Based on Ingredients")

# Initialize session state to store multiple lists
if 'lists' not in st.session_state:
    st.session_state.lists = {"List 1": []}

# Select or create a new list
list_name = st.selectbox("Select or create a new list:", list(st.session_state.lists.keys()))

# Add list button
if st.button("Add List"):
    new_list_name = st.text_input("Enter name for new list:")
    if new_list_name:
        st.session_state.lists[new_list_name] = []

# Input ingredients for the selected list
ingredients_input = st.text_input("Enter ingredients separated by commas (e.g., chicken, pasta, tomato):")
ingredients_list = [ingredient.strip() for ingredient in ingredients_input.split(",")]

# Add ingredients to the selected list
if st.button("Add Ingredients"):
    st.session_state.lists[list_name].extend(ingredients_list)

# Remove ingredients from the selected list
if st.button("Remove Ingredients"):
    remove_ingredient = st.text_input("Enter ingredients to remove separated by commas:")
    remove_ingredients = [ingredient.strip() for ingredient in remove_ingredient.split(",")]
    for ingredient in remove_ingredients:
        if ingredient in st.session_state.lists[list_name]:
            st.session_state.lists[list_name].remove(ingredient)

# Generate recipes for the selected list
if st.button("Generate Recipes"):
    recipes = get_recipes(st.session_state.lists[list_name])
    if recipes:
        st.subheader("Here are some recipe suggestions:")
        for recipe in recipes:
            st.subheader(recipe['label'])
            st.image(recipe['image'])

            st.subheader("Info:")
            info = f"Yield: {recipe['yield']}\n"
            if 'calories' in recipe['totalNutrients']:
                info += f"Calories per Serving: {recipe['totalNutrients']['calories']['quantity']} {recipe['totalNutrients']['calories']['unit']}\n"
            if 'totalTime' in recipe:
                info += f"Cooking Time: {recipe['totalTime']} minutes\n"
            st.write(info)

            st.subheader("Ingredients:")
            for ingredient in recipe['ingredientLines']:
                st.write("- " + ingredient)

            st.subheader("Full Recipe:")
            st.write(recipe['url'])
            st.write("---")
    else:
        st.write("No recipes found with these ingredients.")








