import streamlit as st
import requests
import io
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Terupt Comic Creator", page_icon="❄️", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    
    .stApp {
        background-color: #f0f2f6;
    }
    
    h1 {
        font-family: 'Comic Neue', cursive;
        color: #2c3e50;
        text-align: center;
        font-size: 60px;
    }
    
    .stImage img {
        border: 5px solid black;
        box-shadow: 10px 10px 0px #888888;
        transition: transform 0.2s;
    }
    .stImage img:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ The Terupt Visualizer")
st.markdown("### Turn a chapter into a comic page instantly!")

# --- 3. SIDEBAR & AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("Enter Hugging Face Token", type="password")

# --- 4. AI FUNCTIONS ---
def get_story_panels(scene_description, character):
    """Uses Llama 3 to split a scene into 3 image prompts"""
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # The Prompt Engineering
    prompt = f"""
    [INST] You are a comic book writer adapting the book 'Because of Mr. Terupt'.
    
    The user wants to visualize this scene: "{scene_description}".
    The perspective is from the character: {character}.
    
    Create 3 distinct, visual descriptions for 3 comic book panels that tell this story sequentially.
    Keep descriptions physical and visual (what do we see?).
    
    Format output EXACTLY like this:
    PANEL 1: [Description]
    PANEL 2: [Description]
    PANEL 3: [Description]
    [/INST]
    """
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        return response.json()[0]['generated_text']
    except:
        # Fallback if AI fails (Mock data)
        return f"PANEL 1: {character} looks worried.\nPANEL 2: The scene happens: {scene_description}.\nPANEL 3: The aftermath."

def generate_image(prompt_text):
    """Uses Stable Diffusion to draw the panel"""
    # We use the reliable v1-5 model
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Add art style magic words
    final_prompt = f"comic book art, graphic novel style, {prompt_text}, detailed, vibrant colors, school setting"
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt})
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None
    except:
        return None

# --- 5. USER INPUTS ---
col1, col2 = st.columns([1, 2])

with col1:
    character = st.selectbox("Who is narrating?", 
        ["Peter (The Class Clown)", "Jessica (The New Girl)", "Luke (The Brain)", 
         "Alexia (The Queen Bee)", "Jeffrey (The Slacker)", "Danielle (The Pushover)", "Anna (The Shy One)"]
    )
    
    chapter_idea = st.text_area("Describe the Scene/Chapter:", 
        placeholder="Example: The class goes outside for the reward day and Peter creates a snowball..."
    )
    
    generate_btn = st.button("🎨 Draw Comic Page")

# --- 6. MAIN GENERATION LOOP ---
if generate_btn and api_key:
    if not chapter_idea:
        st.warning("Please describe a scene first!")
    else:
        # Step 1: Write the Script
        with st.spinner("✍️ Writing the script (Asking Llama 3)..."):
            script_raw = get_story_panels(chapter_idea, character)
            
            # Simple parsing to find the panels (This assumes the AI follows instructions, which Llama 3 usually does)
            # If parsing fails, we just use the user input as the base
            p1_text = f"{character} in a school setting, {chapter_idea}, beginning of scene"
            p2_text = f"Action shot, {chapter_idea}, middle of scene"
            p3_text = f"Dramatic reaction, {chapter_idea}, end of scene"
            
            # Try to extract real panels from AI response
            if "PANEL 1:" in script_raw:
                parts = script_raw.split("PANEL")
                if len(parts) >= 4:
                    p1_text = parts[1].replace("1:", "").strip()
                    p2_text = parts[2].replace("2:", "").strip()
                    p3_text = parts[3].replace("3:", "").strip()

        # Step 2: Draw the Panels
        st.success("Script Generated! Now drawing...")
        
        panel_cols = st.columns(3)
        prompts = [p1_text, p2_text, p3_text]
        
        for i, col in enumerate(panel_cols):
            with col:
                st.info(f"Panel {i+1}")
                st.caption(f"Prompt: {prompts[i][:100]}...") # Show a preview of the text
                
                with st.spinner("Drawing..."):
                    img = generate_image(prompts[i])
                    if img:
                        st.image(img, use_column_width=True)
                    else:
                        st.error("Image Gen Failed (Server Busy)")

elif generate_btn and not api_key:
    st.error("🔒 Please enter your Token in the sidebar!")
