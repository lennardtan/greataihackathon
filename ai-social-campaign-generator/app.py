"""
Streamlit Web Interface for AI Social Media Campaign Generator
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from services.llm_service import LLMService
from services.image_service import ImageService
from agents.orchestrator import CampaignOrchestrator
from utils.memory_manager import MemoryManager
from utils.helpers import create_campaign_report, format_platform_content
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Social Campaign Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

@st.cache_resource
def initialize_services():
    """Initialize services (cached to avoid recreation)"""
    llm_service = LLMService()
    image_service = ImageService()
    orchestrator = CampaignOrchestrator(llm_service, image_service)
    memory_manager = MemoryManager()
    return orchestrator, memory_manager

def main():
    # Initialize services
    orchestrator, memory_manager = initialize_services()
    st.session_state.orchestrator = orchestrator
    
    # Header
    st.title("🚀 AI Social Media Campaign Generator")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("💬 Conversation")
        
        # Start new conversation button
        if st.button("🔄 Start New Conversation", type="primary"):
            asyncio.run(start_new_conversation())
        
        # Session info
        if st.session_state.session_id:
            st.success(f"Active Session: {st.session_state.session_id[:8]}...")
            st.info(f"Stage: {st.session_state.current_stage.replace('_', ' ').title()}")
        
        st.markdown("---")
        
        # Conversation history
        st.subheader("📝 Chat History")
        chat_container = st.container()
        
        with chat_container:
            for i, msg in enumerate(st.session_state.conversation_history[-10:]):  # Show last 10 messages
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
        
        st.markdown("---")
        
        # Export options
        st.subheader("📤 Export")
        if st.session_state.campaign_ready:
            if st.button("📋 Export Campaign"):
                export_campaign()
        else:
            st.info("Complete your campaign to enable export")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.subheader("💬 Chat with Your AI Marketing Consultant")
        
        # Chat input
        if st.session_state.session_id is None:
            if st.button("Start Conversation", type="primary"):
                asyncio.run(start_new_conversation())
        else:
            # Message input
            user_message = st.chat_input("Type your message here...")
            
            if user_message:
                asyncio.run(handle_user_message(user_message))
        
        # Display current conversation
        if st.session_state.conversation_history:
            st.markdown("### Current Conversation")
            for msg in st.session_state.conversation_history[-6:]:  # Show last 6 messages
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
                    # Show suggestions if available
                    if msg.get("suggestions"):
                        st.markdown("**Suggestions:**")
                        for suggestion in msg["suggestions"]:
                            if st.button(f"💡 {suggestion}", key=f"suggestion_{hash(suggestion)}"):
                                asyncio.run(handle_user_message(suggestion))
    
    with col2:
        # Status and progress
        st.subheader("📊 Progress")
        
        if st.session_state.session_id:
            # Progress bar
            progress = calculate_progress(st.session_state.current_stage)
            st.progress(progress)
            st.write(f"Progress: {progress:.0%}")
            
            # Stage indicators
            stages = [
                ("Greeting", "greeting"),
                ("Discovery", "discovery"),
                ("Brand Analysis", "brand_analysis"),
                ("Strategy", "strategy_development"),
                ("Content Creation", "content_creation"),
                ("Review", "review_refinement"),
                ("Finalization", "finalization")
            ]
            
            for stage_name, stage_key in stages:
                if stage_key == st.session_state.current_stage:
                    st.success(f"✅ {stage_name} (Current)")
                elif get_stage_order(stage_key) < get_stage_order(st.session_state.current_stage):
                    st.success(f"✅ {stage_name}")
                else:
                    st.info(f"⏳ {stage_name}")
        
        st.markdown("---")
        
        # Campaign preview
        if st.session_state.campaign_ready:
            st.subheader("🎯 Campaign Preview")
            campaign = asyncio.run(get_campaign_output())
            
            if campaign and not campaign.get("error"):
                # Show basic stats
                posts = campaign.get("campaign", {}).get("posts", [])
                platforms = list(set([post.get("platform", "") for post in posts]))
                
                st.metric("Posts Created", len(posts))
                st.metric("Platforms", len(platforms))
                
                # Show platform breakdown
                platform_counts = {}
                for post in posts:
                    platform = post.get("platform", "unknown")
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                for platform, count in platform_counts.items():
                    st.write(f"📱 {platform.title()}: {count} posts")

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
        
        # Get AI response
        response = await st.session_state.orchestrator.continue_conversation(
            st.session_state.session_id, message
        )
        
        if response.get("status") == "error":
            st.error(f"Error: {response.get('message', 'Unknown error')}")
            return
        
        # Add AI response to history
        ai_message = {
            "role": "assistant",
            "content": response["message"]
        }
        
        # Add suggestions if available
        if response.get("suggestions"):
            ai_message["suggestions"] = response["suggestions"]
        
        st.session_state.conversation_history.append(ai_message)
        
        # Update stage
        st.session_state.current_stage = response["stage"]
        
        # Check if campaign is ready
        if response["stage"] in ["review_refinement", "finalization"]:
            campaign = await get_campaign_output()
            if campaign and not campaign.get("error"):
                st.session_state.campaign_ready = True
        
        st.rerun()
    except Exception as e:
        st.error(f"Failed to process message: {e}")

async def get_campaign_output():
    """Get campaign output if available"""
    try:
        if st.session_state.session_id:
            return await st.session_state.orchestrator.get_campaign_output(
                st.session_state.session_id
            )
    except Exception as e:
        st.error(f"Failed to get campaign output: {e}")
    return None

def export_campaign():
    """Export campaign to downloadable file"""
    try:
        campaign = asyncio.run(get_campaign_output())
        if not campaign or campaign.get("error"):
            st.error("Campaign not ready for export")
            return
        
        # Create export data
        export_data = {
            "session_id": st.session_state.session_id,
            "generated_at": datetime.utcnow().isoformat(),
            "campaign": campaign["campaign"],
            "conversation_history": st.session_state.conversation_history[-20:]  # Last 20 messages
        }
        
        # Convert to JSON
        json_str = json.dumps(export_data, indent=2, default=str)
        
        # Create download
        st.download_button(
            label="📥 Download Campaign JSON",
            data=json_str,
            file_name=f"campaign_{st.session_state.session_id[:8]}.json",
            mime="application/json"
        )
        
        st.success("Campaign ready for download!")
        
    except Exception as e:
        st.error(f"Export failed: {e}")

def calculate_progress(stage: str) -> float:
    """Calculate progress based on current stage"""
    stage_weights = {
        "greeting": 0.1,
        "discovery": 0.3,
        "brand_analysis": 0.5,
        "strategy_development": 0.7,
        "content_creation": 0.9,
        "review_refinement": 0.95,
        "finalization": 1.0
    }
    return stage_weights.get(stage, 0.0)

def get_stage_order(stage: str) -> int:
    """Get stage order for comparison"""
    stages = [
        "greeting", "discovery", "brand_analysis", 
        "strategy_development", "content_creation", 
        "review_refinement", "finalization"
    ]
    return stages.index(stage) if stage in stages else 0

# Advanced features page
def show_advanced_features():
    """Show advanced features page"""
    st.header("🔧 Advanced Features")
    
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "⚙️ Settings", "📱 Platform Specs"])
    
    with tab1:
        st.subheader("Campaign Analytics")
        if st.session_state.campaign_ready:
            campaign = asyncio.run(get_campaign_output())
            if campaign and not campaign.get("error"):
                posts = campaign.get("campaign", {}).get("posts", [])
                
                # Platform distribution chart
                platform_counts = {}
                for post in posts:
                    platform = post.get("platform", "unknown")
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                st.bar_chart(platform_counts)
                
                # Content length analysis
                content_lengths = [len(post.get("content", "")) for post in posts]
                if content_lengths:
                    st.metric("Average Content Length", f"{sum(content_lengths) / len(content_lengths):.0f} chars")
                    st.metric("Total Hashtags", sum(len(post.get("hashtags", [])) for post in posts))
        else:
            st.info("Complete your campaign to see analytics")
    
    with tab2:
        st.subheader("Configuration")
        
        # Model settings
        st.selectbox("LLM Provider", ["AWS Bedrock", "OpenAI", "Anthropic"], index=0)
        st.selectbox("LLM Model", ["Claude-3 Sonnet", "GPT-4", "Claude-3 Haiku"], index=0)
        
        # Content settings
        st.slider("Content Creativity", 0.1, 1.0, 0.7, 0.1)
        st.slider("Posts per Platform", 1, 10, 3)
        
        st.button("💾 Save Settings")
    
    with tab3:
        st.subheader("Platform Specifications")
        
        platform_specs = {
            "Instagram": {"Post": "1080x1080", "Story": "1080x1920", "Reel": "1080x1920"},
            "Facebook": {"Post": "1200x630", "Story": "1080x1920"},
            "LinkedIn": {"Post": "1200x627", "Article": "1200x627"},
            "Twitter": {"Post": "1200x675", "Header": "1500x500"},
            "TikTok": {"Video": "1080x1920"},
            "YouTube": {"Thumbnail": "1280x720", "Channel Art": "2560x1440"}
        }
        
        for platform, specs in platform_specs.items():
            with st.expander(f"📱 {platform}"):
                for content_type, dimensions in specs.items():
                    st.write(f"**{content_type}:** {dimensions}")

# Navigation
def show_navigation():
    """Show navigation menu"""
    pages = {
        "💬 Chat": main,
        "🔧 Advanced": show_advanced_features
    }
    
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[selected_page]()

if __name__ == "__main__":
    # Check if we should show advanced features
    if st.sidebar.button("🔧 Advanced Features"):
        show_advanced_features()
    else:
        main()