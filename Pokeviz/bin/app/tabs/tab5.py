import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import plotly.express as px
import base64

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def display_tab(df, df2, color_theme):
    st.markdown("")
    st.markdown(
        "<div style='text-align: left; font-size: 30px; font-weight: bold; color: grey;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Happy to connect on LinkedIn :)</div>",
        unsafe_allow_html=True
    )


    rs1, r1, rs2,r2,rs3,r3,rs4, r4,r5 = st.columns((0.1,1,0.1,1,0.1,1,0.1, 5,0.1) )



    with r1:

        ksmaurya_image_path = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/images/ksmaurya.png"
        ksmaurya_image = Image.open(ksmaurya_image_path)
        # Reduce the image size to improve loading time
        ksmaurya_image.thumbnail((1000, 1000))  # Adjust the size as needed
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        image_width = 300  # Adjust the width as needed
        ksmaurya_url = "https://phonetool.amazon.com/users/ksmaurya"
        ksmaurya_linkedin = "https://www.linkedin.com/in/krishnamaurya95/"
        st.markdown(
            f"<a href='{ksmaurya_url}'><img src='data:image/png;justify-content: center; base64,{image_to_base64(ksmaurya_image)}' alt='ksmaurya' style='width: 100%; max-width: {image_width}px;'></a>",
            unsafe_allow_html=True)

        st.markdown(
            f"<p style='text-align: left; font-size: 1.20vw; font-weight: bold; margin-bottom: 5px;'>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<a href='{ksmaurya_linkedin}' style='color: inherit; text-decoration: none;'>Data Engineer</a>"
            f"</p>",
            unsafe_allow_html=True
        )



    with r2:

        caclopes_image_path = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/images/caclopes.png"
        caclopes_image = Image.open(caclopes_image_path)
        # Reduce the image size to improve loading time
        caclopes_image.thumbnail((1000, 1000))  # Adjust the size as needed
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        image_width = 300  # Adjust the width as needed
        caclopes_url = "https://phonetool.amazon.com/users/caclopes"
        caclopes_linkedin = "https://www.linkedin.com/in/carlota-lopes-dias/"
        st.markdown(
            f"<a href='{caclopes_url}'><img src='data:image/png;base64,{image_to_base64(caclopes_image)}' alt='caclopes' style='width: 100%; max-width: {image_width}px;'></a>",
            unsafe_allow_html=True)


        st.markdown(
            f"<p style='text-align: left; font-size: 1.20vw; font-weight: bold; margin-bottom: 5px;'>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<a href='{caclopes_linkedin}' style='color: inherit; text-decoration: none;'>BIE</a>"
            f"</p>",
            unsafe_allow_html=True
        )

    with r3:

        lakshutt_image_path = "/Users/ksmaurya/Documents/AnalyticonViz/Pokeviz/bin/images/lakshutt.png"
        lakshutt_image = Image.open(lakshutt_image_path)
        # Reduce the image size to improve loading time
        lakshutt_image.thumbnail((1000, 1000))  # Adjust the size as needed
        st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        image_width = 300  # Adjust the width as needed
        lakshutt_url = "https://phonetool.amazon.com/users/lakshutt"
        lakshutt_linkedin = "https://www.linkedin.com/in/lakshyauttrani/"
        st.markdown(
            f"<a href='{lakshutt_url}'><img src='data:image/png;base64,{image_to_base64(lakshutt_image)}' alt='lakshutt' style='width: 100%; max-width: {image_width}px;'></a>",
            unsafe_allow_html=True)

        st.markdown(
            f"<p style='text-align: left; font-size: 1.20vw; font-weight: bold; margin-bottom: 5px;'>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<a href='{lakshutt_linkedin}' style='color: inherit; text-decoration: none;'>Data Scientist</a>"
            f"</p>",
            unsafe_allow_html=True
        )



if __name__ == "__main__":

    display_tab()