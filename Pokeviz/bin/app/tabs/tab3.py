import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

def display_tab(df, df2, color_theme):

    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]

    # Data for the first graph - Scatter plot
    data_1 = df  

    # Data for the second graph - Bar plot
    categories = df['generation'].unique()
    values = df['generation'].value_counts().sort_index()
    bar_data = pd.DataFrame({"Generation": categories, "Count": values})

    # Data for the third graph - Area chart
    data_2 = df.sample(10)  # Sample 10 random Pokemon for illustration

    # Data for the fourth graph - Scatter plot with regression line
    x = df['attack']
    y = df['defense']

    # Data for the fifth graph - Scatter chart
    data_3 = df.sample(50)  # Sample 50 random Pokemon for illustration

    # Create a layout with 2 rows and 3 columns

    row1_space1, col1, row1_space2, col2, row1_space3 = st.columns((0.005, 1, 0.1, 1, 0.1))  # Two columns in the first row
    row2_space1, col3, row2_space2, col4, row2_space3 = st.columns((0.005, 1, 0.1, 1, 0.1))  # Two columns in the second row
    row3_space1, col5, row3_space2, col6, row3_space3 = st.columns((0.005, 1, 0.1, 1, 0.1))  # Two columns in the third row

    col5 = st.columns(1)  # Single column in the third row

    # First row, first graph: Scatter plot
    with col1:
        # Create a Plotly scatter plot
        if color1 == "#FF6F00":
            color = 'reds'
        elif color1 == "#00b4d8":
            color = 'teal'
        elif color1 == "#8BC34A":
            color = 'greens'
        elif color1 == "#8B4513":
            color = 'earth'
        else :
            color = 'red'

        fig = px.scatter(data_1, x='attack', y='defense', color='generation', color_continuous_scale=color,
                         title="Attack vs Defense of Pokemon",
                         labels={'attack': 'Attack', 'defense': 'Defense', 'name': 'Name'},
                         hover_data=["name", "attack", "defense", "generation"], 
                         width=800, height=600)  # Adjust size of the plot

        # Customize the plot appearance
        fig.update_layout(
            title="Attack vs Defense of Pokemon",
            title_font=dict(size=28),  # Adjust title font size
            xaxis_title="Attack",
            yaxis_title="Defense",
            showlegend=True,
            legend=dict(
                x=0.85,
                y=0.95,
                title="Generation",
                font=dict(size=10)  # Adjust legend font size
            ),
            coloraxis_colorbar=dict(
                title='Generation',  # Colorbar title
                tickvals=[1, 2, 3, 4, 5, 6, 7, 8],  # Adjust tick values
                ticktext=['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7', 'Gen 8'],  # Adjust tick labels
                lenmode="pixels", len=300,  # Adjust colorbar length
                thicknessmode="pixels", thickness=20,  # Adjust colorbar thickness
                yanchor="middle", y=0.5  # Adjust colorbar vertical position
            )
        )

        # Display the Plotly figure using st.plotly_chart()
        st.plotly_chart(fig, use_container_width=True)


        description = """
                 <div style="font-size: 22px; line-height: 1.6; ">
                     <p style="margin-bottom: 16px;">The scatter plot captures the interplay between a Pokémon's attack and defense attributes across generations. Color-coded by generation, this dynamic visualization helps identify trends and variations. It’s interesting to see most outliers are from first generations, for example, Shuckle (Gen 2) stands out with an exceptional defense stat of 230, while Mega Heracross (Gen 2) showcases an unusually high attack stat of 185.
                     </p></div>
                 """

        st.write(description, unsafe_allow_html=True)

    # First row, second graph: Bar plot
    with col2:
        st.subheader("")
        st.markdown("<div style='font-size: 28px; font-weight: bold; text-align: left;'>Distribution of Pokemon across Generations</div>", unsafe_allow_html=True)





        st.subheader("")

        color_map = color1

        fig = px.bar(bar_data, x="Generation", y="Count", color="Generation")

        # Customize the color of the chart using the color_map
        fig.update_traces(marker=dict(color=color_map))

        # Customize the size of the chart and title
        fig.update_layout(
            width=800,  # Set the width of the chart
            height=500,  # Set the height of the chart
            title="",  # Set the title
            title_font=dict(size=28),  # Adjust title font size
            coloraxis_colorbar=dict(
                title='Generation',  # Colorbar title
                tickvals=[1, 2, 3, 4, 5, 6, 7, 8],  # Adjust tick values
                ticktext=['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7', 'Gen 8'],  # Adjust tick labels
                lenmode="pixels", len=300,  # Adjust colorbar length
                thicknessmode="pixels", thickness=20,  # Adjust colorbar thickness
                yanchor="middle", y=0.5  # Adjust colorbar vertical position
            )
        )

        # Display the Plotly figure using st.plotly_chart()
        st.plotly_chart(fig, use_container_width=True)

        description = """
                         <div style="font-size: 22px; line-height: 1.6; ">
                             <p style="margin-bottom: 16px;">The bar chart depicts the distribution of Pokémon across generations, where each bar's color corresponds to a specific generation. It seems that the peak of Pokémon breeding occurred right at the beginning, with 192 new Pokémon hatching from the first generation.
                             </p></div>
                         """

        st.write(description, unsafe_allow_html=True)

        # Second row, first graph: Area chart
    with col3:

        def cat_total_points(row):
            if row.total_points < 300:
                return 'Weakest'
            elif (row.total_points >= 300) & (row.total_points < 600):
                return 'Intermediate'
            else:
                return 'Strong'

        st.subheader("")
        st.subheader("")

        # Create bins on total_points column
        df['cat_total_points'] = df.apply(cat_total_points, axis='columns')

        data_to_consider = df[['hp', 'attack', 'defense', 'total_points', 'cat_total_points']].copy()

        # Drop rows with any missing values
        data_to_consider = data_to_consider.dropna()

        fig = px.scatter_ternary(data_to_consider,
                                 a="hp",
                                 b="attack",
                                 c="defense",
                                 color="cat_total_points",
                                 color_discrete_map={
                                     'Weakest': color1,
                                     'Intermediate': color2,
                                     'Strong': color3
                                 },
                                 size="total_points",
                                 size_max=14)

        fig.update_layout(
            title="Ternary Plot of Pokemon Attributes",
            title_font=dict(size=28),
            ternary=dict(
                aaxis_title="HP",
                baxis_title="Attack",
                caxis_title="Defense"
            ),
            width=800,  # Adjust the width of the plot
            height=600, # Adjust the height of the plot,
             legend_title_text='Total  Points'
        )

        st.plotly_chart(fig, use_container_width=True)

        description1 = """
         <div style="font-size: 22px; line-height: 1.6; ">
             <p style="margin-bottom: 16px;">The ternary plot visualizes Pokemon attributes based on health points (HP), attack, and defense. Notably, Pokemon categorized as 'Strong' gather around the center of the plot, indicating a balanced distribution of their offensive and defensive capabilities. On the other hand, 'Weakest' Pokemon tend to cluster near the edges, implying a focus on specific attributes rather than balance.
             </p></div>
         """


        st.write(description1, unsafe_allow_html=True)







    with col4:
        st.subheader("")
        df2 = df[['generation','total_points', 'hp', 'attack', 'defense']]
        per_gen_pokemon = df2.groupby('generation').mean()[['total_points', 'hp', 'attack', 'defense']]
        

        df3 = df[['generation','total_points', 'hp', 'attack', 'defense', 'status']]
        # Calculate the number of non-normal status Pokémon per generation
        legendary_counts = df3[df3['status'] != 'Normal'].groupby('generation')['status'].count()

        # Scale down the legendary counts for better visualization
        scaled_legendary_counts = legendary_counts * 15

        fig = go.Figure()
        fig.add_trace(go.Bar(x=per_gen_pokemon.index, y=per_gen_pokemon['hp'],
                             name='Health Points', marker_color=color1))
        fig.add_trace(go.Bar(x=per_gen_pokemon.index, y=per_gen_pokemon['defense'],
                             name='Defense', marker_color=color2))
        fig.add_trace(go.Bar(x=per_gen_pokemon.index, y=per_gen_pokemon['attack'],
                             name='Attack', marker_color=color3))
        fig.add_trace(go.Bar(x=per_gen_pokemon.index, y=per_gen_pokemon['total_points'],
                             name='Total Points', marker_color=color4))
        fig.update_layout(barmode='stack', title='Generation-wise Aggregated Characteristic Stat Comparison',
                          title_font=dict(size=28),
                          height=620
                          )
        # Adding a line for the number of legendary Pokémon
        fig.add_trace(go.Scatter(x=legendary_counts.index, y=scaled_legendary_counts.values,
                         mode='lines+markers', name='Special Pokémons',
                         line=dict(color='#333333', width=3),
                         customdata=legendary_counts.values,
                         hovertemplate=' %{customdata} Special Pokémons')) 

        # Display the Plotly figure using st.plotly_chart()
        st.plotly_chart(fig, use_container_width=True)

        description1 = f"""
             <div style="font-size: 22px; line-height: 1.6; ">
                 <p style="margin-bottom: 16px;">If we consider Pokémon base points as a primary indicator of their overall strength, the seventh generation emerges as the most powerful. This observation could be attributed to the presence of 30 special Pokémon within this generation. The graph depicts a comparison between the ranking of total points across generations and the count of special Pokémon within each generation.
                 </p></div>
             """

        st.write(description1, unsafe_allow_html=True)




if __name__ == "__main__":
    display_tab()



