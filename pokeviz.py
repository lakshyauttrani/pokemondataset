import urllib.request

# import gender_guesser.detector as gender
#import openpyxl
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import xmltodict
from pandas import json_normalize
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
import requests
from PIL import Image
from io import BytesIO
import time
import random


# Add a dark mode slider button


df = pd.read_csv("pokedex_input.csv")
df2 = pd.read_csv("revenue.csv", sep=';')

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


#Chart Functions
def create_violin_plot(df, stat, best_type):
    fig_violin = px.violin(df[df['type_1'] == best_type], y=stat, x="type_1", box=True, points="all",  color_discrete_sequence=["#9EE6CF"])
    fig_violin.update_layout(
        title=f"{stat.capitalize()} Distribution for {best_type}",
        xaxis_title="Type 1",
        yaxis_title=stat.capitalize(),
    )
    return fig_violin


st.set_page_config(page_title="PokeViz App", layout="wide")


dark_mode = st.sidebar.checkbox("Dark Mode")

# Set the theme based on the dark mode status
dark = """
<style>
    .stApp {
        background-color: black;
        color: white; /* Change font color to white in dark mode */
    }
    .stTab {
        color: white; /* Change tab color to white in dark mode */
    }
</style>
"""

light = """
<style>
    .stApp {
        background-color: white;
        color: black; /* Change font color to black in light mode */
    }
    .stTab {
        color: black; /* Change tab color to black in light mode */
    }
</style>
"""

st.markdown(light, unsafe_allow_html=True)

# Create a toggle button
toggle = st.button("Toggle theme")

# Use a global variable to store the current theme
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Change the theme based on the button state
if toggle:
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

# Apply the theme to the app
if st.session_state.theme == "dark":
    st.markdown(dark, unsafe_allow_html=True)
else:
    st.markdown(light, unsafe_allow_html=True)

# Display some text
st.write("This is a streamlit app with a toggle button for themes.")



#Header
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)

with row0_1:
    st.header("Welcome to Pokéviz")

    st.markdown(
        "Step into the extraordinary realm of captivating creatures, where imagination knows no bounds! Prepare to embark on an exhilarating journey through the enchanting world of Pokemon in this data-driven adventure."

    )
    st.markdown(
        "⚡ Uncover the Hidden Insights! ⚡"
    )

# Button Image
button_image_path = "comp_code/Battle_groud.webp"
button_image = Image.open(button_image_path)
# Reduce the image size to improve loading time
button_image.thumbnail((200, 200))  # Adjust the size as needed

# Button to open the new Streamlit page
with row0_2:
    if st.image(button_image, use_column_width=True, caption="Click to enter the battle ground"):
        link = "http://localhost:8501comp_code/pokeviz2.py"
        # Use Markdown to create a hyperlink to the new Streamlit app




line1_spacer1, line1_1, line1_spacer2 = st.columns((0.1, 3.2, 0.1))

user_name = "Test_Krishna"
with line1_1:
    st.header("Analyzing the Data for: **{}**".format(user_name))



tab1, tab2, tab3, tab4, tab5 = st.tabs(["Main", "Explore your Pokemon", "EDA-1", "EDA-2", "Battle Ground"])
with tab1:
    row1_space1, row_1_1, row1_space2, row_1_2, row3_space3 = st.columns(
        (0.1, 1, 0.1, 1, 0.1)
    )

    with row_1_1:
        # Line chart for revenue over the years
        st.header("Pokemon Go Revenue")
        fig_line = px.line(
            df2,
            x='year',
            y='revenue_billions',
            title='Revenue Trend',
            labels={'year': 'Year', 'revenue_billions': 'Revenue in billions'},
            line_shape='linear',  # You can change this to 'spline', 'vhv', 'hvh', etc. for different line shapes
            color_discrete_sequence=["#9EE6CF"],  # You can change the line color here
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with row_1_2:

        # Area chart for revenue over the years
        st.header("Pokemon Go Users Over the Years")
        fig_area = px.area(
            df2,
            x='year',
            y='users_millions',
            title='Users',
            labels={'year': 'Year', 'users_millions': 'Users in Millions'},
            line_shape='linear',  # You can change this to 'spline', 'vhv', 'hvh', etc. for different line shapes
            color_discrete_sequence=["#9EE6CF"],  # You can change the area color here
        )
        st.plotly_chart(fig_area, use_container_width=True)

    row2_space1, row_2_1, row2_space2, row_2_2, row2_space3 = st.columns(
        (0.1, 1, 0.1, 1, 0.1)
    )

    with row_2_1:
        # EDA 1: Type Distribution
        st.header("Pokemon Distribution through generation")
        type_df = df["type_1"].value_counts().reset_index()
        type_df.columns = ["Type", "Count"]
        fig_type = px.pie(
            type_df,
            names="Type",
            values="Count",
            title="Pokemon Generation",
            color_discrete_sequence=["#9EE6CF"],
        )
        st.plotly_chart(fig_type, use_container_width=True)

    with row_2_2:
        # EDA 2: Generation Distribution
        st.header("Pokemon abilities")
        gen_df = df["ability_1"].value_counts().nlargest(10).reset_index()
        gen_df.columns = ["Ability", "Count"]
        fig_gen = px.bar(
            gen_df,
            x="Ability",
            y="Count",
            title="Pokemon Ability Distribution",
            color_discrete_sequence=["#9EE6CF"],
        )
        st.plotly_chart(fig_gen, use_container_width=True)

    column1_space, column1, column2_space, column2, column3_space, column3, column4_space, column4, column5_space, column5, column6_space = st.columns(
        (0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1)
    )

    # Calculations for Abilities
    stats_columns = ['attack', 'defense', 'sp_attack', 'sp_defense', 'speed']


    def calculate_best_type(df, stats):
        stats_columns = stats
        best_types = {}

        for stat in stats_columns:
            best_type_idx = df[stat].idxmax()
            best_type = df.loc[best_type_idx, 'type_1']
            mean_value = round(df[stat].mean())
            best_types[stat] = {'best_type': best_type, 'mean_value': mean_value}

        return best_types


    best_types = calculate_best_type(df, stats_columns)

    # Define the custom color (e.g., blue) using hexadecimal code
    custom_color = "#9EE6CF"

    # CSS styling for the rounded corner box
    css = f"""
        border-radius: 10px;
        border: 2px solid {custom_color};
        padding: 10px;
        text-align: center;
        color: {custom_color};
        font-weight: bold;
    """

    with column1:
        for stat in stats_columns[:1]:  # First two stats
            # Display the rounded corner box using markdown
            st.markdown("##### Best Attack")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"])
            st.plotly_chart(fig_violin, use_container_width=True)

    with column2:
        for stat in stats_columns[1:2]:  # Last three stats
            st.markdown("##### Best Defense")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"])
            st.plotly_chart(fig_violin, use_container_width=True)

    with column3:
        for stat in stats_columns[2:3]:  # First two stats
            st.markdown("##### Best Special Attack")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"])
            st.plotly_chart(fig_violin, use_container_width=True)

    with column4:
        for stat in stats_columns[3:4]:  # Last three stats
            st.markdown("##### Best Special Defense")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"])
            st.plotly_chart(fig_violin, use_container_width=True)

    with column5:
        for stat in stats_columns[4:5]:  # Last three stats
            st.markdown("##### Best Speed")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"])
            st.plotly_chart(fig_violin, use_container_width=True)


with tab2:
    # Create two columns for filters
    filter_column1, filter_column2, filter_column3 = st.columns(3)

    # Filter by Generation
    selected_generation = filter_column1.selectbox("Select a Generation", df["generation"].unique())

    # Filter by Type based on selected Generation
    filtered_df_by_generation = df[df["generation"] == selected_generation]
    selected_type = filter_column2.selectbox("Select a Type", filtered_df_by_generation["type_1"].unique())

    # Filter by Name based on selected Generation and Type
    filtered_df_by_type = filtered_df_by_generation[filtered_df_by_generation["type_1"] == selected_type]
    selected_pokemon = filter_column3.selectbox("Select a Pokemon", filtered_df_by_type["name"])

    # Fetch the Pokemon data from the API
    pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{selected_pokemon.lower()}"
    response = requests.get(pokeapi_url)

    if response.status_code == 200:
        pokemon_data = response.json()
        # Use PokeSprites API for higher resolution images
        pokemon_image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_data['id']}.png"
        pokemon_name = pokemon_data["name"]

        # Display the Pokemon image and stats
        image_column, stats_column = st.columns((1, 2))

        kyp_space1, image_column, kyp_space2, stats_column, kyp_space3 = st.columns(
            (0.1, 0.5, 0.1, 0.7, 0.1)
        )

        # Check if the higher resolution image is available
        response_image_high_res = requests.get(pokemon_image_url)
        if response_image_high_res.status_code == 200:
            with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                image = Image.open(BytesIO(response_image_high_res.content))
                st.image(image, use_column_width=True)
        else:
            # If higher resolution image is not available, use the other API with lower resolution
            pokemon_image_url_low_res = pokemon_data["sprites"]["front_default"]
            with image_column:
                st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
                response_image_low_res = requests.get(pokemon_image_url_low_res)
                image_low_res = Image.open(BytesIO(response_image_low_res.content))
                st.image(image_low_res, use_column_width=True, caption="Sorry for the image quality")

        with stats_column:
            # st.header("Stats")
            st.markdown(f"<h1 style='text-align: center;'>Stats</h1>", unsafe_allow_html=True)

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
                dict(selector="td", props=[("padding", "8px")])  # Increase row spacing

            ]))

    else:
        st.warning("Pokemon not found in the API.")

with tab5:
    bg_space1, bg_1_1, bg_space2, bg_1_2, bg_space3, bg_1_3 = st.columns(
        (0.1, 1, 0.1, 0.4, 0.1, 1)
    )

    contender1 = ''
    contender2 = ''

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
                dict(selector="th", props=[("max-width", "15px")]),
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
                dict(selector="th", props=[("max-width", "15px")]),
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
                dict(selector="th", props=[("max-width", "15px")]),
                dict(selector="td", props=[("padding", "2px")])  # Increase row spacing

            ]))
            st.markdown(catch_rate_phrase(pokemon_name))

    with bg_1_2:
        # Load the button image
        button_image_path = "comp_code/Poke_Ball.webp"
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
        if st.image(button_image, use_column_width=True, caption="Click to start the battle"):
            link = "https://pvpoke.com/train/"
            if st.button('Start Battle'):
                # Example battle simulation
                battle_log, winner = simulate_turn_based_battle(contender1, contender2)

                for log in battle_log:
                    st.markdown(log)
                    # st.markdown("![Alt Text](https://media.giphy.com/media/dzIrXQiyqgsSbGGpZR/giphy.gif)")
                    time.sleep(1.0)
                if winner:
                    st.markdown(f"\n{winner} wins the battle!")
                else:
                    st.markdown("\nIt's a tie!")

with tab3:
    # Introduction
    st.write(
        "Dive into the fascinating world of Pokémon types and unravel their hidden strengths and strategies. "
        "Let's journey together to explore the intricate relationships among different types."
    )

    # Graph layout customization
    fig_layout = dict(
        margin=dict(l=0, r=0, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    # Graph 1 & 2 side by side
    st.header("Graph 1: Enigmatic Type Distribution")
    col1, col2 = st.columns(2)

    # Graph 1: Distribution of Pokémon Types
    type_counts = df['type_1'].value_counts().sort_values(ascending=False)
    fig1 = px.bar(x=type_counts.index, y=type_counts.values, labels={'x': 'Type', 'y': 'Count'})
    fig1.update_layout(**fig_layout)
    col1.plotly_chart(fig1)
    st.write("Unveil the frequencies of different Pokémon types.")

    # Graph 2: Type Effectiveness Heatmap
    type_cols = ['against_bug', 'against_dark', 'against_dragon', 'against_electric', 'against_fairy']
    type_effectiveness = df[type_cols]
    fig2 = px.imshow(type_effectiveness.corr(), labels=dict(x="Type", y="Type"))
    fig2.update_layout(**fig_layout)
    col2.plotly_chart(fig2)
    st.write("Decode the intricate web of type effectiveness correlations.")

    # Explanation for Graphs 1 & 2
    st.write(
        "Graph 1: Discover the prevalence of each type among Pokémon species. For example, Fire and Water types "
        "are frequent, while Ghost and Bug types are less common."
    )
    st.write(
        "Graph 2: Unravel the secret ties between type effectiveness. Higher correlations indicate stronger type interactions. "
        "For instance, Fighting types are effective against Normal types, which is evident from the high correlation."
    )

    # Graph 3: Elemental Power Showcase
    st.header("Graph 3: Elemental Power Showcase")
    avg_stats_by_type = df.groupby('type_1')[['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']].mean()
    avg_stats_by_type = avg_stats_by_type.sort_values(by='attack', ascending=False)
    fig3 = px.bar(avg_stats_by_type, labels=dict(type_1="Type", value="Average Stat"),
                  title="Unveil Elemental Powers: Average Base Stats by Type")
    fig3.update_layout(**fig_layout)
    st.plotly_chart(fig3)
    st.write(
        "Graph 3: Delve into the elemental prowess of each type. For example, the Attack of Fighting and Dragon types "
        "is generally higher compared to other types."
    )

    # Graph 4: Dual-Type Marvels
    st.header("Graph 4: Dual-Type Marvels")
    type_combinations = df.groupby(['type_1', 'type_2']).size().reset_index(name='count')
    fig4 = px.scatter(type_combinations, x='type_1', y='type_2', size='count',
                      labels=dict(type_1="Primary Type", type_2="Secondary Type", count="Count"))
    fig4.update_layout(**fig_layout)
    st.plotly_chart(fig4)
    st.write(
        "Graph 4: Embark on an exploration of dual-type Pokémon. This scatter plot reveals various combinations, "
        "like Water-Flying and Grass-Poison types, showcasing the diversity of type interactions."
    )

    # Conclusion
    st.header("Conclusion")
    st.write(
        "By immersing ourselves in these visualizations, we uncover the tapestry of Pokémon types. The interplay between "
        "types, their frequencies, effectiveness, strengths, and partnerships, weave a captivating narrative of battles and strategy."
    )
