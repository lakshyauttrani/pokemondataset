import streamlit as st
from tabs import tab1, tab2, tab3, tab4, tab5, battle
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from pandas import json_normalize
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
import requests
from PIL import Image
from io import BytesIO
import time
import random
import os
import matplotlib.pyplot as plt
import base64



def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


input_file = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/data/pokedex_input.csv"
revenue_file = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/data/revenue.csv"

#Read and transform data
df = pd.read_csv(input_file)
df.drop(columns=['Unnamed: 0','german_name','japanese_name'],inplace=True)
df['catch_label'] = pd.qcut(df['catch_rate'], 4, labels=['You Got Lucky', 'Super Hard', 'Caught It', 'Meh'], retbins=False, precision=3, duplicates='raise')

df2 = pd.read_csv(revenue_file, sep=';')

# Set page config
st.set_page_config(page_title="PokeViz App", layout="wide")





row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.05, 3.5, 0.1, 1, 0.1)
)


with row0_1:
    st.markdown("<div style='text-align: left; font-size: 3vw; font-weight: bold;'>Welcome to Pokéviz:</div>",
                unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: left; font-size: 0.75vw; font-weight: bold; font-family: sans-serif; color: grey;'>Explore the Enigmatic World of Pokémon</div>",
        unsafe_allow_html=True
    )

    st.header("")

    st.markdown(
        "Immerse yourself in the world of Pokémon with Pokeviz, a dynamic dashboard unveiling a treasure trove of info about these unique creatures. Explore profiles of 1028 Pokémon, from classics to sub-legendaries, on an enlightening journey through generations.Delve into Pokémon intricacies like physical traits and combat prowess. Pokeviz goes beyond stats, diving into abilities, growth rates, and type defenses. Whether Trainer or enthusiast, it guides you through diverse traits. Uncover Pokémon facets with graphs, charts, and visual storytelling at Pokeviz.",
        unsafe_allow_html=True
    )

    st.markdown(
        "Step into a world where data-driven exploration merges with the enchanting realm of Pokémon. Welcome to Pokeviz, your guide to the captivating universe of these incredible creatures.",
        unsafe_allow_html=True
    )









with row0_2:


    image_path = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/images/pokemon_logo.png"
    image = Image.open(image_path)
    image_url = "https://pokemonbattle.streamlit.app/"

    # Use HTML to apply styling to the image
    st.markdown(
        f'<div style="display: flex; justify-content: center;"><a href="{image_url}"><img src="data:image/png;base64,{image_to_base64(image)}" alt="pokemon" style="max-width: 100%;"></a></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color: rgba(0, 0, 0, 0.5); font-size: 25px; text-align: center;'>Click to explore something fun</p>",
        unsafe_allow_html=True
    )



    selected_option = st.selectbox(
        "",
        ["Select a theme", "Fire - 🔥", "Water - 🌊", "Grass - 🌿", "Rock - 🪨"],
        help="Choose a theme to customize your experience"
    )

    if selected_option in ["Select a theme"]:
        color1 = "#FF6F00" 
        color2 = "#B80000"   # Intense Red
        color3 = "#FFD133"  # Light Yellow-Orange
        color4 = "#FF5733"  # Bold Yellow-Orange
        color5 = "#9A6324"  # Deep Brown
        st.markdown(
            f"<h3 style='text-align: center; background-color: {color1}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🔥 Current theme - Fire - 🔥 </h3>",
            unsafe_allow_html=True
        )
    elif selected_option == "Fire - 🔥":
        color1 = "#FF6F00" 
        color2 = "#B80000"   # Intense Red
        color3 = "#FFD133"  # Light Yellow-Orange
        color4 = "#FF5733"  # Bold Yellow-Orange
        color5 = "#9A6324"  # Deep Brown

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color1}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🔥 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Water - 🌊":
        color1 = "#00b4d8"  # Teal Blue
        color2 = "#008080"  # Teal (Toned Down) 
        color3 =  "#006994"  # Deep Blue
        color4 = "#6AC9E2"  # Light Blue
        color5 = "#3CB371"  # Sea Green 


        st.markdown(
            f"<h3 style='text-align: center; background-color: {color2}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🌊 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Grass - 🌿":
        color1 =  "#8BC34A"   # Bright Green
        color2 =  "#9CCC65"  # Brown
        color3 = "#795548"   # Deep Green 
        color4 = "#8D6E63"  # Deep Brown
        color5 =   "#558B2F"# Light Green

        st.markdown(
            f"<h3 style='text-align: center; background-color: {color1}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🌿 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    elif selected_option == "Rock - 🪨":
        color1 = "#8B4513"  # Saddle Brown
        color2 = "#A0522D"  # Deep Brown
        color3 = "#6B4423"  # Rust Brown
        color4 = "#AAAAAA"  # Light Gray
        color5 = "#333333"  # Very Dark Gray



        st.markdown(
            f"<h3 style='text-align: center; background-color: {color4}; padding: 10px; border-radius: 5px; color: #333;'>"
            f"🪨 Current theme - {selected_option} </h3>",
            unsafe_allow_html=True
        )

    color_theme = [color1, color2, color3, color4, color5]



line1_spacer1, line1_1, line1_spacer2 = st.columns((0.02, 3.2, 0.1))

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
Main, EYP, EAD1, EAD2, BATTLE, AUS = st.tabs(["PokeVerse", "Explore your Pokemon", "NarrativeNest", "Exploradex", "Battle Ground", "About Us"])

# Display content for each tab
with Main:
    tab1.display_tab(df, df2, color_theme)
with EYP:
    tab2.display_tab(df, df2, color_theme)
with EAD1:
    tab3.display_tab(df, df2, color_theme)
with EAD2:
    tab4.display_tab(df, df2, color_theme)
with BATTLE:
    battle.display_tab()
with AUS:
    tab5.display_tab(df, df2, color_theme)

