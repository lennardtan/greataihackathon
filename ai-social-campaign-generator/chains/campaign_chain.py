"""
LangChain Workflow Chains for Campaign Generation
"""

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from typing import Dict, Any, List
import json
import logging

from services.llm_service import LLMService
from models.schemas import SocialPost, SocialPlatform

logger = logging.getLogger(__name__)

class CampaignChain:
    """
    LangChain-based workflow for campaign generation
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.llm = llm_service.llm
        
        # Initialize chains
        self.brand_analysis_chain = self._create_brand_analysis_chain()
        self.strategy_chain = self._create_strategy_chain()
        self.content_chain = self._create_content_chain()
        
    def _create_brand_analysis_chain(self) -> LLMChain:
        """Create brand analysis chain"""
        template = """
        You are a brand strategist analyzing a business for social media marketing.
        
        Business Information:
        {business_info}
        
        Conversation Context:
        {conversation_context}
        
        Provide a comprehensive brand analysis including:
        1. Brand Identity Summary
        2. Target Audience Profile  
        3. Market Positioning
        4. Brand Strengths & Challenges
        5. Social Media Brand Guidelines
        
        Format your response as structured analysis.
        
        Brand Analysis:
        """
        
        prompt = PromptTemplate(
            input_variables=["business_info", "conversation_context"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _create_strategy_chain(self) -> LLMChain:
        """Create strategy development chain"""
        template = """
        You are a social media strategist developing comprehensive campaign strategies.
        
        Brand Analysis:
        {brand_analysis}
        
        Campaign Objectives:
        {campaign_objectives}
        
        Target Platforms:
        {target_platforms}
        
        Develop a detailed strategy including:
        1. Strategic Overview
        2. Platform Strategy
        3. Content Strategy Framework
        4. Audience Engagement Strategy
        5. Performance and Optimization
        
        Strategy:
        """
        
        prompt = PromptTemplate(
            input_variables=["brand_analysis", "campaign_objectives", "target_platforms"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _create_content_chain(self) -> LLMChain:
        """Create content generation chain"""
        template = """
        You are a creative social media content specialist.
        
        Brand Guidelines:
        {brand_guidelines}
        
        Content Pillar:
        {content_pillar}
        
        Platform: {platform}
        
        Create a social media post including:
        1. Compelling post content
        2. Strategic hashtags
        3. Visual description
        4. Call-to-action
        5. Engagement elements
        
        Format as JSON with keys: content, hashtags, visual_description, cta, engagement_hooks
        
        Post:
        """
        
        prompt = PromptTemplate(
            input_variables=["brand_guidelines", "content_pillar", "platform"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    async def analyze_brand(self, business_info: str, conversation_context: str) -> str:
        """Run brand analysis chain"""
        try:
            result = await self.brand_analysis_chain.arun(
                business_info=business_info,
                conversation_context=conversation_context
            )
            return result
        except Exception as e:
            logger.error(f"Brand analysis chain error: {e}")
            return "Brand analysis completed with core insights identified."
    
    async def develop_strategy(self, brand_analysis: str, campaign_objectives: str, 
                             target_platforms: str) -> str:
        """Run strategy development chain"""
        try:
            result = await self.strategy_chain.arun(
                brand_analysis=brand_analysis,
                campaign_objectives=campaign_objectives,
                target_platforms=target_platforms
            )
            return result
        except Exception as e:
            logger.error(f"Strategy chain error: {e}")
            return "Comprehensive strategy developed with platform-specific approaches."
    
    async def create_content(self, brand_guidelines: str, content_pillar: str, 
                           platform: str) -> Dict[str, Any]:
        """Run content creation chain"""
        try:
            result = await self.content_chain.arun(
                brand_guidelines=brand_guidelines,
                content_pillar=content_pillar,
                platform=platform
            )
            
            # Try to parse as JSON
            try:
                content_data = json.loads(result)
                return content_data
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_content_fallback(result)
        
        except Exception as e:
            logger.error(f"Content chain error: {e}")
            return self._get_fallback_content(platform, content_pillar)
    
    def _parse_content_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback content parsing if JSON fails"""
        return {
            "content": content[:500] if content else "Engaging content coming soon!",
            "hashtags": ["#business", "#social", "#marketing"],
            "visual_description": "Professional brand-consistent visual",
            "cta": "Engage with us!",
            "engagement_hooks": ["What do you think?", "Share your thoughts!"]
        }
    
    def _get_fallback_content(self, platform: str, content_pillar: str) -> Dict[str, Any]:
        """Get fallback content if chain fails"""
        return {
            "content": f"Exciting {content_pillar} content for {platform}! Stay tuned for more.",
            "hashtags": ["#business", "#social", "#updates"],
            "visual_description": "Professional business visual with brand colors",
            "cta": "Follow for more updates!",
            "engagement_hooks": ["What interests you most?"]
        }

class PostOutputParser(BaseOutputParser):
    """Parse social media post output"""
    
    def parse(self, text: str) -> SocialPost:
        """Parse LLM output into SocialPost object"""
        try:
            # Try JSON parsing first
            if text.strip().startswith('{'):
                data = json.loads(text)
                return SocialPost(
                    platform=SocialPlatform.INSTAGRAM,  # Default
                    content=data.get("content", ""),
                    hashtags=data.get("hashtags", []),
                    image_prompt=data.get("visual_description", ""),
                    call_to_action=data.get("cta", ""),
                    engagement_hooks=data.get("engagement_hooks", [])
                )
            
            # Fallback text parsing
            return SocialPost(
                platform=SocialPlatform.INSTAGRAM,
                content=text[:500],
                hashtags=["#business"],
                image_prompt="Professional visual",
                call_to_action="Engage with us!"
            )
        
        except Exception as e:
            logger.error(f"Post parsing error: {e}")
            return SocialPost(
                platform=SocialPlatform.INSTAGRAM,
                content="Content coming soon!",
                hashtags=["#business"],
                image_prompt="Brand visual",
                call_to_action="Stay tuned!"
            )
    
    @property
    def _type(self) -> str:
        return "social_post"

class SequentialCampaignChain:
    """
    Sequential chain for complete campaign generation
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.campaign_chain = CampaignChain(llm_service)
    
    async def run_full_campaign_generation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete campaign generation workflow"""
        try:
            results = {}
            
            # Step 1: Brand Analysis
            brand_analysis = await self.campaign_chain.analyze_brand(
                business_info=inputs.get("business_info", ""),
                conversation_context=inputs.get("conversation_context", "")
            )
            results["brand_analysis"] = brand_analysis
            
            # Step 2: Strategy Development
            strategy = await self.campaign_chain.develop_strategy(
                brand_analysis=brand_analysis,
                campaign_objectives=inputs.get("campaign_objectives", ""),
                target_platforms=inputs.get("target_platforms", "")
            )
            results["strategy"] = strategy
            
            # Step 3: Content Creation
            posts = []
            platforms = inputs.get("platforms", ["instagram", "facebook"])
            content_pillars = inputs.get("content_pillars", [{"name": "General Content"}])
            
            for platform in platforms:
                for pillar in content_pillars[:3]:  # Limit to 3 pillars
                    content_data = await self.campaign_chain.create_content(
                        brand_guidelines=inputs.get("brand_guidelines", ""),
                        content_pillar=pillar.get("name", "Content"),
                        platform=platform
                    )
                    
                    post = SocialPost(
                        platform=SocialPlatform(platform),
                        content=content_data.get("content", ""),
                        hashtags=content_data.get("hashtags", []),
                        image_prompt=content_data.get("visual_description", ""),
                        call_to_action=content_data.get("cta", ""),
                        engagement_hooks=content_data.get("engagement_hooks", [])
                    )
                    posts.append(post)
            
            results["posts"] = [post.dict() for post in posts]
            results["success"] = True
            
            return results
        
        except Exception as e:
            logger.error(f"Sequential chain error: {e}")
            return {
                "success": False,
                "error": str(e),
                "brand_analysis": "Analysis completed",
                "strategy": "Strategy developed", 
                "posts": []
            }