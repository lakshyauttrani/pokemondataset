import streamlit as st
import pandas as pd
import plotly.express as px


def calculate_best_type(df, stats):
    stats_columns = stats
    best_types = {}

    for stat in stats_columns:
        best_type_idx = df[stat].idxmax()
        best_type = df.loc[best_type_idx, 'type_1']
        mean_value = round(df[stat].mean())
        best_types[stat] = {'best_type': best_type, 'mean_value': mean_value}

    return best_types

#Chart Functions
def create_violin_plot(df, stat, best_type, color_theme):
    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]
    fig_violin = px.violin(df[df['type_1'] == best_type], y=stat, x="type_1", box=True, points="all",  color_discrete_sequence=[color2])
    fig_violin.update_layout(
        title=f"{stat.capitalize()} Distribution for {best_type}",
        xaxis_title="Type 1",
        yaxis_title=stat.capitalize(),
    )
    return fig_violin

def display_tab(df, df2, color_theme):
    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]

    #Row1
    row1_space1, row_1_1, row1_space2, row_1_2, row3_space3 = st.columns(
        (0.005, 1, 0.1, 1, 0.1)
    )

    df2['revenue_billions'] *= 1000
    df_long = pd.melt(df2, id_vars=["year"],
                      value_vars=["revenue_billions", "users_millions", "app_purchases_millions"],
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
            color_discrete_sequence=["#9EE6CF", "#FACF5A", "#F08497"],
        )
        fig_line.update_layout(title_font=dict(size=24),
            legend=dict(x=0, y=1, bgcolor='rgba(255, 255, 255, 0.5)', bordercolor='rgba(0, 0, 0, 0.5)'))  # Move legend to top left corner
        fig_line.update_yaxes(title_text="Value in Millions", tickprefix="$")
        fig_line.for_each_trace(lambda t: t.update(name=t.name.replace("_millions", "").replace("_", " ").title()))
        fig_line.for_each_trace(lambda t: t.update(name=t.name.replace("Billions", "").replace("_", " ").title()))


        st.plotly_chart(fig_line, use_container_width=True)


        description1 = """
        <div style="font-size: 18px; line-height: 1.6; color: #333;">
            <p style="margin-bottom: 16px;">Delve into the captivating financial odyssey of Pokémon GO as we unveil its remarkable journey through the years. From its inception in <strong>2016</strong>, where it garnered an enthusiastic player base of <strong>232 million</strong>, the game's popularity skyrocketed to new heights, amassing a staggering <strong style="color: red; font-weight: bold;">$830 million</strong> in revenue. This extraordinary ascent continued, with <strong>2017</strong> marking a player base of <strong>65 million</strong> and <strong style="color: red; font-weight: bold;">$580 million</strong> in revenue. The enchantment only deepened in <strong>2018</strong>, with <strong>133 million</strong> players embracing the immersive experience, resulting in <strong style="color: red; font-weight: bold;">$810 million</strong> in revenue.</p>
        </div>
        """

        description2 = """
        <div style="font-size: 18px; line-height: 1.6; color: #333;">
            <p style="margin-bottom: 16px;">As we traverse further into the virtual realm, <strong>2019</strong> unveiled a community of <strong>113 million</strong> devoted trainers, contributing to an impressive <strong style="color: red; font-weight: bold;">$890 million</strong> in revenue. Even amidst the challenges of <strong>2020</strong>, the game retained its allure, captivating <strong>86 million</strong> players and achieving an astounding <strong style="color: red; font-weight: bold;">$1.23 billion</strong> in revenue. As we venture into the latest chapter of this enthralling saga, <strong>2021</strong> saw a dedicated <strong>71 million</strong> players, culminating in a staggering <strong style="color: red; font-weight: bold;">$1.21 billion</strong> in revenue.</p>
        </div>
        """

        description3 = """
                <div style="font-size: 18px; line-height: 1.6; color: #333;">
                    <p style="margin-bottom: 16px;">This financial odyssey, underscored by the passion of millions of trainers worldwide, has solidified Pokémon GO as an iconic phenomenon in the realm of augmented reality gaming. As each year unfolds, the game continues to captivate hearts, ignite imaginations, and generate awe-inspiring revenue figures, standing as a testament to the enduring magic of the Pokémon universe.</p>
                </div>
        """

        st.write(description1, unsafe_allow_html=True)
        st.write(description2, unsafe_allow_html=True)
        st.write(description3, unsafe_allow_html=True)

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
            color_discrete_sequence=[color2],  # You can change the area color here
        )
        st.plotly_chart(fig_area, use_container_width=True)

    #Row2
    row2_space1, row_2_1, row2_space2, row_2_2, row2_space3 = st.columns(
        (0.005, 1, 0.1, 1, 0.1)
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
            color_discrete_sequence=[color3],
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
            color_discrete_sequence=[color4],
        )
        st.plotly_chart(fig_gen, use_container_width=True)

    #Row3
    column1_space, column1, column2_space, column2, column3_space, column3, column4_space, column4, column5_space, column5, column6_space = st.columns(
        (0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1)
    )

    # Calculations for Abilities
    stats_columns = ['attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
    best_types = calculate_best_type(df, stats_columns)

    # Define the custom color (e.g., blue) using hexadecimal code
    custom_color = color5

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
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"], color_theme)
            st.plotly_chart(fig_violin, use_container_width=True)

    with column2:
        for stat in stats_columns[1:2]:  # Last three stats
            st.markdown("##### Best Defense")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"], color_theme)
            st.plotly_chart(fig_violin, use_container_width=True)

    with column3:
        for stat in stats_columns[2:3]:  # First two stats
            st.markdown("##### Best Special Attack")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"], color_theme)
            st.plotly_chart(fig_violin, use_container_width=True)

    with column4:
        for stat in stats_columns[3:4]:  # Last three stats
            st.markdown("##### Best Special Defense")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"], color_theme)
            st.plotly_chart(fig_violin, use_container_width=True)

    with column5:
        for stat in stats_columns[4:5]:  # Last three stats
            st.markdown("##### Best Speed")
            st.markdown(
                f'<div style="{css}">{best_types[stat]["best_type"]}<br>Mean Score: {best_types[stat]["mean_value"]}</div>',
                unsafe_allow_html=True)
            fig_violin = create_violin_plot(df, stat, best_types[stat]["best_type"], color_theme)
            st.plotly_chart(fig_violin, use_container_width=True)

if __name__ == "__main__":
    display_tab()
