import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Mr. Terupt Comic Creator", page_icon="❄️", layout="wide")

# --- 2. COMIC STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Roboto&display=swap');
    
    .stApp {
        background-color: #f4f4f4;
    }
    
    h1 {
        font-family: 'Bangers', cursive;
        color: #2c3e50;
        text-align: center;
        font-size: 70px;
        letter-spacing: 2px;
        text-shadow: 3px 3px #3498db;
    }
    
    .chapter-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2c3e50;
        box-shadow: 5px 5px 0px #2c3e50;
    }
    
    .stImage img {
        border: 4px solid black;
        box-shadow: 8px 8px 0px black;
        transition: transform 0.2s;
    }
    .stImage img:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ BECAUSE OF MR. TERUPT")
st.markdown("<h3 style='text-align: center; font-family: Roboto;'>The Graphic Novel Generator</h3>", unsafe_allow_html=True)

# --- 3. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("Enter Hugging Face Token", type="password")

# --- 4. THE BOOK KNOWLEDGE BASE ---
# We map specific chapters to visual descriptions so the AI gets it right every time.
BOOK_SCENES = {
    "Select a Chapter...": "",
    
    "September: The Dollar Word Challenge": {
        "character": "Luke (The Brain)",
        "summary": "Mr. Terupt challenges the class to find words where the letters add up to exactly 100 dollars. Luke calculates furiously on the board.",
        "panels": [
            "Luke standing at a chalkboard covered in math equations and alphabet numbers, looking intense.",
            "Mr. Terupt smiling and holding a dollar bill, challenging the class.",
            "Luke holding up a piece of paper with the word 'EXCELLENT' written on it, looking proud."
        ]
    },
    
    "November: The Plant Experiment": {
        "character": "Jessica (The New Girl)",
        "summary": "The class is growing bean plants. Some are fed special concoctions. Jessica is caring gently for her plant.",
        "panels": [
            "Close up of bean plants growing in cups on a classroom windowsill.",
            "Jessica carefully watering a plant with a dropper, looking caring.",
            "A split screen showing a healthy plant vs a dead plant, science experiment style."
        ]
    },
    
    "February: The Snowball Incident": {
        "character": "Peter (The Class Clown)",
        "summary": "The class has a reward day in the snow. Peter rolls a snowball. He throws it and accidentally hits Mr. Terupt, who falls.",
        "panels": [
            "A snowy playground, Peter rolling a large snowball, looking mischievous.",
            "Peter throwing the snowball through the air, time frozen, looking shocked.",
            "Mr. Terupt falling into the snow, glasses flying off, dramatic angle."
        ]
    },
    
    "March: The Hospital Waiting Room": {
        "character": "Alexia (The Queen Bee)",
        "summary": "The students are sitting in the hospital hallway waiting for news about Mr. Terupt. They are sad and bonding.",
        "panels": [
            "A sterile hospital hallway, students sitting on chairs looking sad.",
            "Alexia and Jessica holding hands or sitting close, looking supportive.",
            "A view of a closed hospital door with a 'Do Not Enter' sign."
        ]
    },
    
    "June: The Last Day": {
        "character": "Mr. Terupt",
        "summary": "Mr. Terupt returns to the classroom on the last day of school. The kids are cheering.",
        "panels": [
            "The classroom door opening, revealing Mr. Terupt standing there.",
            "The entire class cheering and clapping, streamers in the air.",
            "A close up of Mr. Terupt smiling with a tear in his eye."
        ]
    }
}

# --- 5. AI GENERATION FUNCTION (DIRECT MODE) ---
def generate_panel(prompt_text):
    client = InferenceClient(model="runwayml/stable-diffusion-v1-5", token=api_key)
    
    # Comic Book Magic Words
    style = "comic book art, graphic novel style, thick ink lines, vibrant colors, detailed, cel shaded"
    full_prompt = f"{style}, {prompt_text}"
    
    try:
        # We use the text_to_image function (safe and reliable)
        image = client.text_to_image(full_prompt)
        return image
    except Exception as e:
        return None

# --- 6. USER INTERFACE ---
selected_chapter = st.selectbox("📖 Choose a Chapter/Event:", list(BOOK_SCENES.keys()))

if selected_chapter != "Select a Chapter..." and api_key:
    scene_data = BOOK_SCENES[selected_chapter]
    
    # Display Scene Info
    st.info(f"**Narrator:** {scene_data['character']}")
    st.write(f"**Context:** {scene_data['summary']}")
    
    if st.button("🎨 GENERATE COMIC PAGE"):
        
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for i, panel_desc in enumerate(scene_data['panels']):
            with columns[i]:
                st.markdown(f"**Panel {i+1}**")
                with st.spinner("Drawing..."):
                    img = generate_panel(panel_desc)
                    if img:
                        st.image(img, use_column_width=True)
                        st.caption(panel_desc)
                    else:
                        st.error("Server Busy (Try Again)")

elif not api_key:
    st.warning("Please enter your Token in the sidebar.")
