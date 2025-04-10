import streamlit as st
from PIL import Image
import easyocr
from streamlit_drawable_canvas import st_canvas
import requests
from gtts import gTTS
import tempfile
import os

# Your API key and cx values
api_key = "AIzaSyAh3LODrTMO0LZr8rauTPTA9r8il0Cf9uo"
cx = "0713c6f2c87804f82"

def fetch_image_urls(query):
    try:
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": cx,
            "key": api_key,
            "searchType": "image",
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            st.error("Error fetching data from API: " + str(data))
            return []

        image_urls = [item["link"] for item in data.get("items", [])]
        return image_urls
    except Exception as e:
        st.error(f"An error occurred while fetching image URLs: {e}")
        return []

# Function to recognize text from image
def recognize_text(image):
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    result_words = reader.readtext(image)  # Recognize words
    result_chars = reader.readtext(image, detail=0)  
    return result_words, result_chars

# Function to generate speech from recognized text
def generate_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio_path = temp_audio.name
        tts.save(temp_audio_path)
    st.audio(temp_audio_path, format="audio/mp3")
    os.remove(temp_audio_path)

def save_image_to_file(image_data, filename):
    image = Image.fromarray(image_data.astype("uint8")).convert("RGB")
    image.save(filename)

def main():
    st.set_page_config(page_title="HandScribeVoice", page_icon=":pencil2:")
    
    st.title("Canvas Text Recognizer")
    st.sidebar.title("HandScribeVoice")
    st.sidebar.markdown("Draw text on the canvas below and convert it to voice")

    canvas_result = st_canvas(
        fill_color="rgb(255, 255, 255)",
        stroke_width=10,
        stroke_color="rgb(0, 0, 0)",
        background_color="rgb(255, 255, 255)",
        height=300,
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.sidebar.button("Recognize Text", key="recognize_button"):
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data, caption='Drawing', use_column_width=True)
            st.write("Recognizing text...")

            tmp_file_path = "drawn_image.png"
            save_image_to_file(canvas_result.image_data, tmp_file_path)

            result_words, result_chars = recognize_text(tmp_file_path)

            recognized_words = " ".join([text[1] for text in result_words])
            recognized_chars = "".join(result_chars)
            recognized_text = recognized_words if recognized_words else recognized_chars
            st.write("Recognized Text:", recognized_text)
            
            image_urls = fetch_image_urls(recognized_text)
            if image_urls:
                st.image(image_urls[0], width=400)
            else:
                st.error("No image URLs found for the recognized text.")
            
            generate_speech(recognized_text)

if __name__ == "__main__":
    main()
