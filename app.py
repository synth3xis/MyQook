import streamlit as st
import requests
import toml
import os

# Get absolute path to the directory where this script resides
current_dir = os.path.dirname(os.path.abspath(__file__))
secrets_path = os.path.join(current_dir, ".streamlit/secrets.toml")

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
            if not any(allergen.lower() in [a.lower() for a in recipe.get('healthLabels', [])] for allergen in allergens):
                include_recipe = False
        if diet:
            if not any(diet_type.lower() in [d.lower() for d in recipe.get('dietLabels', [])] for diet_type in diet):
                include_recipe = False
        if include_recipe:
            filtered_recipes.append(recipe)
    return filtered_recipes

# Function to map user-friendly options to Edamam API parameters
def map_to_api_params(selected_options, mapping_dict):
    return [mapping_dict[option] for option in selected_options if option in mapping_dict]

# Function to get recipes from Edamam API
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def get_recipes(ingredients, allergens=[], diet=[], count=10):
    allergen_query = "".join([f"&health={a}" for a in allergens])
    diet_query = "".join([f"&diet={d}" for d in diet])
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

st.divider()

# Sidebar for instructions
st.sidebar.title("How to use")
with st.sidebar.expander("How to Use"):
    st.markdown("""
    1. **Add a new list**: To add a new list, simply type in the name of your list in the -new list- tab, click on generate and remember to select your list in the dropdown-menu on the sidebar

    2. **Add Ingredients**: After you selected your list, type in an ingredient, press enter and click on -add ingredient-, you can add multiple ingredients this way

    3. **Generate Recipes**: After adding your ingredients, click on the -Generate Recipes- button to generate recipes based on your ingredients on the selected list.

    4. **Filter Recipes**: Use the filters on the left sidebar to filter recipes based on allergens and diet types.

    5. **View Recipes**: Expand the recipe card to view ingredients, preparation steps, and a link to the full recipe.

    6. **Delete Lists**: To remove a list, click on the "Delete" button next to the list name in the "My Lists" section.
    """)

st.sidebar.divider()

# Initialize session state for lists
if 'lists' not in st.session_state:
    st.session_state.lists = {}

# Mapping dictionaries for allergens and diet filters
allergen_mapping = {
    "Gluten-Free": "gluten-free",
    "Egg-Free": "egg-free",
    "Soy-Free": "soy-free",
    "Dairy-Free": "dairy-free",
    "Seafood-Free": "seafood-free",
    "Sesame-Free": "sesame-free",
    "Tree-Nut-Free": "tree-nut-free",
    "Wheat-Free": "wheat-free",
}

diet_mapping = {
    "Balanced": "balanced",
    "High-Protein": "high-protein",
    "Low-Carb": "low-carb",
    "Low-Fat": "low-fat",
    "Paleo": "paleo",
    "Vegan": "vegan",
    "Vegetarian": "vegetarian"
}

# Sidebar for allergen filters
st.sidebar.title("Allergen Filters")
selected_allergens = st.sidebar.multiselect(
    "Select allergens:",
    list(allergen_mapping.keys())
)

# Sidebar for diet filters
st.sidebar.title("Diet Filters")
selected_diets = st.sidebar.multiselect(
    "Select diet types:",
    list(diet_mapping.keys())
)

# Button to add a new list
new_list_name = st.text_input("Enter name for new list:")
if st.button("Add New List"):
    if new_list_name:
        st.session_state.lists[new_list_name] = []
        
st.sidebar.divider()
st.sidebar.title("Select a list")

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
        mapped_allergens = map_to_api_params(selected_allergens, allergen_mapping)
        mapped_diets = map_to_api_params(selected_diets, diet_mapping)
        recipes = get_recipes(ingredients_list, mapped_allergens, mapped_diets)
        if recipes:
            st.markdown("### Recipes")  # Add header for recipes
            for i, recipe in enumerate(recipes):
                with st.expander(f"Recipe {i+1}: {recipe['label']}"):
                    st.image(recipe['image'])

                    # Display additional information
                    st.subheader("Additional Information:")
                    st.write(f"Calories: {recipe['calories']:.2f} kcal")
                    st.write(f"Yield: {recipe['yield']}")
                    st.write(f"Cuisine Type: {', '.join(recipe.get('cuisineType', []))}")
                    st.write(f"Meal Type: {', '.join(recipe.get('mealType', []))}")
                    st.write(f"Dish Type: {', '.join(recipe.get('dishType', []))}")

                    # Display allergens
                    st.subheader("Allergens:")
                    allergens = recipe.get('healthLabels', [])
                    if allergens:
                        st.write(", ".join(allergens))
                    else:
                        st.write("No allergens mentioned")

                    # Display preparation steps
                    st.subheader("Preparation Steps:")
                    for i, step in enumerate(recipe.get('preparation', [])):
                        st.write(f"{i + 1}. {step}")

                    # Display full recipe link
                    st.subheader("Full Recipe:")
                    st.write(recipe['url'])
                    st.write("---")
        else:
            st.warning("No recipes found with the selected ingredients and filters.")
    else:
        st.warning("Please select or add a list of ingredients.")





