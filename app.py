import streamlit as st
import pandas as pd
from datetime import date
from github_contents import GithubContents

# Set constants
DATA_FILE = "MyContactsTable.csv"
DATA_COLUMNS = ["Name", "Strasse", "PLZ", "Ort", "Geburtsdatum"]

# Set page configuration
st.set_page_config(page_title="My Contacts", page_icon="🎂", layout="wide",  
                   initial_sidebar_state="expanded")

def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])

def init_dataframe():
    """Initialize or load the dataframe."""
    if 'df' in st.session_state:
        pass
    elif st.session_state.github.file_exists(DATA_FILE):
        st.session_state.df = st.session_state.github.read_df(DATA_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=DATA_COLUMNS)

def main():
   
    st.title("Add new list")

    # Initialisiere eine leere Liste
    items = []

    # Texteingabefeld für Benutzer, um Elemente hinzuzufügen
    new_item = st.text_input("Neues Element hinzufügen:")
    
    # Button zum Hinzufügen des Elements zur Liste
    if st.button(""):
        if new_item != "":
            items.append(new_item)
            st.success(f"'{new_item}' has been successfully added!")
        else:
            st.warning("something went wrong qwq.")

    # Zeige die Liste der Elemente an
    if len(items) > 0:
        st.write("Aktuelle Liste:")
        for idx, item in enumerate(items, start=1):
            st.write(f"{idx}. {item}")
    else:
        st.write("list is empty")

    
if __name__ == "__main__":
    main()