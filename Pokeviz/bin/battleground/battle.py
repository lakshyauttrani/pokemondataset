import urllib.request
import base64
# import gender_guesser.detector as gender
#import openpyxl
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


# Add a dark mode slider button


df = pd.read_csv("Pokeviz/bin/data/pokedex_input.csv")

df.drop(columns=['Unnamed: 0','german_name','japanese_name'],inplace=True)
df['catch_label'] = pd.qcut(df['catch_rate'], 4, labels=['You Got Lucky', 'Super Hard', 'Caught It', 'Meh'], retbins=False, precision=3, duplicates='raise')

def return_letter_by_letter(text, delay=0.07):
    for letter in text:
        yield letter
        time.sleep(delay)

def return_letter_by_letter(text, delay=0.05):
    words = text.split()
    for word in words:
        for letter in word:
            yield letter
            time.sleep(delay)
        yield ' '  # Add a space between words
        time.sleep(delay)  # Add extra delay between words


# Selection of pokemons and comments

def catch_rate_phrase(name):
    filtered_df = df.copy()
    filtered_df['name'] = filtered_df['name'].str.lower()
    filtered_df = filtered_df[filtered_df['name'] == name.lower()]

    if not filtered_df.empty:
        status = filtered_df.iloc[0]['status']
        catch_label = filtered_df.iloc[0]['catch_label']

        if pd.notna(status) and pd.notna(catch_label):
            matching_rows = filtered_df[
                (filtered_df['status'] == status) & (filtered_df['catch_label'] == catch_label)
            ]
            if not matching_rows.empty:
                if catch_label == 'You Got Lucky':
                    return "Are you sure you really caught it? It's super tough to catch one!"
                elif catch_label == 'Super Hard':
                    return f'Wow, this one was {catch_label} to catch, Kudos!'
                elif catch_label == 'Caught It':
                    return f'Did you just throw a Pokeball, and a voice said {catch_label}?'
                elif catch_label == 'Meh':
                    return f'{catch_label}, everyone has one of these!'
                else:
                    return 'Now this is like catching God, but we will be game and play along.'
            else:
                return 'No matching catch_label found for the given name and status.'
        else:
            return 'No matching status or catch_label found for the given name.'
    else:
        return 'No matching name found in the DataFrame.'

def calculate_effectiveness(attacker_type_1, attacker_type_2, defender_name,attacker_base_hit):
    defender_rows = df[df['name'] == defender_name]
    against_column = 'against_' + attacker_type_1.lower()
    val_def = defender_rows[against_column].values[0]
    impact  = attacker_base_hit*val_def

    if (attacker_type_2):
        against_column = 'against_' + attacker_type_2.lower()
        if against_column == 'against_fighting':
            return impact
        else:
            val_def = defender_rows[against_column].values[0]
            impact = impact+ (attacker_base_hit*val_def)

    return impact

def swapList(sl):
    sl[0], sl[1] = sl[1], sl[0]
    return sl

def get_non_null_abilities(row):
    abilities_df = ['ability_1', 'ability_2', 'ability_hidden']
    non_null_abilities = [ability for ability in abilities_df if pd.notna(row[ability])]
    return non_null_abilities

def simulate_turn_based_battle(attacker_name, defender_name):
    attacker_rows = df[df['name'] == attacker_name]
    defender_rows = df[df['name'] == defender_name]

    if attacker_rows.empty or defender_rows.empty:
        return "Invalid Pokemon names. Make sure the names are correct.", []

    attacker_row = attacker_rows.iloc[0].copy()
    defender_row = defender_rows.iloc[0].copy()

    battle_log = []
    turn_order = [attacker_name, defender_name]
    attacker_row_copy = attacker_row.copy()
    defender_row_copy = defender_row.copy()
    for round_count in range(6):
        if attacker_row['total_points'] <= 0 or defender_row['total_points'] <= 0:
            break

        attacker_name = turn_order[0]
        defender_name = turn_order[1]

        non_null_abilities = get_non_null_abilities(attacker_row)
        if non_null_abilities:
            random_ability = random.choice(non_null_abilities)
        else:
            random_ability = None

        if attacker_row['type_number'] == 1:
            damage_taken_defender = calculate_effectiveness(attacker_row['type_1'], None, defender_name, attacker_row['attack'])
            if defender_row['total_points'] - damage_taken_defender < 0:
                defender_row['total_points'] = 0
            else:
                defender_row['total_points'] = defender_row['total_points'] - damage_taken_defender
        else:
            damage_taken_defender = calculate_effectiveness(attacker_row['type_1'], attacker_row['type_2'], defender_name, attacker_row['attack'])
            defender_row['total_points'] = defender_row['total_points'] - damage_taken_defender
            if defender_row['total_points'] - damage_taken_defender < 0:
                defender_row['total_points'] = 0
            else:
                defender_row['total_points'] = defender_row['total_points'] - damage_taken_defender

        battle_log.append(f"{attacker_name} uses {attacker_row[random_ability]} on {defender_name}. "
                          f"{defender_name}'s total points reduced by {damage_taken_defender:.2f} to "
                          f"{defender_row['total_points']:.1f}.")

        turn_order = swapList(turn_order)
        attacker_row_copy = attacker_row.copy()
        attacker_row = defender_row.copy()
        defender_row = attacker_row_copy.copy()

    if attacker_row['total_points'] > defender_row['total_points']:
        winner = defender_name
    elif defender_row['total_points'] > attacker_row['total_points']:
        winner = attacker_name
    else:
        winner = "It's a tie!"

    return battle_log, winner


st.set_page_config(page_title="PokeViz App", layout="wide")

#Header
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)

with row0_1:
    st.header("Welcome to Pokéviz BattleGround")

    st.markdown(
        "⚡ It's time for showdown! ⚡"
    )

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# set_background('background6.jpg')


def convert_to_black_and_white(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        bw_image = image.convert("L")  # Convert to grayscale
        return bw_image




line1_spacer1, line1_1, line1_spacer2 = st.columns((0.1, 3.2, 0.1))


tab1, tab2 = st.tabs(["Battle Ground", ""])
with tab1:
    bg_space1, bg_1_1, bg_space2, bg_1_2, bg_space3, bg_1_3 = st.columns(
        (0.1, 1, 0.1, 0.4, 0.1, 1)
    )

    contender1 = ''
    contender2 = ''
    selected_pokemon_data = {
    "Contender 1": {"name": None, "image_url": None},
    "Contender 2": {"name": None, "image_url": None}
    }

    with bg_1_1:
        # Create two columns for filters
        bgr_column1, bgr_column2, bgr_column3, bgr_column4 = st.columns(4)

        # Filter by Generation
        selected_generation = bgr_column1.selectbox("Generation", df["generation"].unique(),
                                                    key="generation")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["generation"] == selected_generation]
        selected_status = bgr_column2.selectbox("Select Status", filtered_df_by_generation["status"].unique(),
                                                key="status")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["status"] == selected_status]
        selected_type = bgr_column3.selectbox("Select a Type", filtered_df_by_generation["type_1"].unique(),
                                              key="type")

        # Filter by Name based on selected Generation and Type
        filtered_df_by_type = filtered_df_by_generation[filtered_df_by_generation["type_1"] == selected_type]
        selected_pokemon = bgr_column4.selectbox("Select a Pokemon", filtered_df_by_type["name"], key="pokemon")
        contender1 = selected_pokemon

        # Fetch the Pokemon data from the API
        pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{selected_pokemon.lower()}"
        response = requests.get(pokeapi_url)

        if response.status_code == 200:
            pokemon_data = response.json()
            # Use PokeSprites API for higher resolution images
            pokemon_image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_data['id']}.png"
            pokemon_name = pokemon_data["name"]
            selected_pokemon_data["Contender 1"]["name"] = selected_pokemon.lower()
            selected_pokemon_data["Contender 1"]["image_url"] = pokemon_image_url

            # Display the Pokemon image and stats
            # image_column, stats_column, image_column = st.columns((1, 2))

            # Check if the higher resolution image is available
            response_image_high_res = requests.get(pokemon_image_url)
            if response_image_high_res.status_code == 200:
                # with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                image = Image.open(BytesIO(response_image_high_res.content))
                st.image(image, use_column_width=True)
            else:
                # If higher resolution image is not available, use the other API with lower resolution
                pokemon_image_url_low_res = pokemon_data["sprites"]["front_default"]
                # with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                response_image_low_res = requests.get(pokemon_image_url_low_res)
                image_low_res = Image.open(BytesIO(response_image_low_res.content))
                st.image(image_low_res, use_column_width=True, caption="Sorry for the image quality")

            stats = {
                "Name": pokemon_name,
                "Generation": df.loc[df["name"] == selected_pokemon, "generation"].values[0],
                "Type": df.loc[df["name"] == selected_pokemon, "type_1"].values[0],
                "Attack": pokemon_data["stats"][4]["base_stat"],
                "Defense": pokemon_data["stats"][3]["base_stat"],
                "Total Points": sum(stat["base_stat"] for stat in pokemon_data["stats"]),
                "Catch Rate": df.loc[df["name"] == selected_pokemon, "catch_rate"].values[0],
            }
            # Convert the stats dictionary to a DataFrame with two columns
            stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=["Value"])
            # Adjust the table size to make it slimmer and remove the header row
            st.table(stats_df.style.set_table_styles([
                dict(selector="thead", props=[("display", "none")]),
                dict(selector="th", props=[("max-width", "30px")]),
                dict(selector="td", props=[("padding", "2px")])  # Increase row spacing

            ]))
            st.markdown(catch_rate_phrase(pokemon_name))

        else:
            st.warning("Pokemon not found in the API.")
            st.text("Just Enjoy some stats of this pokemon.")
            stats = {
                "Name": pokemon_name,
                "Generation": df.loc[df["name"] == selected_pokemon, "generation"].values[0],
                "Type": df.loc[df["name"] == selected_pokemon, "type_1"].values[0],
                "Attack": pokemon_data["stats"][4]["base_stat"],
                "Defense": pokemon_data["stats"][3]["base_stat"],
                "Total Points": sum(stat["base_stat"] for stat in pokemon_data["stats"]),
                "Catch Rate": df.loc[df["name"] == selected_pokemon, "catch_rate"].values[0],
            }
            # Convert the stats dictionary to a DataFrame with two columns
            stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=["Value"])
            # Adjust the table size to make it slimmer and remove the header row
            st.table(stats_df.style.set_table_styles([
                dict(selector="thead", props=[("display", "none")]),
                dict(selector="th", props=[("max-width", "30px")]),
                dict(selector="td", props=[("padding", "2px")])  # Increase row spacing

            ]))
            st.markdown(catch_rate_phrase(pokemon_name))

    with bg_1_3:
        # Create two columns for filters
        bgr_column1, bgr_column2, bgr_column3, bgr_column4 = st.columns(4)

        # Filter by Generation
        selected_generation = bgr_column1.selectbox("Generation", df["generation"].unique(),
                                                    key="generation_select")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["generation"] == selected_generation]
        selected_status = bgr_column2.selectbox("Select Status", filtered_df_by_generation["status"].unique(),
                                                key="status_select")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["status"] == selected_status]
        selected_type = bgr_column3.selectbox("Select a Type", filtered_df_by_generation["type_1"].unique(),
                                              key="type_select")

        # Filter by Name based on selected Generation and Type
        filtered_df_by_type = filtered_df_by_generation[filtered_df_by_generation["type_1"] == selected_type]
        selected_pokemon = bgr_column4.selectbox("Select a Pokemon", filtered_df_by_type["name"], key="pokemon_select")
        contender2 = selected_pokemon

        # Fetch the Pokemon data from the API
        pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{selected_pokemon.lower()}"
        response = requests.get(pokeapi_url)
        if response.status_code == 200:
            pokemon_data = response.json()
            # Use PokeSprites API for higher resolution images
            pokemon_image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_data['id']}.png"
            pokemon_name = pokemon_data["name"]

            selected_pokemon_data["Contender 2"]["name"] = selected_pokemon.lower()
            selected_pokemon_data["Contender 2"]["image_url"] = pokemon_image_url
            # Display the Pokemon image and stats
            # image_column, stats_column, image_column = st.columns((1, 2))

            # Check if the higher resolution image is available
            response_image_high_res = requests.get(pokemon_image_url)
            if response_image_high_res.status_code == 200:
                # with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                image = Image.open(BytesIO(response_image_high_res.content))
                st.image(image, use_column_width=True)
            else:
                # If higher resolution image is not available, use the other API with lower resolution
                pokemon_image_url_low_res = pokemon_data["sprites"]["front_default"]
                # with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                response_image_low_res = requests.get(pokemon_image_url_low_res)
                image_low_res = Image.open(BytesIO(response_image_low_res.content))
                st.image(image_low_res, use_column_width=True, caption="Sorry for the image quality")

            stats = {
                "Name": pokemon_name,
                "Generation": df.loc[df["name"] == selected_pokemon, "generation"].values[0],
                "Type": df.loc[df["name"] == selected_pokemon, "type_1"].values[0],
                "Attack": pokemon_data["stats"][4]["base_stat"],
                "Defense": pokemon_data["stats"][3]["base_stat"],
                "Total Points": sum(stat["base_stat"] for stat in pokemon_data["stats"]),
                "Catch Rate": df.loc[df["name"] == selected_pokemon, "catch_rate"].values[0],
            }
            # Convert the stats dictionary to a DataFrame with two columns
            stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=["Value"])
            # Adjust the table size to make it slimmer and remove the header row
            st.table(stats_df.style.set_table_styles([
                dict(selector="thead", props=[("display", "none")]),
                dict(selector="th", props=[("max-width", "30px")]),
                dict(selector="td", props=[("padding", "2px")])  # Increase row spacing

            ]))
            st.markdown(catch_rate_phrase(pokemon_name))

        else:
            st.warning("Pokemon not found in the API.")
            st.text("Just Enjoy some stats of this pokemon.")
            stats = {
                "Name": pokemon_name,
                "Generation": df.loc[df["name"] == selected_pokemon, "generation"].values[0],
                "Type": df.loc[df["name"] == selected_pokemon, "type_1"].values[0],
                "Attack": pokemon_data["stats"][4]["base_stat"],
                "Defense": pokemon_data["stats"][3]["base_stat"],
                "Total Points": sum(stat["base_stat"] for stat in pokemon_data["stats"]),
                "Catch Rate": df.loc[df["name"] == selected_pokemon, "catch_rate"].values[0],
            }
            # Convert the stats dictionary to a DataFrame with two columns
            stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=["Value"])
            # Adjust the table size to make it slimmer and remove the header row
            st.table(stats_df.style.set_table_styles([
                dict(selector="thead", props=[("display", "none")]),
                dict(selector="th", props=[("max-width", "30px")]),
                dict(selector="td", props=[("padding", "2px")])  # Increase row spacing

            ]))
            st.markdown(catch_rate_phrase(pokemon_name))

    with bg_1_2:
        # Load the button image
        button_image_path = "Pokeviz/bin/images/Poke_Ball.webp"
        button_image = Image.open(button_image_path)
        # Reduce the image size to improve loading time
        button_image.thumbnail((180, 200))  # Adjust the size as needed

        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")

        # Button to open the link
        if st.image(button_image, use_column_width=True):
            link = "https://pvpoke.com/train/"
            if st.button('Start Battle'):
                # Example battle simulation
                battle_log, winner = simulate_turn_based_battle(contender1, contender2)

                for log in battle_log:
                    st.markdown(log)
                    # st.markdown("![Alt Text](https://media.giphy.com/media/dzIrXQiyqgsSbGGpZR/giphy.gif)")
                    time.sleep(1.0)
                if winner:
                    # Determine the loser based on the winner
                    loser_pokemon = contender1 if winner == contender2 else contender2
                    loser_pokemon_name = loser_pokemon.lower()
                    pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{loser_pokemon_name}"
                    response = requests.get(pokeapi_url)

                    if response.status_code == 200:
                        loser_pokemon_data = response.json()
                        loser_pokemon_image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{loser_pokemon_data['id']}.png"

                        # Store the loser Pokemon data
                        selected_pokemon_data[loser_pokemon_name] = {
                            "data": loser_pokemon_data,
                            "image_url": loser_pokemon_image_url
                        }

                        # Display the loser's black and white image
                        loser_bw_image = convert_to_black_and_white(loser_pokemon_image_url)
                        st.markdown(f"**Loser: {loser_pokemon}**")
                        st.image(loser_bw_image, use_column_width=True)
                else:
                    st.markdown("\nIt's a tie!")
