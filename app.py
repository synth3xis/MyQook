import streamlit as st
import requests
import toml
import os

# Get absolute path to the directory where this script resides

current_dir = os.path.dirname(os.path.abspath(__file__))
secrets_path = os.path.join(current_dir, "secrets.toml")


# Load secrets from secrets.toml
secrets = toml.load(secrets_path)
edamam_credentials = secrets.get("edamam", {})
app_id = edamam_credentials.get("app_id", "")
app_key = edamam_credentials.get("app_key", "")

# Function to filter recipes based on allergens and diet types
def filter_recipes(recipes, allergens=[], diet=[]):
    filtered_recipes = []
    for recipe in recipes:
        include_recipe = True
        if allergens:
            for allergen in allergens:
                if allergen.lower() in [a.lower() for a in recipe.get('healthLabels', [])]:
                    include_recipe = False
                    break
        if diet:
            for diet_type in diet:
                if diet_type.lower() not in [d.lower() for d in recipe.get('dietLabels', [])]:
                    include_recipe = False
                    break
        if include_recipe:
            filtered_recipes.append(recipe)
    return filtered_recipes

# Function to get recipes from Edamam API
def get_recipes(ingredients, allergens=[], diet=[], count=10):
    allergen_query = f"&health={','.join(allergens)}" if allergens else ""
    diet_query = f"&diet={','.join(diet)}" if diet else ""
    url = f"https://api.edamam.com/search?q={'+'.join(ingredients)}&app_id={app_id}&app_key={app_key}&to={count}{allergen_query}{diet_query}"
    response = requests.get(url)
    data = response.json()
    
    recipes = []
    if 'hits' in data:
        hits = data['hits']
        for hit in hits:
            recipe = hit['recipe']
            if 'ingredientLines' in recipe:
                recipes.append(recipe)
    
    # Filter recipes based on allergens and diet types
    filtered_recipes = filter_recipes(recipes, allergens, diet)
    
    return filtered_recipes

# Streamlit app layout
st.title("MyQook")

# Sidebar for instructions
with st.sidebar.expander("How to Use"):
    st.markdown("""
    
    
    1. **Add a list**: Type in the name of the list in the "Enter name for new list" text box, then click on the "Add New List" button.

    2. **Choose List**: After you created your list, choose your list in the dropdown menu.

    3. **Add Ingredients**: you can add your Ingredients in the "Add ingredients" box. Click on "Add ingredient" to add an Ingredient to the list.

    4. **Generate Recipes**: Click on "Generate recipe" to generate Recipes based on the ingredients on the selected List currently chosen.

    5. **Remove Lists or ingredients**: To remove a list or ingredient , click on the "Delete" button next to the list name in the "My Lists" section.

    IMPORTANT: This App is still in development, some aspects (e.g filter options) might not function properly. 

    supported language is **english only**
    """)

# Initialize session state for lists
if 'lists' not in st.session_state:
    st.session_state.lists = {}

# Sidebar for allergen filters
st.sidebar.title("Allergen Filters")
allergen_filter = st.sidebar.multiselect(
    "Select allergens:",
    [
        "Dairy-Free",
        "Egg-Free",
        "Gluten-Free",
        "Peanut-Free",
        "Seafood-Free",
        "Sesame-Free",
        "Soy-Free",
        "Sulfite-Free",
        "Tree-Nut-Free",
        "Wheat-Free",
    ],
)

# Sidebar for diet filters
st.sidebar.title("Diet Filters")
diet_filter = st.sidebar.multiselect("Select diet types:", ["Balanced", "High-Protein", "Low-Carb", "Low-Fat", "Paleo", "Vegan", "Vegetarian"])

# Button to add a new list
new_list_name = st.text_input("Enter name for new list:")
if st.button("Add New List"):
    if new_list_name:
        st.session_state.lists[new_list_name] = []

# Multiselect widget to select or add lists
selected_list_name = st.sidebar.selectbox("Select a list:", [""] + list(st.session_state.lists.keys()))
if selected_list_name:
    ingredient_input_key = f"ingredient_input_{selected_list_name}"
    ingredient_input = st.text_input("Add ingredient:", key=ingredient_input_key)
    if ingredient_input:
        if st.button("Add Ingredient"):
            if selected_list_name not in st.session_state.lists:
                st.session_state.lists[selected_list_name] = []
            st.session_state.lists[selected_list_name].append(ingredient_input)

# Display items in the selected list
if selected_list_name and selected_list_name in st.session_state.lists:
    st.write(f"# {selected_list_name}")
    for i, item in enumerate(st.session_state.lists[selected_list_name]):
        ingredient_key = f"ingredient_{selected_list_name}_{i}"
        if st.button(f"Remove {item}", key=ingredient_key):
            st.session_state.lists[selected_list_name].remove(item)
            break  # Exit loop after removing the item
    for item in st.session_state.lists[selected_list_name]:
        st.write(f"- {item}")

# Display created lists in the sidebar
st.sidebar.title("My Lists")
lists_to_delete = []
for list_name, ingredients in st.session_state.lists.items():
    expander = st.sidebar.expander(list_name)
    for ingredient in ingredients:
        expander.write(f"- {ingredient}")
    delete_list = expander.button(f"Delete {list_name}")
    if delete_list:
        lists_to_delete.append(list_name)

# Remove lists from session state
for list_name in lists_to_delete:
    del st.session_state.lists[list_name]

# Generate recipes with filter options
generate_button_clicked = st.button("Generate Recipes")
if generate_button_clicked:
    # Clear previous recipe display
    st.empty()

    if selected_list_name in st.session_state.lists:
        ingredients_list = st.session_state.lists[selected_list_name]
        recipes = get_recipes(ingredients_list, allergen_filter, diet_filter)
        if recipes:
            st.markdown("### Recipes")  # Add header for recipes
            for i, recipe in enumerate(recipes):
                with st.expander(f"Recipe {i+1}: {recipe['label']}"):
                    st.image(recipe['image'])

                    # Display additional information
                    st.subheader(" Information:")
                    st.write(f"Calories: {recipe['calories']:.2f} kcal")
                    st.write(f"Yield: {recipe['yield']}")
                    st.write(f"Cuisine Type: {', '.join(recipe.get('cuisineType', []))}")
                    st.write(f"Meal Type: {', '.join(recipe.get('mealType', []))}")
                    st.write(f"Dish Type: {', '.join(recipe.get('dishType', []))}")

                    st.subheader("Ingredients:")
                    for ingredient in recipe['ingredientLines']:
                        st.write("- " + ingredient)

                    if 'preparation' in recipe:
                        st.subheader("Preparation Steps:")
                        for i, step in enumerate(recipe['preparation']):
                            st.write(f"{i + 1}. {step}")

                    st.subheader("Full Recipe:")
                    st.write(recipe['url'])
                    st.write("---")
        else:
            st.write("No recipes found with the selected ingredients and filters.")
    else:
        st.warning("Please select or add a list of ingredients.")












