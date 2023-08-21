import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def display_tab(df, df2, color_theme):

    # Data for the first graph - Scatter plot
    data_1 = df  # Sample 10 random Pokemon for illustration

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
        fig = px.scatter(data_1, x='attack', y='defense', color='generation', color_continuous_scale='sunset',
                         title="Attack vs Defense of Pokemon",
                         labels={'attack': 'Attack', 'defense': 'Defense'},
                         width=800, height=600)  # Adjust size of the plot
        # Customize the plot appearance
        fig.update_layout(
            title="Attack vs Defense of Pokemon",
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
        st.plotly_chart(fig)

        narrative = """
        <div style="font-size: 18px; line-height: 1.6; color: #333;">
            <p style="margin-bottom: 16px;">Step into the <strong>captivating</strong> world of <strong>Pokémon</strong>, where each creature boasts <strong>unique</strong> strengths and defenses. The scatter plot above <strong>showcases</strong> the <strong>dynamic interplay</strong> between a Pokémon's <strong>attack</strong> and <strong>defense stats</strong>, with each point representing a <strong>randomly selected</strong> creature from various generations. The <strong>vibrant hues</strong> depict the <strong>generation</strong> of each Pokémon, adding a touch of <strong>visual delight</strong>.</p>
            <p style="margin-bottom: 16px;">As we <strong>navigate through</strong> this <strong>enchanting realm</strong>, it's <strong>fascinating</strong> to <strong>observe</strong> the <strong>wide range</strong> of <strong>attack</strong> and <strong>defense values</strong> exhibited by different species. From the <strong>formidable</strong> to the <strong>nimble</strong>, the plot offers a <strong>glimpse into the diverse attributes</strong> that trainers consider when <strong>crafting their teams and strategies</strong>.</p>
            <p style="margin-bottom: 16px;">Whether it's the <strong>powerhouse punches</strong> of <strong>Machamp</strong> or the <strong>steadfast defenses</strong> of <strong>Steelix</strong>, each Pokémon contributes a <strong>unique flavor</strong> to battles and adventures. So, <strong>venture forth</strong> and <strong>uncover the secrets</strong> behind these <strong>statistical nuances</strong>, and <strong>embrace the journey</strong> of <strong>becoming a Pokémon Master</strong>.</p>
        </div>
        """

        st.write(narrative, unsafe_allow_html=True)
        st.header("")

    # First row, second graph: Bar plot
    with col2:
        st.subheader("")
        st.write("**Distribution of Pokemon across generations.**")

        # Create a Plotly bar chart
        fig = px.bar(bar_data, x="Generation", y="Count", color="Generation")

        # Customize the size and color of the chart
        fig.update_layout(
            width=800,  # Set the width of the chart
            height=500,  # Set the height of the chart
            colorway=['#FFDB01', '#FFA900', '#FF6F00', '#FF3D00', '#DD2C00', '#A30000', '#4A148C', '#0D47A1'],
            coloraxis_colorbar=dict(
                title='Generation',  # Colorbar title
                tickvals=[1, 2, 3, 4, 5, 6, 7, 8],  # Adjust tick values
                ticktext=['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7', 'Gen 8'],  # Adjust tick labels
                lenmode="pixels", len=300,  # Adjust colorbar length
                thicknessmode="pixels", thickness=20,  # Adjust colorbar thickness
                yanchor="middle", y=0.5  # Adjust colorbar vertical position
            )
            # Set custom color palette
        )

        # Display the Plotly figure using st.plotly_chart()
        st.plotly_chart(fig)

        description = """
        <div style="font-size: 18px; line-height: 1.6; color: #333;">
            <p style="margin-bottom: 16px;">Embark on a journey through the diverse generations of Pokémon, each contributing its unique charm and captivating millions of trainers worldwide.
            Beginning with the <strong style="color: red; font-weight: bold;">first generation</strong>, which introduced us to the enchanting world of Pokémon in <strong>1996</strong>, the franchise has since grown to encompass a total of <strong>8 generations</strong>, each bringing forth a plethora of new species and adventures.
            As we traverse through the years, witness the evolution of Pokémon designs, types, and abilities. Notably, the <strong>third generation</strong> marked a milestone with <strong>135 new species</strong> and the introduction of abilities, enhancing battle strategies and adding depth to gameplay.</p>
            <p style="margin-bottom: 16px;">The allure of Pokémon continued to thrive, and by the time the <strong>seventh generation</strong> arrived, trainers were introduced to the captivating region of Alola, along with <strong>81 new species</strong> to discover.
            In the most recent <strong>eighth generation</strong>, set in the remarkable Galar region, trainers embraced a total of <strong>89 new species</strong>, embarking on new quests and forming bonds with these awe-inspiring creatures.
            As the Pokémon saga unfolds across generations, one thing remains certain—the enduring magic and unbreakable bond between trainers and their Pokémon.</p>
        </div>
        """
        st.header("")
        st.write(description, unsafe_allow_html=True)
        st.header("")

        # Second row, first graph: Area chart
    with col3:
        st.subheader("Random Pokemon Abilities")
        st.write("Discover the abilities of randomly selected Pokemon.")
        data_2_long = data_2[['ability_1', 'ability_2', 'ability_hidden']].melt(var_name='ability_type',
                                                                                value_name='ability')

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot using Seaborn lineplot
        sns.lineplot(data=data_2_long, x='ability_type', y='ability', palette='viridis', ax=ax)

        # Display the Matplotlib figure using st.pyplot()

        st.pyplot(fig)

    # Second row, second graph: Scatter plot with regression line
    with col4:
        st.subheader("Attack vs. Defense")
        st.write("Examining the relationship between attack and defense stats.")
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=x, y=y, color='blue')
        sns.regplot(x=x, y=y, ci=None, line_kws={"color": "red"})
        st.pyplot()

    # Third row: Scatter chart





if __name__ == "__main__":
    display_tab()



