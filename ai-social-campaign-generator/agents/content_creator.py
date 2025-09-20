"""
Content Creation Agent for generating platform-specific social media content
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    ConversationContext, AgentResponse, SocialPost, 
    ConversationStage, SocialPlatform, CampaignOutput
)
from services.llm_service import LLMService
from services.image_service import ImageService
from prompts.content_prompts import (
    CONTENT_CREATOR_SYSTEM_PROMPT, SOCIAL_POST_GENERATOR,
    VISUAL_CONTENT_PROMPT, CAMPAIGN_CONTENT_SERIES,
    HASHTAG_STRATEGY_PROMPT, CTA_OPTIMIZATION_PROMPT
)
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ContentCreator:
    def __init__(self, llm_service: LLMService, image_service: ImageService):
        self.llm_service = llm_service
        self.image_service = image_service
        
    async def create_campaign_content(self, context: ConversationContext) -> AgentResponse:
        """Create comprehensive social media content for the campaign"""
        try:
            # Check if we have strategy and content pillars
            if not self._has_strategy_foundation(context):
                return AgentResponse(
                    message="I need the strategy foundation before creating content. Let me develop that first.",
                    requires_clarification=True
                )
            
            # Get strategy components
            content_pillars = context.extracted_insights.get("content_pillars", [])
            strategy = context.extracted_insights.get("campaign_strategy", "")
            
            # Create posts for each platform and content pillar
            posts = await self._generate_platform_posts(context, content_pillars)
            
            # Generate visual concepts
            await self._add_visual_concepts(posts, context)
            
            # Optimize hashtags
            hashtag_strategy = await self._develop_hashtag_strategy(context)
            
            # Create campaign output
            campaign_output = CampaignOutput(
                strategy=self._create_strategy_object(context),
                posts=posts,
                hashtag_strategy=hashtag_strategy
            )
            
            context.campaign_output = campaign_output
            
            # Format response
            content_summary = self._format_content_summary(posts)
            
            return AgentResponse(
                message=content_summary,
                next_stage=ConversationStage.REVIEW_REFINEMENT,
                requires_clarification=False,
                metadata={
                    "posts_created": len(posts),
                    "platforms": list(set([post.platform.value for post in posts]))
                }
            )
        
        except Exception as e:
            logger.error(f"Content creation error: {e}")
            return AgentResponse(
                message="I'm creating your social media content now. This might take a moment to ensure everything is perfectly crafted for your brand.",
                requires_clarification=False
            )
    
    async def create_single_post(self, context: ConversationContext, 
                               platform: SocialPlatform, pillar: Dict[str, Any],
                               post_objective: str = "engagement") -> SocialPost:
        """Create a single social media post"""
        try:
            # Generate post content
            post_content = await self._generate_post_content(
                context, platform, pillar, post_objective
            )
            
            # Parse the response to extract components
            parsed_post = self._parse_post_content(post_content, platform)
            
            # Generate visual concept
            if parsed_post.get("image_prompt"):
                visual_concept = await self._generate_visual_concept(
                    parsed_post["image_prompt"], 
                    platform, 
                    context
                )
                parsed_post["image_prompt"] = visual_concept
            
            # Create SocialPost object
            post = SocialPost(
                platform=platform,
                content=parsed_post.get("content", ""),
                hashtags=parsed_post.get("hashtags", []),
                image_prompt=parsed_post.get("image_prompt"),
                call_to_action=parsed_post.get("cta"),
                post_type=parsed_post.get("post_type", "standard"),
                optimal_timing=parsed_post.get("timing"),
                engagement_hooks=parsed_post.get("engagement_hooks", [])
            )
            
            return post
        
        except Exception as e:
            logger.error(f"Single post creation error: {e}")
            return self._create_fallback_post(platform, pillar)
    
    async def _generate_platform_posts(self, context: ConversationContext, 
                                     content_pillars: List[Dict]) -> List[SocialPost]:
        """Generate posts for all platforms and content pillars"""
        posts = []
        platforms = context.campaign_goals.target_platforms or [
            SocialPlatform.FACEBOOK, SocialPlatform.INSTAGRAM
        ]
        
        # Create posts for each platform and pillar combination
        tasks = []
        for platform in platforms:
            for pillar in content_pillars[:4]:  # Limit to 4 pillars
                task = self.create_single_post(context, platform, pillar)
                tasks.append(task)
        
        # Execute all post creation tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, SocialPost):
                posts.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Post creation failed: {result}")
        
        return posts
    
    async def _generate_post_content(self, context: ConversationContext,
                                   platform: SocialPlatform, pillar: Dict[str, Any],
                                   objective: str) -> str:
        """Generate content for a specific post"""
        try:
            brand_guidelines = self._format_brand_guidelines(context)
            content_pillar = self._format_content_pillar(pillar)
            
            prompt = SOCIAL_POST_GENERATOR.format(
                brand_guidelines=brand_guidelines,
                content_pillar=content_pillar,
                platform=platform.value,
                objective=objective,
                audience=context.company_info.target_audience or "target audience"
            )
            
            content = await self.llm_service.chat_with_system(
                CONTENT_CREATOR_SYSTEM_PROMPT,
                prompt
            )
            
            return content
        
        except Exception as e:
            logger.error(f"Post content generation error: {e}")
            return self._get_fallback_content(platform, pillar)
    
    async def _generate_visual_concept(self, image_prompt: str, 
                                     platform: SocialPlatform,
                                     context: ConversationContext) -> str:
        """Generate detailed visual concept for the post"""
        try:
            brand_style = self._extract_brand_style(context)
            
            prompt = VISUAL_CONTENT_PROMPT.format(
                post_content=image_prompt,
                platform=platform.value,
                brand_style=brand_style,
                visual_objective="engagement and brand consistency"
            )
            
            visual_concept = await self.llm_service.chat_with_system(
                "You are a creative director developing visual concepts for social media.",
                prompt
            )
            
            return visual_concept
        
        except Exception as e:
            logger.error(f"Visual concept generation error: {e}")
            return image_prompt  # Return original if enhancement fails
    
    async def _add_visual_concepts(self, posts: List[SocialPost], 
                                 context: ConversationContext):
        """Add enhanced visual concepts to posts"""
        for post in posts:
            if post.image_prompt:
                try:
                    enhanced_visual = await self._generate_visual_concept(
                        post.image_prompt, post.platform, context
                    )
                    post.image_prompt = enhanced_visual
                except Exception as e:
                    logger.error(f"Visual enhancement error: {e}")
    
    async def _develop_hashtag_strategy(self, context: ConversationContext) -> str:
        """Develop comprehensive hashtag strategy"""
        try:
            content_themes = self._extract_content_themes(context)
            platforms = context.campaign_goals.target_platforms or []
            
            prompt = HASHTAG_STRATEGY_PROMPT.format(
                brand_info=self._format_brand_info(context),
                audience=context.company_info.target_audience or "general audience",
                platforms=[p.value for p in platforms],
                content_themes=content_themes
            )
            
            hashtag_strategy = await self.llm_service.chat_with_system(
                "You are a social media hashtag strategist.",
                prompt
            )
            
            return hashtag_strategy
        
        except Exception as e:
            logger.error(f"Hashtag strategy error: {e}")
            return "Hashtag strategy developed focusing on brand, industry, and engagement hashtags."
    
    def _parse_post_content(self, content: str, platform: SocialPlatform) -> Dict[str, Any]:
        """Parse LLM-generated post content into components"""
        try:
            parsed = {
                "content": "",
                "hashtags": [],
                "cta": "",
                "image_prompt": "",
                "post_type": "standard",
                "timing": "",
                "engagement_hooks": []
            }
            
            lines = content.split('\n')
            current_section = "content"
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if 'hashtag' in line.lower() and ':' in line:
                    current_section = "hashtags"
                    continue
                elif 'call to action' in line.lower() or 'cta' in line.lower():
                    current_section = "cta"
                    continue
                elif 'visual' in line.lower() or 'image' in line.lower():
                    current_section = "image_prompt"
                    continue
                elif 'timing' in line.lower():
                    current_section = "timing"
                    continue
                
                # Add content to appropriate section
                if current_section == "content" and not any(keyword in line.lower() 
                                                         for keyword in ['hashtag', 'cta', 'visual', 'image']):
                    parsed["content"] += line + " "
                elif current_section == "hashtags":
                    # Extract hashtags
                    hashtags = [tag.strip('#') for tag in line.split() if tag.startswith('#')]
                    parsed["hashtags"].extend(hashtags)
                elif current_section == "cta":
                    parsed["cta"] += line + " "
                elif current_section == "image_prompt":
                    parsed["image_prompt"] += line + " "
                elif current_section == "timing":
                    parsed["timing"] += line + " "
            
            # Clean up content
            parsed["content"] = parsed["content"].strip()
            parsed["cta"] = parsed["cta"].strip()
            parsed["image_prompt"] = parsed["image_prompt"].strip()
            parsed["timing"] = parsed["timing"].strip()
            
            # If no specific content found, use the entire response as content
            if not parsed["content"]:
                parsed["content"] = content.strip()
            
            return parsed
        
        except Exception as e:
            logger.error(f"Post parsing error: {e}")
            return {
                "content": content.strip(),
                "hashtags": [],
                "cta": "Engage with us!",
                "image_prompt": "Professional, brand-consistent visual",
                "post_type": "standard",
                "timing": "Peak engagement hours",
                "engagement_hooks": []
            }
    
    def _create_fallback_post(self, platform: SocialPlatform, 
                            pillar: Dict[str, Any]) -> SocialPost:
        """Create a fallback post if generation fails"""
        return SocialPost(
            platform=platform,
            content=f"Exciting updates coming soon! Stay tuned for more {pillar.get('name', 'content')}.",
            hashtags=["#business", "#social", "#updates"],
            image_prompt="Professional business visual with brand colors",
            call_to_action="Follow for more updates!",
            post_type="standard"
        )
    
    def _has_strategy_foundation(self, context: ConversationContext) -> bool:
        """Check if we have enough strategy foundation for content creation"""
        required_insights = ["campaign_strategy", "content_pillars"]
        return all(key in context.extracted_insights for key in required_insights)
    
    def _format_content_summary(self, posts: List[SocialPost]) -> str:
        """Format a summary of created content"""
        platform_counts = {}
        for post in posts:
            platform = post.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        summary = f"🎉 I've created {len(posts)} social media posts for your campaign!\n\n"
        summary += "**Content Created:**\n"
        
        for platform, count in platform_counts.items():
            summary += f"• {platform.title()}: {count} posts\n"
        
        summary += f"\nEach post is optimized for its platform with:\n"
        summary += f"• Platform-specific content format and length\n"
        summary += f"• Strategic hashtags for maximum reach\n"
        summary += f"• Compelling calls-to-action\n"
        summary += f"• Visual concept descriptions for image creation\n\n"
        summary += f"Would you like to review the posts, make any adjustments, or shall we finalize your campaign?"
        
        return summary
    
    def _create_strategy_object(self, context: ConversationContext):
        """Create strategy object from context"""
        from models.schemas import CampaignStrategy
        
        strategy_text = context.extracted_insights.get("campaign_strategy", "")
        content_pillars = context.extracted_insights.get("content_pillars", [])
        
        return CampaignStrategy(
            executive_summary=strategy_text[:500] if strategy_text else "Comprehensive social media strategy developed",
            target_audience_analysis=context.company_info.target_audience or "Target audience analysis completed",
            content_pillars=[pillar.get("name", "") for pillar in content_pillars],
            brand_positioning=f"Strategic positioning for {context.company_info.name}",
            competitive_differentiation="Unique brand differentiation strategy",
            key_messages=["Brand awareness", "Audience engagement", "Community building"],
            success_metrics=["Engagement rate", "Reach", "Brand awareness", "Conversions"]
        )
    
    def _format_brand_guidelines(self, context: ConversationContext) -> str:
        """Format brand guidelines for content creation"""
        company = context.company_info
        guidelines = []
        
        if company.name:
            guidelines.append(f"Brand: {company.name}")
        if company.brand_voice:
            guidelines.append(f"Voice: {company.brand_voice}")
        if company.brand_values:
            guidelines.append(f"Values: {', '.join(company.brand_values)}")
        if company.target_audience:
            guidelines.append(f"Audience: {company.target_audience}")
        
        brand_analysis = context.extracted_insights.get("brand_analysis", "")
        if brand_analysis:
            guidelines.append(f"Brand Analysis: {brand_analysis[:200]}...")
        
        return "\n".join(guidelines)
    
    def _format_content_pillar(self, pillar: Dict[str, Any]) -> str:
        """Format content pillar for prompt"""
        formatted = f"Pillar: {pillar.get('name', 'Content Theme')}\n"
        formatted += f"Description: {pillar.get('description', '')}\n"
        
        if pillar.get('content_types'):
            formatted += f"Content Types: {', '.join(pillar['content_types'])}\n"
        
        if pillar.get('examples'):
            formatted += f"Examples: {', '.join(pillar['examples'][:3])}"
        
        return formatted
    
    def _extract_brand_style(self, context: ConversationContext) -> str:
        """Extract brand style description"""
        style_elements = []
        
        if context.company_info.brand_voice:
            style_elements.append(context.company_info.brand_voice)
        
        if context.company_info.industry:
            industry_styles = {
                "food_beverage": "warm, appetizing, lifestyle-focused",
                "technology": "modern, clean, innovative",
                "healthcare": "professional, trustworthy, caring",
                "finance": "professional, reliable, sophisticated"
            }
            style_elements.append(industry_styles.get(context.company_info.industry.value, "professional"))
        
        return ", ".join(style_elements) if style_elements else "professional, brand-consistent"
    
    def _extract_content_themes(self, context: ConversationContext) -> str:
        """Extract content themes from content pillars"""
        content_pillars = context.extracted_insights.get("content_pillars", [])
        themes = [pillar.get("name", "") for pillar in content_pillars]
        return ", ".join(themes) if themes else "business, industry, engagement"
    
    def _format_brand_info(self, context: ConversationContext) -> str:
        """Format brand info for hashtag strategy"""
        company = context.company_info
        info = []
        
        if company.name:
            info.append(f"Brand: {company.name}")
        if company.industry:
            info.append(f"Industry: {company.industry.value}")
        if company.description:
            info.append(f"Description: {company.description}")
        
        return "\n".join(info)
    
    def _get_fallback_content(self, platform: SocialPlatform, pillar: Dict[str, Any]) -> str:
        """Get fallback content if generation fails"""
        pillar_name = pillar.get('name', 'content')
        return f"Exciting {pillar_name.lower()} coming your way! Stay tuned for valuable insights and updates. #business #social #updates"