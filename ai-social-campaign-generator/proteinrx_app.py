"""
ProteinRX Marketing Campaign Generator - Web Interface
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import re
import logging

from services.llm_service import LLMService
from services.image_service import ImageService
from agents.orchestrator import CampaignOrchestrator
from utils.memory_manager import MemoryManager
from config.settings import settings

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ProteinRX Campaign Generator",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ProteinRX branding
st.markdown("""
<style>
    /* Import Lato font */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

    /* Global styles */
    .main {
        background: linear-gradient(135deg, #000000 0%, #1a0000 50%, #000000 100%);
        font-family: 'Lato', sans-serif;
    }

    /* Header styles */
    .header-container {
        background: linear-gradient(90deg, #ff0000, #cc0000);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.3);
    }

    .header-title {
        color: white;
        font-family: 'Lato', sans-serif;
        font-weight: 900;
        font-size: 3rem;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    .header-subtitle {
        color: #f0f0f0;
        font-family: 'Lato', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        text-align: center;
        margin: 0.5rem 0 0 0;
    }

    /* Chat container */
    .chat-container {
        background: rgba(20, 20, 20, 0.9);
        border: 2px solid #ff0000;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(255, 0, 0, 0.2);
    }

    /* Message styles */
    .user-message {
        background: linear-gradient(135deg, #ff0000, #cc0000);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        font-family: 'Lato', sans-serif;
        font-weight: 500;
        box-shadow: 0 3px 10px rgba(255, 0, 0, 0.3);
    }

    .assistant-message {
        background: rgba(40, 40, 40, 0.9);
        color: #f0f0f0;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        border-left: 4px solid #ff0000;
        font-family: 'Lato', sans-serif;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Input styles */
    .stTextInput > div > div > input {
        background: rgba(20, 20, 20, 0.9);
        color: white;
        border: 2px solid #ff0000;
        border-radius: 10px;
        font-family: 'Lato', sans-serif;
        font-size: 1rem;
        padding: 0.75rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #ff4444;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
    }

    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #ff0000, #cc0000);
        color: white;
        border: none;
        border-radius: 10px;
        font-family: 'Lato', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(255, 0, 0, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #ff3333, #ff0000);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.4);
    }

    /* Sidebar styles */
    .css-1d391kg {
        background: rgba(10, 10, 10, 0.95);
        border-right: 2px solid #ff0000;
    }

    /* Status indicators */
    .status-active {
        color: #ff0000;
        font-weight: 700;
        font-family: 'Lato', sans-serif;
    }

    .status-ready {
        color: #00ff00;
        font-weight: 700;
        font-family: 'Lato', sans-serif;
    }

    /* Logo styling */
    .logo-container {
        text-align: center;
        margin: 1rem 0;
    }

    .dumbbell-logo {
        font-size: 3rem;
        color: #ff0000;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Campaign card styles */
    .campaign-card {
        background: rgba(30, 30, 30, 0.9);
        border: 2px solid #ff0000;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(255, 0, 0, 0.2);
    }

    .campaign-title {
        color: #ff0000;
        font-family: 'Lato', sans-serif;
        font-weight: 900;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff0000, #cc0000);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ff3333, #ff0000);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "greeting"
if "campaign_ready" not in st.session_state:
    st.session_state.campaign_ready = False
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

def initialize_services():
    """Initialize services (no caching to ensure fresh API calls)"""
    llm_service = LLMService()
    image_service = ImageService()
    orchestrator = CampaignOrchestrator(llm_service, image_service)
    memory_manager = MemoryManager()
    return orchestrator, memory_manager

def display_header():
    """Display the ProteinRX branded header"""
    st.markdown("""
    <div class="header-container">
        <div class="logo-container">
            <div class="dumbbell-logo">🏋️</div>
        </div>
        <h1 class="header-title">ProteinRX</h1>
        <p class="header-subtitle">AI Marketing Campaign Generator</p>
        <p class="header-subtitle">Luxury Protein • Strong Results • Smart Marketing</p>
    </div>
    """, unsafe_allow_html=True)

# Removed complex parsing functions for now

def display_message(role: str, content: str):
    """Display a chat message with ProteinRX styling"""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Format content with line breaks - show raw response like CLI
        formatted_content = content.replace('\n', '<br>')
        st.markdown(f"""
        <div class="assistant-message">
            {formatted_content}
        </div>
        """, unsafe_allow_html=True)

# Removed complex display function for now

async def extract_and_generate_images(ai_response: str):
    """Extract image prompts from AI response and generate images"""
    try:
        # Extract image prompts using regex
        image_prompts = []

        # Look for patterns like "**Image Prompt:** [description]" - more precise
        patterns = [
            r'\*\*Image Prompt:\*\*\s*(.+?)(?=\*\*Instagram Caption|\*\*Caption|##\s*Campaign|\n\n)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            image_prompts.extend([match.strip() for match in matches if match.strip()])

        # Debug: Log the AI response and extracted prompts
        logger.info(f"AI Response length: {len(ai_response)} characters")
        logger.info(f"AI Response preview: {ai_response[:200]}...")

        if not image_prompts:
            logger.info("No image prompts found in AI response")
            return

        logger.info(f"Found {len(image_prompts)} image prompts:")
        for i, prompt in enumerate(image_prompts):
            logger.info(f"  {i+1}: {prompt[:100]}...")

        # Initialize image service
        image_service = ImageService()

        # Generate images for each prompt
        generated_images = []
        for i, prompt in enumerate(image_prompts):
            try:
                logger.info(f"Generating image {i+1}/{len(image_prompts)}: {prompt[:50]}...")

                # Add ProteinRX branding to the prompt
                enhanced_prompt = f"{prompt}, ProteinRX branding, red and black colors, dumbbell logo, professional fitness photography, high quality"

                # Try to generate image, but fallback to description if it fails
                try:
                    image_result = await image_service.generate_image(
                        enhanced_prompt,
                        style="professional",
                        platform="instagram"
                    )
                except Exception as img_error:
                    logger.warning(f"Image generation failed: {img_error}")
                    image_result = None

                if image_result and image_result.startswith('data:image'):
                    # Successfully generated image (either real or placeholder)
                    generated_images.append({
                        "prompt": prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image_data": image_result,
                        "campaign_number": i + 1,
                        "type": "image"
                    })
                    logger.info(f"Successfully generated visual for campaign {i+1}")
                else:
                    # Fallback to description if even placeholder fails
                    generated_images.append({
                        "prompt": prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image_data": None,
                        "campaign_number": i + 1,
                        "type": "description",
                        "visual_description": enhanced_prompt
                    })
                    logger.info(f"Created text description for campaign {i+1}")

            except Exception as e:
                logger.error(f"Error generating image {i+1}: {e}")
                generated_images.append({
                    "prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "image_data": None,
                    "campaign_number": i + 1,
                    "error": str(e)
                })

        # Store generated images in session state
        st.session_state.generated_images = generated_images
        logger.info(f"Stored {len(generated_images)} image results in session state")

        return generated_images

    except Exception as e:
        logger.error(f"Error in extract_and_generate_images: {e}")
        return []

async def start_new_conversation():
    """Start a new conversation session"""
    try:
        response = await st.session_state.orchestrator.start_conversation()
        st.session_state.session_id = response["session_id"]
        st.session_state.current_stage = response["stage"]
        st.session_state.conversation_history = []
        st.session_state.campaign_ready = False

        # Add initial message
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": response["message"]
        })

        st.rerun()
    except Exception as e:
        st.error(f"Failed to start conversation: {e}")

async def handle_user_message(message: str):
    """Handle user message and get AI response"""
    try:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Debug: Check orchestrator type
        logger.info(f"Orchestrator type: {type(st.session_state.orchestrator)}")
        logger.info(f"LLM service type: {type(st.session_state.orchestrator.llm_service)}")

        # Use the standard continue_conversation method (now that orchestrator is fixed)
        logger.info(f"Processing user message: {message}")

        import time
        start_time = time.time()
        response_dict = await st.session_state.orchestrator.continue_conversation(
            st.session_state.session_id, message
        )
        end_time = time.time()
        logger.info(f"Response time: {end_time - start_time:.2f} seconds")

        if response_dict.get("status") == "error":
            st.error(f"Error: {response_dict.get('message', 'Unknown error')}")
            return

        # Add AI response to history
        ai_message = {
            "role": "assistant",
            "content": response_dict["message"]
        }

        st.session_state.conversation_history.append(ai_message)

        # Update stage
        st.session_state.current_stage = response_dict["stage"]

        # Extract and generate images from AI response
        await extract_and_generate_images(response_dict["message"])

        st.rerun()
    except Exception as e:
        st.error(f"Failed to process message: {e}")

def main():
    """Main application"""
    # Initialize services fresh each time to avoid caching issues
    if "orchestrator" not in st.session_state or st.session_state.orchestrator is None:
        orchestrator, memory_manager = initialize_services()
        st.session_state.orchestrator = orchestrator
        logger.info(f"Initialized new orchestrator: {type(orchestrator)}")
        logger.info(f"LLM service: {type(orchestrator.llm_service)}")
        logger.info(f"LLM provider: {orchestrator.llm_service.llm}")
    else:
        logger.info(f"Using existing orchestrator: {type(st.session_state.orchestrator)}")

    # Display header
    display_header()

    # Main layout
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # Chat interface
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        if st.session_state.session_id is None:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <h3 style="color: #ff0000; font-family: 'Lato', sans-serif;">Welcome to ProteinRX Marketing AI</h3>
                <p style="color: #000000; font-weight: 500;">Ready to create powerful Instagram campaigns for your protein smoothie brand?</p>
                <p style="color: #000000; font-weight: 500;">Click "Start Campaign Planning" to begin!</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Start Campaign Planning", key="start_btn"):
                asyncio.run(start_new_conversation())
        else:
            # Display conversation history
            for msg in st.session_state.conversation_history:
                display_message(msg["role"], msg["content"])

            # Message input
            user_input = st.chat_input("Share your campaign ideas for ProteinRX...")

            if user_input:
                asyncio.run(handle_user_message(user_input))

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Status panel
        st.markdown("""
        <div class="campaign-card">
            <div class="campaign-title">📊 Status</div>
        """, unsafe_allow_html=True)

        if st.session_state.session_id:
            st.markdown(f'<p class="status-active">🟢 Active Session</p>', unsafe_allow_html=True)
            stage_display = st.session_state.current_stage.replace('_', ' ').title()
            st.markdown(f'<p style="color: #f0f0f0;">Stage: {stage_display}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #888;">No active session</p>', unsafe_allow_html=True)

        if st.session_state.campaign_ready:
            st.markdown('<p class="status-ready">✅ Campaign Ready</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Brand info panel
        st.markdown("""
        <div class="campaign-card">
            <div class="campaign-title">🏋️ ProteinRX Brand</div>
            <p style="color: #f0f0f0; font-size: 0.9rem;">
                <strong>Product:</strong> Canned protein smoothies<br>
                <strong>Target:</strong> Gym-goers (20-45)<br>
                <strong>Platform:</strong> Instagram<br>
                <strong>Voice:</strong> Luxury + Strong<br>
                <strong>Colors:</strong> Red & Black<br>
                <strong>Logo:</strong> 🏋️ Dumbbell
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick actions
        st.markdown("""
        <div class="campaign-card">
            <div class="campaign-title">⚡ Quick Actions</div>
        """, unsafe_allow_html=True)

        if st.button("🔄 New Session", key="new_session"):
            if st.session_state.session_id:
                asyncio.run(start_new_conversation())

        if st.session_state.campaign_ready:
            if st.button("📥 Export Campaign", key="export_campaign"):
                st.success("Campaign export feature coming soon!")

        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        # Assets section
        st.markdown("""
        <div class="campaign-card">
            <div class="campaign-title">🎨 Generated Assets</div>
        """, unsafe_allow_html=True)

        if st.session_state.generated_images:
            st.markdown(f'<p style="color: #f0f0f0; font-size: 0.9rem;">Found {len(st.session_state.generated_images)} campaign visuals</p>', unsafe_allow_html=True)

            for i, image_data in enumerate(st.session_state.generated_images):
                with st.expander(f"Campaign {image_data['campaign_number']} Visual", expanded=False):
                    # Show the original prompt
                    st.markdown(f"**Prompt:** {image_data['prompt'][:100]}..." if len(image_data['prompt']) > 100 else f"**Prompt:** {image_data['prompt']}")

                    if image_data.get('type') == 'image' and image_data['image_data']:
                        # Display the generated image
                        if image_data['image_data'].startswith('data:image'):
                            # Base64 encoded image
                            st.markdown(f'<img src="{image_data["image_data"]}" style="width:100%; border-radius:8px; border:2px solid #ff0000;" alt="Campaign Visual">', unsafe_allow_html=True)
                        else:
                            # URL or other format
                            st.image(image_data['image_data'], width=200, caption=f"Campaign {image_data['campaign_number']}")
                    elif image_data.get('type') == 'description':
                        # Show visual description
                        st.markdown(f"""
                        <div style="background: rgba(255,0,0,0.1); border: 1px solid #ff0000; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                            <h4 style="color: #ff0000; margin: 0 0 0.5rem 0;">📸 Visual Concept</h4>
                            <p style="color: #f0f0f0; margin: 0; font-size: 0.9rem;">{image_data['visual_description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif 'error' in image_data:
                        st.error(f"❌ {image_data['error']}")
                    else:
                        st.info("🔄 Processing visual...")

            # Clear images button
            if st.button("🗑️ Clear Assets", key="clear_assets"):
                st.session_state.generated_images = []
                st.rerun()
        else:
            st.markdown('<p style="color: #888; font-size: 0.9rem;">No assets generated yet. Images will appear here after campaigns are created.</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()