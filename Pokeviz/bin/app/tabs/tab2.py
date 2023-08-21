import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px
from tabulate import tabulate
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pydub import AudioSegment
from pydub.playback import play

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_generation_name(generation):
    return f"{generation}{'st' if generation == 1 else 'nd' if generation == 2 else 'rd' if generation == 3 else 'th'} Gen"



def display_tab(df, df2, color_theme):


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


    if selected_type  in ["Fire", "Poison", "Electric", "Fighting", "Dragon"]:
        theme = "#FFA78C"
    elif selected_type in ["Water", "Dragon", "Steel"]:
        theme = "#D4F1F9"
    elif selected_type in ["Grass", "Ice", "Fairy", "Ghost"]:
        theme = "#E7F4D3"
    elif selected_type in ["Bug", "Normal", "Dark", "Ground", "Phychic", "Rock"]:
        theme = "#F1D5AA"



    # Display the Pokemon image and stats
    image_column, stats_column = st.columns((1, 2))
    kyp_space1, image_column, kyp_space2, stats_column, kyp_space3 = st.columns((0.1, 0.5, 0.1, 0.7, 0.1))

    desc_column, graph_column = st.columns((1, 2))
    kyp2_space1, desc_column, kyp2_space2, graph_column, kyp2_space3 = st.columns((0.1, 0.5, 0.1, 0.7, 0.1))

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

        with image_column:
            st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()} </h1>", unsafe_allow_html=True)
            image = Image.open(BytesIO(response_image.content))
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

        with desc_column:
            species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_data['id']}/"
            species_response = requests.get(species_url)
            if species_response.status_code == 200:

                species_data = species_response.json()
                flavor_text_entries = species_data["flavor_text_entries"]

                # Preprocess and remove duplicates from description
                unique_description = []
                seen_sentences = set()
                for entry in flavor_text_entries:
                    if entry["language"]["name"] == "en":
                        sentence = entry["flavor_text"].replace("\n", " ").lower()
                        sentence = " ".join(sentence.split())
                        if sentence not in seen_sentences:
                            seen_sentences.add(sentence)
                            unique_description.append(entry["flavor_text"])

                # Form the modified description
                poke_api_description = "\n".join(unique_description)
            else:
                poke_api_description = f"We love {selected_pokemon}, but unfortunately we did not find any information about it!!! :("

            # Display Pokemon description
            st.write(f"### Something you should know about {selected_pokemon}")
            st.write(poke_api_description)

    else:
        pokemon_name = selected_pokemon  # Set a default name
        local_image_path = "Pokeviz/bin/images/pokemon_image_nf.jpg"
        with image_column:
            st.markdown(f"<h1 style='text-align: center;'>{pokemon_name.upper()}</h1>", unsafe_allow_html=True)
            local_image = Image.open(local_image_path)
            # Restrict image size to a certain resolution
            max_image_width = 500
            max_image_height = 500
            local_image.thumbnail((max_image_width, max_image_height))
            st.image(local_image, use_column_width=True, caption=f"Sorry but I cannot find an image of {(pokemon_name)}")


    with stats_column:
        st.markdown(f"<h1 style='text-align: center;'>Statistics</h1>", unsafe_allow_html=True)

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
             "props": [("background-color", f"{theme}"), ("color", "#333"), ("font-weight", "bold")]},
            {"selector": "td",
             "props": [("border", f"1px solid {theme}"), ("padding", "10px 12px"), ("text-align", "left")]},
            {"selector": "thead",
             "props": [("display", "none")]}
        ]))






    with graph_column:
        # Generate radar chart
        radar_data = {
            "Stats": ["Attack", "Defense", "Special Attack", "Special Defense", "Speed", "HP"],
            "Values": [
                df.loc[df["name"] == selected_pokemon, "attack"].values[0],
                df.loc[df["name"] == selected_pokemon, "defense"].values[0],
                df.loc[df["name"] == selected_pokemon, "sp_attack"].values[0],
                df.loc[df["name"] == selected_pokemon, "sp_defense"].values[0],
                df.loc[df["name"] == selected_pokemon, "speed"].values[0],
                df.loc[df["name"] == selected_pokemon, "hp"].values[0],
            ],
        }

        radar_df = pd.DataFrame(radar_data)

        radar_fig = px.line_polar(radar_df, r="Values", theta="Stats", line_close=True)
        radar_fig.update_traces(fill="toself", line_color=theme)

        # Customize radar chart layout
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(showticklabels=False, ticksuffix="%", showline=False),
                angularaxis=dict(showticklabels=True, linecolor="gray"),
            ),
            showlegend=True,  # Display legend
            legend=dict(x=0.9, y=0.9),  # Adjust legend position
            title=dict(text="Pokémon Base Stats Profile", x=0.5, xanchor="center", y=0.001,
                       font=dict(size=24)),  # Adjust title position and margin
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
            margin=dict(l=0, r=0, b=50, t=50),  # Adjust margin
        )

        # Display radar chart
        st.plotly_chart(radar_fig)

        def get_pokemon_cry(pokemon_name):
            base_url = "https://www.pkmnapi.com/api/v1/pokemon"
            response = requests.get(f"{base_url}/{pokemon_name}/cry")

            if response.status_code == 200:
                cry_data = response.json()
                cry_url = cry_data['sound']
                return cry_url
            else:
                return None

        st.title("Pokemon Cry Player")
        pokemon_name = selected_pokemon

        if st.button("Play Cry"):
            cry_url = get_pokemon_cry(pokemon_name)
            if cry_url:
                cry_audio = AudioSegment.from_file(cry_url)
                play(cry_audio)
                st.success(f"Playing cry for {pokemon_name}")
            else:
                st.error(f"Failed to retrieve cry for {pokemon_name}")



if __name__ == "__main__":
    display_tab()
