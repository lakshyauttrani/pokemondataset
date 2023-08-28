import base64
from io import BytesIO
import sys
import pandas as pd
import os
from PIL import Image
import plotly as plt
import plotly.express as px
import random
import requests
import streamlit as st
import time

# Reading the data

df = pd.read_csv("Pokeviz/bin/data/pokedex_input.csv")
df.drop(columns=['Unnamed: 0', 'german_name', 'japanese_name'], inplace=True)
df['catch_label'] = pd.qcut(df['catch_rate'], 4, labels=['You Got Lucky', 'Super Hard', 'Caught It', 'Meh'],
                            retbins=False, precision=3, duplicates='raise')


def typing_effect(message, font_size=17):
    st.markdown(
        f"<p id='typing' style='text-align: center; font-size: {font_size}px;'></p>",
        unsafe_allow_html=True
    )

    typing_script = """
    <script>
        var text = `""" + message.replace("`", "\\`") + """`;
        var typingSpeed = 50;
        var element = document.getElementById('typing');
        function typeCharacter(i) {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(function() { typeCharacter(i); }, typingSpeed);
            }
        }
        typeCharacter(0);
    </script>
    """
    st.markdown(typing_script, unsafe_allow_html=True)

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_generation_name(generation):
    return f"{generation}{'st' if generation == 1 else 'nd' if generation == 2 else 'rd' if generation == 3 else 'th'} Gen"




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


def calculate_effectiveness(attacker_type_1, attacker_type_2, defender_name, attacker_base_hit):
    defender_rows = df[df['name'] == defender_name]
    against_column = 'against_' + attacker_type_1.lower()
    val_def = defender_rows[against_column].values[0]
    impact = attacker_base_hit * val_def

    if (attacker_type_2):
        against_column = 'against_' + attacker_type_2.lower()
        if against_column == 'against_fighting':
            return impact
        else:
            val_def = defender_rows[against_column].values[0]
            impact = impact + (attacker_base_hit * val_def)

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
            damage_taken_defender = calculate_effectiveness(attacker_row['type_1'], None, defender_name,
                                                            attacker_row['attack'])
            if defender_row['total_points'] - damage_taken_defender < 0:
                defender_row['total_points'] = 0
            else:
                defender_row['total_points'] = defender_row['total_points'] - damage_taken_defender
        else:
            damage_taken_defender = calculate_effectiveness(attacker_row['type_1'], attacker_row['type_2'],
                                                            defender_name, attacker_row['attack'])
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



def get_pokemon_details(selected_pokemon, theme, winner):
    # Fetch the Pokemon data from the API
    pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{selected_pokemon.lower()}"
    response = requests.get(pokeapi_url)
    pokemon_data = None

    if response.status_code == 200:
        pokemon_data = response.json()  # Assign the data
        pokemon_name = pokemon_data["name"].capitalize()

    if pokemon_data:
        # Use PokeSprites API for higher resolution images
        pokemon_image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_data['id']}.png"
        response_image = requests.get(pokemon_image_url)

        st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()} </h1>", unsafe_allow_html=True)
        image = Image.open(BytesIO(response_image.content))

        if winner == "yes":
            image = Image.open(BytesIO(response_image.content))
        elif winner == "no":
            image = image.convert("L")



        max_image_width = 600
        max_image_height = 600
        image.thumbnail((max_image_width, max_image_height))
        # st.image(image, use_column_width=True)
        st.markdown(
            f"<div style='max-width: {max_image_width}px; max-height: {max_image_height}px; margin: 0 auto; text-align: center;'>"
            f"<img src='data:image/png;base64,{image_to_base64(image)}' alt='{pokemon_name}' style='width: 100%; max-width: {max_image_width}px; max-height: {max_image_height}px;'>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("")
        st.markdown(f"<p style='text-align: center; font-size: 0.75vw;'>{catch_rate_phrase(pokemon_name)}</p>",
                    unsafe_allow_html=True)


    else:
        pokemon_name = selected_pokemon  # Set a default name
        local_image_path = "Pokeviz/bin/images/pokemon_image_nf.jpg"

        st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
        local_image = Image.open(local_image_path)
        # Restrict image size to a certain resolution
        max_image_width = 500
        max_image_height = 500
        local_image.thumbnail((max_image_width, max_image_height))
        st.markdown(
            f"<div style='display: flex; justify-content: center;'>"
            f"<img src='data:image/png;base64,{image_to_base64(local_image)}' alt='{pokemon_name}' style='width: 660px;'>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align: center; font-size: 0.5vw;'>Sorry we cannot find the image of {(pokemon_name)} 😔 </p>",
            unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align: center; font-size: 0.5vw;'>But you can still have a Battle!</p>",
            unsafe_allow_html=True)

    stats = {
        "Name": selected_pokemon,
        "Generation": get_generation_name(df.loc[df["name"] == selected_pokemon, "generation"].values[0]),
        "Type": df.loc[df["name"] == selected_pokemon, "type_1"].values[0],
        "Attack": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "attack"].values[0]),
        "Special Attack": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "sp_attack"].values[0]),
        "Defense": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "defense"].values[0]),
        "Special Defense": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "sp_defense"].values[0]),
        "Total Points": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "total_points"].values[0]),
        "Speed": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "speed"].values[0]),
        "HP": "{:.2f} pts".format(df.loc[df["name"] == selected_pokemon, "hp"].values[0])
    }

    # Convert the stats dictionary to a DataFrame with two columns
    stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=["Value"])

    # Apply custom CSS for styling
    st.markdown(
        """
        <style>
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        .styled-table th, .styled-table td {
            padding: 12px 15px;
            border: 1px solid #e0e0e0;
            text-align: left;
        }
        .styled-table th {
            background-color: #f5f5f5;
            color: #333;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the table using Streamlit's st.table
    st.table(stats_df.style.set_table_styles([
        {"selector": "th",
         "props": [("background-color", f"{theme}"), ("color", "#333"), ("font-weight", "bold"), ("font-size", "17px")]},
        {"selector": "td",
         "props": [("border", f"1px solid {theme}"), ("padding", "10px 32px"), ("text-align", "left")]},
        {"selector": "thead",
         "props": [("display", "none")]}
    ]))





st.set_page_config(page_title="PokeViz App", layout="wide")


st.markdown("<div style='text-align: center; font-size: 2.8vw; font-weight: bold;'>Welcome to the Showdown 😈</div>",
            unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 2vw;'>Unleash the Poke-challenger within!</div>",
            unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 0.7vw;'>It's time to clash, compete, and catch 'em in the ultimate battle showdown! Let the Pokémon brawl begin!</div>",
            unsafe_allow_html=True)



# Button Image
button_image_path = "Pokeviz/bin/images/Poke_Ball.webp"
button_image = Image.open(button_image_path)
# Reduce the image size to improve loading time
button_image.thumbnail((200, 200))  # Adjust the size as needed



contender1 = ''
contender2 = ''
theme1 = '#FFA78C'
theme2 = '#E7F4D3'


bg_space1, bg_1_1, bg_space2, bg_1_2, bg_space3, bg_1_3, bg_space4 = st.columns(
    (0.05, 0.4, 0.01, 0.2, 0.01, 0.4, 0.05)
)

def left_side(winner):
    with bg_1_1:
        st.markdown(f"<p style='text-align: center; font-size: 20px;'> - Select the 1st Contender - </p>",
                    unsafe_allow_html=True)

        # Create two columns for filters
        bgr_column1, bgr_column2, bgr_column3, bgr_column4 = st.columns(4)

        # Filter by Generation
        default_generation = 1
        selected_generation = bgr_column1.selectbox("Generation", df["generation"].unique(),
                                                    key="generation")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["generation"] == selected_generation]
        default_status = 'Normal'
        selected_status = bgr_column2.selectbox("Select Status", filtered_df_by_generation["status"].unique(),
                                                index=filtered_df_by_generation["status"].unique().tolist().index(
                                                    default_status),
                                                key="status")

        # Filter by Type based on selected Generation
        filtered_df_by_generation = df[df["status"] == selected_status]
        default_type = 'Electric'
        unique_types = filtered_df_by_generation["type_1"].unique().tolist()

        if default_type in unique_types:
            default_type_index = unique_types.index(default_type)
        else:
            default_type_index = 0

        selected_type = bgr_column3.selectbox("Select a Type", unique_types, index=default_type_index, key="type")

        # Filter by Name based on selected Generation and Type
        filtered_df_by_type = filtered_df_by_generation[filtered_df_by_generation["type_1"] == selected_type]

        selected_pokemon = bgr_column4.selectbox("Select a Pokemon", filtered_df_by_type["name"], key="pokemon")

        if selected_type  in ["Fire", "Poison", "Electric", "Fighting", "Dragon"]:
            theme_1 = "#FFA78C"
        elif selected_type in ["Water", "Dragon", "Steel"]:
            theme_1 = "#D4F1F9"
        elif selected_type in ["Grass", "Ice", "Fairy", "Ghost"]:
            theme_1 = "#E7F4D3"
        elif selected_type in ["Bug", "Normal", "Dark", "Ground", "Psychic", "Rock"]:
            theme_1 = "#F1D5AA"

        contender1 = selected_pokemon

        get_pokemon_details(contender1, theme1, winner)
        return contender1

contender1 = left_side("nowinner")

def right_side(winner):
    with bg_1_3:
        st.markdown(f"<p style='text-align: center; font-size: 20px;'> - Select the 2nd Contender - </p>",
                    unsafe_allow_html=True)

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
        if selected_type  in ["Fire", "Poison", "Electric", "Fighting", "Dragon"]:
            theme_2 = "#FFA78C"
        elif selected_type in ["Water", "Dragon", "Steel"]:
            theme_2 = "#D4F1F9"
        elif selected_type in ["Grass", "Ice", "Fairy", "Ghost"]:
            theme_2 = "#E7F4D3"
        elif selected_type in ["Bug", "Normal", "Dark", "Ground", "Psychic", "Rock"]:
            theme_2 = "#F1D5AA"


        contender2 = selected_pokemon

        get_pokemon_details(contender2, theme_2, winner)
        return contender2

contender2 = right_side("nowinner")



with bg_1_2:
    game_space1, game_1_1, game_space2, = st.columns(
        (0.135, 0.5, 0.01)
    )



    with game_1_1:
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

        # Center-aligned button with image
        button_image_path = "Pokeviz/bin/images/Poke_Ball.webp"
        button_image = Image.open(button_image_path)
        # Reduce the image size to improve loading time
        button_image.thumbnail((300, 300))  # Adjust the size as needed

        # image_width = 500  # Adjust the width as needed
        # st.markdown(
        #     f"<div style='display: flex; justify-content: center;'>"
        #     f"<img src='data:image/png;base64,{base64.b64encode(button_image.read()).decode()}' "
        #     f"style='width: 100%; max-width: {image_width}px;'>"
        #     f"</div>",
        #     unsafe_allow_html=True
        # )

        st.markdown(
            f"<img src='data:image/png;justify-content: center; base64,{image_to_base64(button_image)}' alt='pokeball' style='width: 100%; max-width: 300px;'>",
            unsafe_allow_html=True)

        st.markdown(
            "<p style='color: rgba(0, 0, 0, 0.5); font-size: 0.6vw; text-align: left;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Click to start the battle</p>",
            unsafe_allow_html=True
        )
        st.markdown("")

    bt_space1, bt_1_1, bt_space2, = st.columns(
        (0.20, 0.3, 0.01)
    )

    battle_log=''
    winner=''
    with bt_1_1:
        if st.button('Start Battle'):
            # Example battle simulation
            battle_log, winner = simulate_turn_based_battle(contender1, contender2)
            st.header("")
            st.header("")
            st.header("")
            st.header("")

    for log in battle_log:
        st.markdown(
            f"<p style='text-align: center; font-size: 0.6vw;'>{log}</p>",
            unsafe_allow_html=True
        )
        time.sleep(1.0)

    if winner != '':
        st.markdown(
            f"<p style='text-align: center; font-size: 1.7vw; font-weight: bold; color: red; margin-bottom: 5px;'>{winner}</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align: center; font-size: 1.5vwpx;'>  Wins the battle!🏆</p>",
            unsafe_allow_html=True
        )


        # if winner == contender1:
        #     left_side("yes")
        #     right_side("no")
        # else:
        #     left_side("no")
        #     right_side("yes")
    elif winner == '':
        print("")

    else:
        st.markdown("\nIt's a tie!")
    st.markdown("</div>", unsafe_allow_html=True)
