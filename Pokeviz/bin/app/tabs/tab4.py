import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px


def display_tab(df, df2, color_theme):
    row3_space1, row_3_1, row3_space2, row_3_2, row3_space3 = st.columns(
        (0.1, 1, 0.1, 1, 0.1)
    )

    # Filter by Generation
    selected_type_2 = row_3_1.selectbox("Select a Type", df["type_1"].unique())

    # Filter by Type based on selected Generation
    filtered_df_by_type = df[df["type_1"] == selected_type_2]

    with row_3_1:

        # Define a color map for the lines
        color_map = {
            'attack': '#FF0000',
            'defense': '#CC0000',
            'sp_attack': '#3B4CCA',
            'sp_defense': '#FFDE00'
        }

        # Group by generation and calculate mean values
        attributes = ['attack', 'defense', 'sp_attack', 'sp_defense']
        grouped = filtered_df_by_type.groupby('generation')[attributes].mean()

        # Create a line chart using Plotly Express
        fig = px.line(grouped, x=grouped.index, y=attributes,
                      labels={'index': 'Generation', 'value': 'Mean Value of power'}, color_discrete_map=color_map)

        # Streamlit app
        st.title(selected_type_2 + ' powers across generations')

        # Display the line chart using Plotly Express
        st.plotly_chart(fig)

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
        custom_color_scale = [(0.0, '#FFD0D0'), (1.0, '#FF0000')]  # Blue to Red

        # Create a heatmap using Plotly Express
        fig = px.imshow(mean_normalized_effectiveness.pivot(index='Attacking Type', columns='Defending Type',
                                                            values='Mean Normalized Effectiveness'),
                        x=types, y=types, labels=dict(x="Defending Type", y="Attacking Type"),
                        color_continuous_scale=custom_color_scale)  # Use the custom color scale here

        # Streamlit app
        st.title('Find the power of ' + selected_type_2 + ' against other types')

        # Display the heatmap using Plotly Express
        st.plotly_chart(fig)

    row3_space4, row_3_4, row3_space5, row_3_5, row3_space6 = st.columns(
        (0.1, 1, 0.1, 1, 0.1)
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
        color_palette = ['#FF0000', '#3B4CCA', '#CC0000', '#FFDE00']

        # Create a stacked bar chart using Plotly Express with the custom color palette
        fig = px.bar(mean_values_melted, x='type_1', y='Mean Value', color='Attribute',
                     title='Mean Attribute Values per Type_1',
                     labels={'type_1': 'Type', 'Mean Value': 'Mean Value', 'Attribute': 'Attribute'},
                     color_discrete_sequence=color_palette,  # Use the custom color palette
                     barmode='stack')

        # Streamlit app
        st.title('Compare the abilities of ' + selected_type_2 + ' against other types')

        # Display the stacked bar chart using Plotly Express
        st.plotly_chart(fig)

    with row_3_5:

        # Select attributes for the star chart
        attributes = ['attack', 'defense', 'sp_attack', 'sp_defense']

        # Create a color map for different statuses
        color_map = {
            'status1': '#B3A125',
            'status2': '#FF0000',
            'status3': '#3B4CCA'
            # Add more colors and status values as needed
        }

        # Create a DataFrame for each attribute and merge them
        data_frames = []
        for attr in attributes:
            df_attr = df_against_type[['type_1', 'status', attr]].copy()
            df_attr.rename(columns={attr: 'value'}, inplace=True)
            df_attr['attribute'] = attr
            data_frames.append(df_attr)

        merged_df = pd.concat(data_frames)

        # Create a star chart using Plotly Express
        fig = px.line_polar(merged_df, r='value', theta='attribute', line_close=True,
                            color='status', color_discrete_map=color_map,
                            title='Attributes Comparison for Selected Types')

        # Customize the layout with transparent background and hidden radial axis labels
        fig.update_layout(
            polar_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
            polar_radialaxis_ticksuffix='',  # Remove suffix from radial axis ticks
            showlegend=True,
            polar_radialaxis_showticklabels=False  # Hide radial axis labels
        )

        # Streamlit app
        st.title('Attributes Comparison for Selected Types')

        # Display the star chart using Plotly Express
        st.plotly_chart(fig)

if __name__ == "__main__":
    display_tab()