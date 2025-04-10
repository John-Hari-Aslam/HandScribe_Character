import streamlit as st
from PIL import Image
import easyocr
import pyttsx3
from streamlit_drawable_canvas import st_canvas
import requests

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

        # Log the response for debugging
        print("API Response:", data)

        if response.status_code != 200:
            st.error("Error fetching data from API: " + str(data))
            return []

        # Extract image URLs from the response
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
def generate_speech(text, gender='female'):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if gender == 'male':
        engine.setProperty('voice', voices[0].id)  # Select male voice
    else:
        engine.setProperty('voice', voices[1].id)  # Select female voice
    engine.say(text)
    engine.runAndWait()

def save_image_to_file(image_data, filename):
    image = Image.fromarray(image_data.astype("uint8")).convert("RGB")
    image.save(filename)

def main():
    st.set_page_config(page_title="HandScribeVoice", page_icon=":pencil2:")
    
    # Custom CSS styles
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content .block-container {
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content .block-container .stButton>button {
            width: 100%;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            margin-top: 10px;
        }
        .sidebar .sidebar-content .block-container .stButton>button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Canvas Text Recognizer")

    # Draw on canvas
    st.sidebar.title("HandScribeVoice")
    st.sidebar.markdown("Draw a text on the canvas below and convert it to voice")
    canvas_result = st_canvas(
        fill_color="rgb(255, 255, 255)",  # Fixed fill color with white
        stroke_width=10,
        stroke_color="rgb(0, 0, 0)",
        background_color="rgb(255, 255, 255)",
        height=300,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Select voice gender
    voice_gender = st.sidebar.radio("Select Voice Gender", ("Male", "Female"))

    # Button to recognize text
    if st.sidebar.button("Recognize Text", key="recognize_button"):
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data, caption='Drawing', use_column_width=True)
            st.write("Recognizing text...")

            # Save the drawn image to a temporary file
            tmp_file_path = "drawn_image.png"
            save_image_to_file(canvas_result.image_data, tmp_file_path)

            # Read the image using easyocr
            result_words, result_chars = recognize_text(tmp_file_path)

            # Process recognized words
            recognized_words = " ".join([text[1] for text in result_words])
            st.write("Recognized Words:", recognized_words)

            # Process recognized characters
            recognized_chars = "".join(result_chars)
            st.write("Recognized Characters:", recognized_chars)

            # Combine recognized words and characters
            recognized_text = recognized_words if recognized_words else recognized_chars
            st.write("Recognized Text:", recognized_text)
            
            # Fetch image URLs based on recognized text
            image_urls = fetch_image_urls(recognized_text)
            
            # Check if any image URLs are found
            if image_urls:
                image_url = image_urls[0]
                st.image(image_url, width=400)  # Display the first image URL
            else:
                st.error("No image URLs found for the recognized text.")
            
            # Speak out the recognized text with selected voice gender
            gender = 'male' if voice_gender == "Male" else 'female'
            generate_speech(recognized_text, gender=gender)

# Run the app
if __name__ == "__main__":
    main()
