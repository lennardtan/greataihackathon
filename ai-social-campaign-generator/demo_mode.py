"""
Demo mode for testing without API keys
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

from models.schemas import (
    ConversationContext, ConversationMessage, MessageRole, 
    ConversationStage, AgentResponse, CompanyInfo, CampaignGoals,
    Industry, CampaignObjective, SocialPlatform, SocialPost
)

class DemoLLMService:
    """Mock LLM service for demo mode"""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! I'm excited to help you create an amazing social media campaign. What's your business about?",
                "Hi there! I'm your AI marketing consultant. Tell me about your business and what you're hoping to achieve!",
                "Welcome! Let's create some fantastic social media content together. What kind of business are you running?"
            ],
            "discovery": [
                "That sounds great! I'd love to learn more about your target audience. Who are you trying to reach?",
                "Interesting! Tell me more about your brand personality. How would you describe your business voice?",
                "Perfect! What are your main goals for social media marketing? Brand awareness, sales, or engagement?",
                "Excellent! Which social media platforms are most important for your business?"
            ],
            "strategy": [
                "Based on what you've told me, I can see some great opportunities for your brand. Let me develop a comprehensive strategy that focuses on authentic storytelling and community engagement.",
                "I have a clear understanding of your brand now. I'll create a strategy that highlights your unique value proposition and connects with your target audience.",
                "Perfect! I'm developing a multi-platform strategy that will showcase your brand personality and drive meaningful engagement."
            ],
            "content": [
                "Excellent! I've created a complete social media campaign for you with posts optimized for each platform. Each post includes engaging copy, strategic hashtags, and visual concepts.",
                "Your campaign is ready! I've generated platform-specific content that aligns with your brand voice and marketing goals.",
                "Perfect! I've created engaging social media posts that tell your brand story and encourage audience interaction."
            ]
        }
        
        self.content_examples = {
            "instagram": {
                "content": "🌟 Discover the authentic flavors that make our kitchen special! Every dish tells a story of tradition, passion, and community.\n\nWhat's your favorite comfort food that reminds you of home? Share in the comments! 👇",
                "hashtags": ["#AuthenticFlavors", "#CommunityKitchen", "#FoodStory", "#ComfortFood", "#LocalFavorites"],
                "visual": "Warm, inviting kitchen scene with chef preparing signature dish, natural lighting, focus on fresh ingredients and traditional cooking methods"
            },
            "facebook": {
                "content": "Good morning, food lovers! We're excited to share the story behind our signature dish. Three generations of family recipes come together in every bite we serve.\n\nCome experience the difference that tradition and passion make. We're open daily from 11 AM to 9 PM, and we can't wait to welcome you!",
                "hashtags": ["#FamilyTradition", "#AuthenticCuisine", "#LocalRestaurant"],
                "visual": "Family photo in restaurant with three generations, warm atmosphere, showcasing the heritage and tradition behind the business"
            }
        }
    
    async def chat_with_system(self, system_prompt: str, user_message: str) -> str:
        """Mock chat method"""
        # Simple keyword-based responses
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["restaurant", "food", "cuisine", "cooking"]):
            if "target" in user_lower or "audience" in user_lower:
                return "Young professionals aged 25-40 who appreciate authentic cuisine and cultural experiences, food enthusiasts, and local community members"
            elif "goal" in user_lower or "objective" in user_lower:
                return "Increase brand awareness, drive foot traffic for lunch and dinner service, and build a community of food enthusiasts"
            elif "platform" in user_lower:
                return "Instagram for visual food content and Instagram Stories, Facebook for community engagement and events"
            else:
                return random.choice(self.responses["discovery"])
        
        if "strategy" in user_lower or "plan" in user_lower:
            return random.choice(self.responses["strategy"])
        
        if "content" in user_lower or "post" in user_lower:
            return random.choice(self.responses["content"])
        
        return random.choice(self.responses["discovery"])

class DemoImageService:
    """Mock image service for demo mode"""
    
    async def generate_image(self, prompt: str, style: Optional[str] = None, 
                           platform: Optional[str] = None) -> Optional[str]:
        """Mock image generation"""
        return f"[Demo Image: {prompt[:50]}... - optimized for {platform or 'social media'}]"

class DemoOrchestrator:
    """Demo version of the orchestrator"""
    
    def __init__(self):
        self.llm_service = DemoLLMService()
        self.image_service = DemoImageService()
        self.active_contexts: Dict[str, ConversationContext] = {}
        self.demo_company = CompanyInfo(
            name="Demo Restaurant",
            industry=Industry.FOOD_BEVERAGE,
            description="Authentic cuisine restaurant serving traditional dishes",
            target_audience="Young professionals aged 25-40, food enthusiasts",
            brand_voice="Warm, welcoming, authentic, passionate about culinary traditions",
            brand_values=["Authenticity", "Quality", "Community", "Tradition"],
            unique_selling_points=["Family recipes", "Fresh ingredients", "Cultural storytelling"]
        )
    
    async def start_conversation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Start demo conversation"""
        import uuid
        session_id = str(uuid.uuid4())
        
        context = ConversationContext(
            session_id=session_id,
            current_stage=ConversationStage.GREETING,
            messages=[],
            company_info=CompanyInfo(name=""),
            campaign_goals=CampaignGoals(),
            extracted_insights={},
            pending_questions=[],
            user_preferences={}
        )
        
        self.active_contexts[session_id] = context
        
        greeting = random.choice(self.llm_service.responses["greeting"])
        
        context.messages.append(ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=greeting,
            timestamp=datetime.utcnow()
        ))
        
        return {
            "session_id": session_id,
            "message": greeting,
            "stage": ConversationStage.GREETING.value,
            "status": "active"
        }
    
    async def continue_conversation(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Continue demo conversation"""
        context = self.active_contexts.get(session_id)
        if not context:
            return {"error": "Session not found", "status": "error"}
        
        # Add user message
        context.messages.append(ConversationMessage(
            role=MessageRole.USER,
            content=user_message,
            timestamp=datetime.utcnow()
        ))
        
        # Simple state progression
        current_stage = context.current_stage
        
        if current_stage == ConversationStage.GREETING:
            # Extract business info from message
            if any(word in user_message.lower() for word in ["restaurant", "food", "cafe", "kitchen"]):
                context.company_info = self.demo_company
                context.current_stage = ConversationStage.DISCOVERY
                response_text = "That sounds fantastic! I'd love to learn more about your target audience and marketing goals. Who are you trying to reach with your social media?"
            else:
                response_text = "Tell me more about your business. What industry are you in?"
        
        elif current_stage == ConversationStage.DISCOVERY:
            context.current_stage = ConversationStage.STRATEGY_DEVELOPMENT
            response_text = "Perfect! I have a comprehensive understanding of your brand. Let me develop a strategy that showcases your authentic cuisine and builds community engagement."
        
        elif current_stage == ConversationStage.STRATEGY_DEVELOPMENT:
            context.current_stage = ConversationStage.CONTENT_CREATION
            response_text = "Excellent! I've developed your strategy. Now let me create engaging social media content that tells your brand story and drives foot traffic."
        
        elif current_stage == ConversationStage.CONTENT_CREATION:
            # Generate demo campaign
            posts = await self._create_demo_posts()
            context.extracted_insights["demo_posts"] = [post.dict() for post in posts]
            context.current_stage = ConversationStage.FINALIZATION
            
            response_text = f"🎉 Your campaign is ready! I've created {len(posts)} social media posts across Instagram and Facebook.\n\n"
            response_text += "**Your Campaign Includes:**\n"
            response_text += "• Platform-optimized content with engaging copy\n"
            response_text += "• Strategic hashtag recommendations\n"
            response_text += "• Visual concept descriptions for each post\n"
            response_text += "• Brand-consistent messaging and tone\n\n"
            response_text += "Would you like to see the specific posts or export your campaign?"
        
        else:
            response_text = "Your campaign is complete! You can export it or start a new conversation for additional content."
        
        # Add assistant response
        context.messages.append(ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=response_text,
            timestamp=datetime.utcnow()
        ))
        
        return {
            "session_id": session_id,
            "message": response_text,
            "stage": context.current_stage.value,
            "questions": [],
            "suggestions": ["Show me the posts", "Export campaign", "Create more content"],
            "requires_clarification": False,
            "confidence": 0.9,
            "status": "active"
        }
    
    async def _create_demo_posts(self) -> List[SocialPost]:
        """Create demo social media posts"""
        posts = []
        
        # Instagram post
        instagram_post = SocialPost(
            platform=SocialPlatform.INSTAGRAM,
            content="🌟 Discover the authentic flavors that make our kitchen special! Every dish tells a story of tradition, passion, and community.\n\nWhat's your favorite comfort food that reminds you of home? Share in the comments! 👇",
            hashtags=["#AuthenticFlavors", "#CommunityKitchen", "#FoodStory", "#ComfortFood", "#LocalFavorites"],
            image_prompt="Warm, inviting kitchen scene with chef preparing signature dish, natural lighting, focus on fresh ingredients and traditional cooking methods",
            call_to_action="Share your favorite comfort food in the comments!",
            post_type="feed",
            engagement_hooks=["What's your favorite comfort food?", "Share in the comments!"]
        )
        posts.append(instagram_post)
        
        # Facebook post
        facebook_post = SocialPost(
            platform=SocialPlatform.FACEBOOK,
            content="Good morning, food lovers! We're excited to share the story behind our signature dish. Three generations of family recipes come together in every bite we serve.\n\nCome experience the difference that tradition and passion make. We're open daily from 11 AM to 9 PM, and we can't wait to welcome you!",
            hashtags=["#FamilyTradition", "#AuthenticCuisine", "#LocalRestaurant"],
            image_prompt="Family photo in restaurant with three generations, warm atmosphere, showcasing the heritage and tradition behind the business",
            call_to_action="Visit us today and taste the tradition!",
            post_type="feed",
            engagement_hooks=["What's your family's signature dish?", "Tag someone who loves authentic cuisine!"]
        )
        posts.append(facebook_post)
        
        # Instagram Story
        story_post = SocialPost(
            platform=SocialPlatform.INSTAGRAM,
            content="Behind the scenes: Our chef starts at 6AM preparing fresh ingredients for today's specials! 👨‍🍳✨",
            hashtags=["#BehindTheScenes", "#FreshIngredients", "#ChefLife"],
            image_prompt="Chef in early morning kitchen prep, action shot of ingredient preparation, professional kitchen atmosphere",
            call_to_action="Swipe up to see today's menu!",
            post_type="story",
            engagement_hooks=["What time do you start your day?", "Early bird gets the fresh ingredients!"]
        )
        posts.append(story_post)
        
        return posts
    
    async def get_campaign_output(self, session_id: str) -> Dict[str, Any]:
        """Get demo campaign output"""
        context = self.active_contexts.get(session_id)
        if not context or "demo_posts" not in context.extracted_insights:
            return {"error": "Campaign not ready"}
        
        return {
            "session_id": session_id,
            "campaign": {
                "strategy": {
                    "executive_summary": "Comprehensive social media strategy focusing on authentic cuisine and community engagement",
                    "target_audience_analysis": "Young professionals and food enthusiasts who value authentic cultural experiences",
                    "content_pillars": ["Food Showcase", "Cultural Stories", "Behind the Scenes", "Community Engagement"],
                    "brand_positioning": "Authentic family-owned restaurant preserving culinary traditions",
                    "key_messages": ["Authentic flavors", "Family tradition", "Community connection", "Fresh ingredients"]
                },
                "posts": context.extracted_insights["demo_posts"],
                "hashtag_strategy": "Mix of branded, industry, and engagement hashtags to maximize reach and community building"
            },
            "ready": True
        }
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get demo conversation summary"""
        context = self.active_contexts.get(session_id)
        if not context:
            return {"error": "Session not found"}
        
        return {
            "session_id": session_id,
            "stage": context.current_stage.value,
            "company_info": context.company_info.dict(),
            "campaign_goals": context.campaign_goals.dict(),
            "insights_collected": list(context.extracted_insights.keys()),
            "message_count": len(context.messages),
            "created_at": context.created_at.isoformat(),
            "last_updated": context.last_updated.isoformat(),
            "progress": self._calculate_progress(context.current_stage)
        }
    
    def _calculate_progress(self, stage: ConversationStage) -> float:
        """Calculate progress"""
        stage_weights = {
            ConversationStage.GREETING: 0.1,
            ConversationStage.DISCOVERY: 0.3,
            ConversationStage.BRAND_ANALYSIS: 0.5,
            ConversationStage.STRATEGY_DEVELOPMENT: 0.7,
            ConversationStage.CONTENT_CREATION: 0.9,
            ConversationStage.REVIEW_REFINEMENT: 0.95,
            ConversationStage.FINALIZATION: 1.0
        }
        return stage_weights.get(stage, 0.0)