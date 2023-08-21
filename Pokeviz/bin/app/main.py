import streamlit as st
from tabs import tab1, tab2, tab3, tab4
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import xmltodict
from pandas import json_normalize
# from streamlit_extras.add_vertical_space import add_vertical_space
# from streamlit_lottie import st_lottie
import requests
from PIL import Image
from io import BytesIO
import time
import random
import os
import matplotlib.pyplot as plt

input_file = "Pokeviz/bin/data/pokedex_input.csv"
revenue_file = "Pokeviz/bin/data/revenue.csv"

#Read and transform data
df = pd.read_csv(input_file)
df.drop(columns=['Unnamed: 0','german_name','japanese_name'],inplace=True)
df['catch_label'] = pd.qcut(df['catch_rate'], 4, labels=['You Got Lucky', 'Super Hard', 'Caught It', 'Meh'], retbins=False, precision=3, duplicates='raise')

df2 = pd.read_csv(revenue_file, sep=';')

# Set page config
st.set_page_config(page_title="PokeViz App", layout="wide")






row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.1, 1, 0.1)
)


with row0_1:
    st.header("Welcome to Pokéviz : Explore the Enigmatic World of Pokémon")

    st.markdown(
        "Dive into the captivating realm of Pokémon with \"Pokeviz,\" a dynamic visualization dashboard that opens the doors to a treasure trove of information about these remarkable creatures. Our dataset, meticulously compiled, dissected, and organized, introduces you to the profiles of 1028 Pokémon, each a unique entity in the vast tapestry of the Pokémon universe. From the classic charm of the original generation to the mystique of sub-legendaries and mythicals, Pokeviz takes you on an illuminating journey through the generations in pursuit of knowledge."

    )
    st.markdown( "Uncover the intricacies of each Pokémon's attributes, from their physical characteristics such as height and weight, to their combat prowess encompassing attack, defense, speed, and beyond. The dashboard doesn't stop at the surface-level statistics; it delves deeper into the realm of abilities, growth rates, breeding traits, and even the enigmatic intricacies of type defenses. Whether you're a seasoned Pokémon Trainer or a curious enthusiast, Pokeviz promises to be your compass in navigating the diverse traits and traits of these incredible creatures. Embark on this visual expedition as we unravel the many facets of Pokémon through insightful graphs, interactive charts, and a visual storytelling experience like no other. Welcome to Pokeviz, where data-driven exploration meets the enchanting world of Pokémon!"

    )

    # Color palatte
    selected_option = st.selectbox(
        "**Set the Mood: Pick a Theme to Elevate Your Experience**",
        ["Fire - 🔥", "Water - 🌊", "Grass - 🌿", "Rock - 🪨"],
        help="Choose a theme to customize your experience"
    )


    if selected_option == "Fire - 🔥":
        color1 = "#FFDB01"
        color2 = "#F5B608"
        color3 = "#EB900F"
        color4 = "#D8451D"
        color5 = "#CE2024"

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color1}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🔥 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Water - 🌊":
        color1 = "#44B9BD"
        color2 = "#99D9DF"
        color3 = "#68B7D0"
        color4 = "#3D92C2"
        color5 = "#2E5D96"

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color2}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🌊 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Grass - 🌿":
        color1 = "#D7E356"
        color2 = "#A5C940"
        color3 = "#82C23A"
        color4 = "#4F9900"
        color5 = "#1D4600"

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color1}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🌿 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Rock - 🪨":
        color1 = "#FFC011"
        color2 = "#FFF572"
        color3 = "#EEECDF"
        color4 = "#C8B7A7"
        color5 = "#96665C"

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color4}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🪨 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    color_theme = [color1, color2, color3, color4, color5]



with row0_2:
    # Load and resize the image
    image_path = "bin/images/Battle_groud_bkp.webp"
    st.markdown(
        "<div style='text-align: center;'><a href='https://pokemonbattle.streamlit.app/'><img src='https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/1733aa4c-c30e-4ecc-b8d6-80ef83ca0b8e/d3bqzxd-a81ee1f1-6c5f-4081-8640-b4cba8caf363.png/v1/fill/w_797,h_458/pokemon_battle_frontier_logo_by_pklucario_d3bqzxd-fullview.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NDU4IiwicGF0aCI6IlwvZlwvMTczM2FhNGMtYzMwZS00ZWNjLWI4ZDYtODBlZjgzY2EwYjhlXC9kM2JxenhkLWE4MWVlMWYxLTZjNWYtNDA4MS04NjQwLWI0Y2JhOGNhZjM2My5wbmciLCJ3aWR0aCI6Ijw9Nzk3In1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.v3pX-GaQcPxrvpqOLDz5T1SmmVHVdCUqaqDspmOIf8w' alt='Battle' style='width: 100%; max-width: 700px;'></a></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color: rgba(0, 0, 0, 0.5); text-align: center;'>Click to explore the battle ground</p>",
        unsafe_allow_html=True
    )



line1_spacer1, line1_1, line1_spacer2 = st.columns((0.1, 3.2, 0.1))

with line1_1:
    st.header("Peek into PokeVerse: Crafting Pokémon Chronicles from Data")



st.markdown(
    """
    <style>
        .stTabs > div > div > div:nth-child(1) {
            margin-left: 90px; /* Adjust the value as needed */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Create tabs
Main, EYP, EAD1, EAD2 = st.tabs(["PokeVerse", "Explore your Pokemon", "NarrativeNest", "Exploradex"])

# Display content for each tab
with Main:
    tab1.display_tab(df, df2, color_theme)
with EYP:
    tab2.display_tab(df, df2, color_theme)
with EAD1:
    tab3.display_tab(df, df2, color_theme)
with EAD2:
    tab4.display_tab(df, df2, color_theme)
