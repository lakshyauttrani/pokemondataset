import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px


def lighten_color(hex_color, factor=0.8):
    # Convert hexadecimal color to RGB
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    # Calculate new RGB values for the lighter color
    new_r = min(255, int(r + (255 - r) * factor))
    new_g = min(255, int(g + (255 - g) * factor))
    new_b = min(255, int(b + (255 - b) * factor))

    # Convert new RGB values to hexadecimal format
    new_hex_color = "#{:02X}{:02X}{:02X}".format(new_r, new_g, new_b)

    return new_hex_color


def display_tab(df, df2, color_theme):
    
    description1 = """
         <div style="font-size: 22px; line-height: 1.6; ">
             <p style="margin-bottom: 16px;">Pokémons come in all different types, each type with its strengths and weaknesses. Choose the perfect type for you, analyse its strengths and see how it compares to other types. Good luck on your future battles!
             </p></div>
         """


    st.write(description1, unsafe_allow_html=True)

    
    row3_space1, row_3_1, row3_space2, row_3_2, row3_space3 = st.columns(
        (0.001, 1, 0.1, 1, 0.1)
    )

    # Filter by Generation
    selected_type_2 = row_3_1.selectbox("Select a Type", df["type_1"].unique())

    # Filter by Type based on selected Generation
    filtered_df_by_type = df[df["type_1"] == selected_type_2]

    color1 = color_theme[0]
    color2 = color_theme[1]
    color3 = color_theme[2]
    color4 = color_theme[3]
    color5 = color_theme[4]

    
    
    
    with row_3_1:

        # Define a color map for the lines
        color_map = {
            'attack': color1,
            'defense': color5,
            'sp_attack': color3,
            'sp_defense': color4
        }

        # Group by generation and calculate mean values
        attributes = ['attack', 'defense', 'sp_attack', 'sp_defense']
        grouped = filtered_df_by_type.groupby('generation')[attributes].mean()

        # Create a line chart using Plotly Express
        fig = px.line(grouped, x=grouped.index, y=attributes,
                      labels={'index': 'Generations', 'value': 'Mean Value of power', 'generation': 'Generations',
                              'attack': 'Attack'},
                      color_discrete_map=color_map,
                      title=selected_type_2 + ' Powers Across Generations')

        fig.update_layout(title_font=dict(size=30),
                          legend_title_text='Powers',
                          #margin=dict(t=100, b=100, l=100, r=10),  # Adjust these values to control the margins
                            autosize=True,
                              )

        # Display the line chart using Plotly Express
        st.plotly_chart(fig, use_container_width=True)

    # Default value for multiselect
    default_selected_type = ["Fire"]

    # Filter by Generation
    selected_type_3 = row_3_2.multiselect("Select the types you want to fight", df["type_1"].unique(),
                                          default=default_selected_type)

    # Combine selected_type_3 with selected_type_2
    combined_selected_types = [selected_type_2] + selected_type_3

    # Filter by Type based on selected Generation
    df_against_type = df[df["type_1"].isin(combined_selected_types)]




    with row_3_2:
        # Select attributes for the star chart
        attributes = ['attack', 'defense', 'sp_attack', 'sp_defense', "hp"]

        # Create an empty list to store data for the star chart
        star_chart_data = []

        # Iterate through each status
        for status in filtered_df_by_type['status'].unique():
            # Subset the DataFrame for the current status
            subset_df = filtered_df_by_type[filtered_df_by_type['status'] == status]

            # Calculate the mean value for each attribute and store it in the star chart data
            for attr in attributes:
                mean_value = subset_df[attr].mean()  # Calculate the mean value
                star_chart_data.append({'status': status, 'attribute': attr, 'value': mean_value})

        # Create a DataFrame from the star chart data
        star_chart_df = pd.DataFrame(star_chart_data)

        color_map2 = {
            'Normal': color1,
            'Mythical': color5,
            'Legendary': color3,
            'Sub Legendary': color4,
            # Add more colors and status values as needed
        }
        # Create a star chart using Plotly Express
        fig = px.line_polar(star_chart_df, r='value', theta='attribute', line_close=True,
                            color='status', color_discrete_map=color_map2,
                            labels={'index': 'Generations', 'value': 'Mean Value of power',
                                    'generation': 'Generations'},
                            title='Powers of ' + selected_type_2 + ' Across Levels of Rarity')

        fig.update_layout(title_font=dict(size=30),
                          legend_title_text='Rarity')
        fig.update_traces(fill="toself")

        # Customize the layout with transparent background and hidden radial axis labels
        fig.update_layout(
            polar=dict(
                radialaxis=dict(showticklabels=False, ticksuffix="%", showline=False),
                angularaxis=dict(showticklabels=True, linecolor="gray"),
            ),
            showlegend=True,  # Display legend
            legend=dict(x=0.9, y=0.9),  # Adjust legend position
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
        

        )

        # Display radar chart
        st.plotly_chart(fig, use_container_width=True)

    row3_space4, row_3_4, row3_space5, row_3_5, row3_space6 = st.columns(
        (0.001, 1, 0.1, 1, 0.1)
    )
    with row_3_4:

        # Calculate mean values of attributes for each type_1
        mean_attack = df_against_type.groupby('type_1')['attack'].mean().reset_index()
        mean_defense = df_against_type.groupby('type_1')['defense'].mean().reset_index()
        mean_sp_attack = df_against_type.groupby('type_1')['sp_attack'].mean().reset_index()
        mean_sp_defense = df_against_type.groupby('type_1')['sp_defense'].mean().reset_index()

        # Merge the mean values for different attributes
        mean_values = mean_attack.merge(mean_defense, on='type_1')
        mean_values = mean_values.merge(mean_sp_attack, on='type_1')
        mean_values = mean_values.merge(mean_sp_defense, on='type_1')

        # Convert selected type to lowercase for matching
        selected_type_2_lower = selected_type_2.lower()

        # Sort the DataFrame, placing selected_type_2 as the first row
        sorted_values = mean_values.sort_values(by='type_1', key=lambda x: x == selected_type_2_lower, ascending=False)

        # Melt the DataFrame to have a single 'Attribute' column
        mean_values_melted = sorted_values.melt(id_vars='type_1', var_name='Attribute', value_name='Mean Value')

        # Define the custom color palette
        color_palette = [color1, color2, color3, color4]

        # Create a stacked bar chart using Plotly Express with the custom color palette
        fig = px.bar(mean_values_melted, x='type_1', y='Mean Value', color='Attribute',
                     title='Compare the abilities of ' + selected_type_2 + ' Against other types',
                     labels={'type_1': 'Type of Pokémon', 'Mean Value': 'Mean Value', 'Attribute': 'Attribute'},
                     color_discrete_sequence=color_palette,  # Use the custom color palette
                     barmode='stack')

        fig.update_layout(title_font=dict(size=30),
                          legend_title_text='Powers')
        # Display the stacked bar chart using Plotly Express
        st.plotly_chart(fig, use_container_width=True)

    with row_3_5:

        # Preprocessing: convert type columns to lowercase
        df_against_type['type_1'] = df_against_type['type_1'].str.lower()
        # filtered_df_by_type['type_1'] = filtered_df_by_type['type_1'].str.lower()

        # Rename the column 'against_fight' to 'against_fighting'
        df_against_type.rename(columns={'against_fight': 'against_fighting'}, inplace=True)

        # Convert the unique values from the 'type_1' column of filtered_df_by_type to lowercase
        filtered_type_1_lower = [t.lower() for t in filtered_df_by_type['type_1'].unique()]

        # Get unique values from the 'type_1' column of df_against_type and concatenate them with the lowercase values
        types = list(df_against_type['type_1'].unique()) + filtered_type_1_lower

        # Remove duplicates by converting to a set and then back to a list
        types = list(set(types))

        mean_normalized_effectiveness = pd.DataFrame(index=types, columns=types)

        for attacking_type in types:
            for defending_type in types:
                if attacking_type == defending_type:
                    mean_normalized_effectiveness.at[attacking_type, defending_type] = 1.0
                else:
                    min_value = df_against_type[df_against_type['type_1'] == attacking_type][
                        'against_' + defending_type].min()
                    max_value = df_against_type[df_against_type['type_1'] == attacking_type][
                        'against_' + defending_type].max()
                    normalized_values = (df_against_type[df_against_type['type_1'] == attacking_type][
                                             'against_' + defending_type] - min_value) / (max_value - min_value)
                    mean_normalized_effectiveness.at[attacking_type, defending_type] = normalized_values.mean()

        # Reset index and columns to type names
        mean_normalized_effectiveness = mean_normalized_effectiveness.rename_axis('Attacking Type').reset_index()
        mean_normalized_effectiveness = mean_normalized_effectiveness.melt(id_vars='Attacking Type',
                                                                           var_name='Defending Type',
                                                                           value_name='Mean Normalized Effectiveness')

        # Define a custom color scale
        custom_color_scale = [(0.0, lighten_color(color1)), (1.0, color1)]  # Blue to Red

        # Create a heatmap using Plotly Express
        fig = px.imshow(mean_normalized_effectiveness.pivot(index='Attacking Type', columns='Defending Type',
                                                            values='Mean Normalized Effectiveness'),
                        x=types, y=types, labels=dict(x="Defending Type", y="Attacking Type"),
                        color_continuous_scale=custom_color_scale,
                        title='Find the power of ' + selected_type_2 + ' Against Other Types'
                        )  # Use the custom color scale here

        fig.update_layout(title_font=dict(size=30),
                          legend_title_text='Powers')
        # Display the heatmap using Plotly Express
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    display_tab()