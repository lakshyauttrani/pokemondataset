import streamlit as st
import pandas as pd
import plotly.express as px


def calculate_best_type(df, stats):
    stats_columns = stats
    best_types = {}

    for stat in stats_columns:
        best_type_idx = df.groupby('type_1')[stat].mean().idxmax()
        best_type = best_type_idx
        mean_value = round(df[df['type_1'] == best_type_idx][stat].mean())
        best_types[stat] = {'best_type': best_type, 'mean_value': mean_value}

    return best_types


# Chart Functions
def create_violin_plot(df, stat, best_type, color_theme):
    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]
    fig_violin = px.violin(df[df['type_1'] == best_type], y=stat, x="type_1", box=True, points="all",
                           color_discrete_sequence=[color1])
    fig_violin.update_layout(
        title=f"{stat.capitalize()} Distribution for {best_type}",
        xaxis_title="",
        yaxis_title=stat.capitalize()
    )
    # Disable tooltips by setting hoverinfo to 'skip' for the trace
    fig_violin.update_traces(hoverinfo='skip')

    return fig_violin


def display_tab(df, df2, color_theme):
    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]

    # Row1
    row1_space1, row_1_1, row1_space2, row_1_2, row3_space3 = st.columns(
        (0.005, 1, 0.1, 1, 0.1)
    )

    df2['revenue_billions'] *= 1000
    df_long = pd.melt(df2, id_vars=["year"],
                      value_vars=["revenue_billions", "app_purchases_millions"],
                      var_name="metric", value_name="value")

    with row_1_1:
        # Line chart for revenue, users, and app purchases over the years
        fig_line = px.line(
            df_long,
            x='year',
            y='value',
            title='Catching Insights: Pokémon Financial Journey',
            labels={'year': 'Year', 'value': 'Value', 'metric': 'Metric'},
            color='metric',
            line_shape='linear',
            color_discrete_sequence=[color1, color5],
        )
        fig_line.update_layout(title_font=dict(size=30),
                               legend=dict(x=0, y=1, bgcolor='rgba(255, 255, 255, 0.5)',
                                           bordercolor='rgba(0, 0, 0, 0.5)'))  # Move legend to top left corner
        fig_line.update_yaxes(title_text="Value in Millions", tickprefix="$")
        fig_line.for_each_trace(lambda t: t.update(name=t.name.replace("_millions", "").replace("_", " ").title()))
        fig_line.for_each_trace(lambda t: t.update(name=t.name.replace("Billions", "").replace("_", " ").title()))

        st.plotly_chart(fig_line, use_container_width=True)

        description1 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;">Delve into the captivating financial odyssey of Pokémon GO as we unveil its remarkable journey through the years. From its inception in <strong>2016</strong>,the game has generated an astonishing <strong style="color: %s; font-weight: bold;">$830 million</strong> in revenue.
            </p></div>
        """ % color5

        description2 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;">In <strong style="color: %s; font-weight: bold;">2020</strong>, the popular Pokémon GO game achieved a staggering milestone, reaching its peak revenues of <stron style="color: %s; font-weight: bold;">$1.3 billion</strong>.
            </p>
        </div>
        """ % (color5, color5)

        st.write(description1, unsafe_allow_html=True)
        st.write(description2, unsafe_allow_html=True)

    with row_1_2:
        # Area chart for revenue over the years
        fig_area = px.area(
            df2,
            x='year',
            y='users_millions',
            title='Pokemon Go Users Over the Years',
            labels={'year': 'Year', 'users_millions': 'Users in Millions'},
            line_shape='linear',  # You can change this to 'spline', 'vhv', 'hvh', etc. for different line shapes
            color_discrete_sequence=[color3],  # You can change the area color here
        )
        fig_area.update_layout(title_font=dict(size=30))

        st.plotly_chart(fig_area, use_container_width=True)

        description2_1 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;">In its debut year, Pokémon GO attracted an impressive user base of <strong style="color: %s; font-weight: bold;">232</strong> million players.
              </p></div>
        """ % color5
        st.write(description2_1, unsafe_allow_html=True)

    # Row2
    row2_space1, row_2_1, row2_space2, row_2_2, row2_space3 = st.columns(
        (0.005, 1, 0.1, 1, 0.1)
    )

    with row_2_1:
        # EDA 1: Type Distribution

        type_df = df["type_1"].value_counts().reset_index()
        type_df.columns = ["Type", "Count"]

        base_color = color1  # Replace with your desired base color in RGB format

        # Convert the hexadecimal color to RGB format
        base_color_rgb = tuple(int(base_color[i:i + 2], 16) for i in (1, 3, 5))

        # Generate a list of colors based on the base color using hexadecimal format
        num_colors = 6  # Number of colors in the list
        color_scale = []
        step_size = 40

        for i in range(num_colors):
            # Calculate new RGB values for each color by manipulating the base color
            r = max(0, base_color_rgb[0] - i * step_size)
            g = max(0, base_color_rgb[1] - i * step_size)
            b = max(0, base_color_rgb[2] - i * step_size)

            # Convert RGB values to hexadecimal format
            hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)

            color_scale.append(hex_color)

        # Select the top 5 types and group the rest as "Others"
        top5_type_df = type_df.head(5)
        other_count = type_df["Count"].sum() - top5_type_df["Count"].sum()
        other_row = pd.DataFrame({"Type": ["Others"], "Count": [other_count]})
        top5_type_df = pd.concat([top5_type_df, other_row], ignore_index=True)

        fig_type = px.pie(
            top5_type_df,
            names="Type",
            values="Count",
            title="Pokémon Type Distribution",
            color_discrete_sequence=color_scale,
        )
        fig_type.update_layout(title_font=dict(size=30))

        st.plotly_chart(fig_type, use_container_width=True)

        description2_1 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;">Splash! <strong style="color: %s; font-weight: bold;">Water-type Pokémon</strong> steal the spotlight as the most common characters across generations. From old-time favorites like Squirtle and Gyarados to newer stars like Greninja, whether they're making a splash or simply enjoying aquatic adventures, these water-loving critters add their own special magic to the Pokémon world
            </p></div>
        """ % color5
        st.write(description2_1, unsafe_allow_html=True)

    with row_2_2:
        # EDA 2: Generation Distribution
        gen_df = df["ability_1"].value_counts().nlargest(10).reset_index()
        gen_df.columns = ["Ability", "Count"]
        fig_gen = px.bar(
            gen_df,
            x="Ability",
            y="Count",
            title="Pokémon Abilities",
            labels={'Ability': 'Ability', 'Count': '#Pokémons'},
            color_discrete_sequence=[color2],
        )
        fig_gen.update_layout(title_font=dict(size=30))

        st.plotly_chart(fig_gen, use_container_width=True)

        description2_1 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;"> In the world of Pokémon, abilities come in all flavors, and it's true that  <strong style="color: %s; font-weight: bold;">Levitate stands out</strong> as one of the most common abilities among Pokémon. Levitate provides a significant advantage by granting Pokémon <strong style="color: %s; font-weight: bold;">immunity to Ground-type moves</strong>, making it a prevalent and sought-after trait among many species.
            </p></div>
        """ % (color5, color5)
        st.write(description2_1, unsafe_allow_html=True)

    st.header("Find the right Pokémon types for every skill")

    description2_2 = """
        <div style="font-size: 22px; line-height: 1.6; ">
            <p style="margin-bottom: 16px;"> Discover the ultimate Pokémon types that dominate the battlefield: the sharpest attackers Dragons , the most resilient defenders Steel Pokémons ,the devastating special attackers Psychics, the unbreakable walls of special defense Fairies, and the lightning-fast speeders flying Pokémons.
            </p></div>
        """
    st.write(description2_2, unsafe_allow_html=True)

    # Row3
    column1_space, column1, column2_space, column2, column3_space, column3, column4_space, column4, column5_space, column5, column6_space = st.columns(
        (0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1)
    )

    # Calculations for Abilities
    stats_columns = ['attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
    best_types = calculate_best_type(df, stats_columns)

    # Define the custom color (e.g., blue) using hexadecimal code
    custom_color = color2

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
        # Display the rounded corner box using markdown
        st.markdown("##### Best Attack")
        st.markdown(
            f'<div style="{css}">{best_types[stats_columns[0]]["best_type"]}<br>Mean Score: {best_types[stats_columns[0]]["mean_value"]}</div>',
            unsafe_allow_html=True)
        fig_violin = create_violin_plot(df, stats_columns[0], best_types[stats_columns[0]]["best_type"], color_theme)
        st.plotly_chart(fig_violin, use_container_width=True)

    with column2:
        # Display the rounded corner box using markdown
        st.markdown("##### Best Defense")
        st.markdown(
            f'<div style="{css}">{best_types[stats_columns[1]]["best_type"]}<br>Mean Score: {best_types[stats_columns[1]]["mean_value"]}</div>',
            unsafe_allow_html=True)
        fig_violin = create_violin_plot(df, stats_columns[1], best_types[stats_columns[1]]["best_type"], color_theme)
        st.plotly_chart(fig_violin, use_container_width=True)

    with column3:
        # Display the rounded corner box using markdown
        st.markdown("##### Best Special Attack")
        st.markdown(
            f'<div style="{css}">{best_types[stats_columns[2]]["best_type"]}<br>Mean Score: {best_types[stats_columns[2]]["mean_value"]}</div>',
            unsafe_allow_html=True)
        fig_violin = create_violin_plot(df, stats_columns[2], best_types[stats_columns[2]]["best_type"], color_theme)
        st.plotly_chart(fig_violin, use_container_width=True)

    with column4:
        # Display the rounded corner box using markdown
        st.markdown("##### Best Special Defense")
        st.markdown(
            f'<div style="{css}">{best_types[stats_columns[3]]["best_type"]}<br>Mean Score: {best_types[stats_columns[3]]["mean_value"]}</div>',
            unsafe_allow_html=True)
        fig_violin = create_violin_plot(df, stats_columns[3], best_types[stats_columns[3]]["best_type"], color_theme)
        st.plotly_chart(fig_violin, use_container_width=True)

    with column5:
        # Display the rounded corner box using markdown
        st.markdown("##### Best Speed")
        st.markdown(
            f'<div style="{css}">{best_types[stats_columns[4]]["best_type"]}<br>Mean Score: {best_types[stats_columns[4]]["mean_value"]}</div>',
            unsafe_allow_html=True)
        fig_violin = create_violin_plot(df, stats_columns[4], best_types[stats_columns[4]]["best_type"], color_theme)
        st.plotly_chart(fig_violin, use_container_width=True)


if __name__ == "__main__":
    display_tab()
