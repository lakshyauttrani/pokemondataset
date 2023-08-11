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
# from streamlit_extras.add_vertical_space import add_vertical_space
# from streamlit_lottie import st_lottie
import requests
from PIL import Image
from io import BytesIO
import time


with bg_1_2:
    # Load the button image
    button_image_path = "/Users/ksmaurya/Documents/AnalyticonViz/comp_code/Poke_Ball.webp"
    button_image = Image.open(button_image_path)
    # Reduce the image size to improve loading time
    button_image.thumbnail((200, 200))  # Adjust the size as needed


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
    if st.image(button_image, use_column_width=True, caption = "Click to start the battle"):
        ink = "https://pvpoke.com/train/"
