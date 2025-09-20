"""
Visual Content Agent for generating and managing social media visuals
"""

from typing import List, Dict, Any, Optional
from models.schemas import SocialPost, SocialPlatform, ConversationContext
from services.image_service import ImageService
from services.llm_service import LLMService
import asyncio
import logging

logger = logging.getLogger(__name__)

class VisualAgent:
    def __init__(self, image_service: ImageService, llm_service: LLMService):
        self.image_service = image_service
        self.llm_service = llm_service
        
    async def generate_visuals_for_posts(self, posts: List[SocialPost], 
                                       context: ConversationContext) -> List[SocialPost]:
        """Generate visual content for all posts"""
        try:
            # Create tasks for concurrent image generation
            tasks = []
            for post in posts:
                if post.image_prompt:
                    task = self._generate_post_visual(post, context)
                    tasks.append(task)
            
            # Execute all image generation tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update posts with generated images
            updated_posts = []
            result_index = 0
            
            for post in posts:
                if post.image_prompt:
                    if result_index < len(results) and not isinstance(results[result_index], Exception):
                        post.image_url = results[result_index]
                    result_index += 1
                updated_posts.append(post)
            
            return updated_posts
        
        except Exception as e:
            logger.error(f"Batch visual generation error: {e}")
            return posts  # Return original posts if generation fails
    
    async def _generate_post_visual(self, post: SocialPost, 
                                  context: ConversationContext) -> Optional[str]:
        """Generate visual for a single post"""
        try:
            # Enhance the image prompt with brand context
            enhanced_prompt = await self._enhance_image_prompt(
                post.image_prompt, post.platform, context
            )
            
            # Determine visual style based on brand and platform
            visual_style = self._determine_visual_style(context, post.platform)
            
            # Generate the image
            image_url = await self.image_service.generate_image(
                prompt=enhanced_prompt,
                style=visual_style,
                platform=post.platform.value
            )
            
            return image_url
        
        except Exception as e:
            logger.error(f"Post visual generation error: {e}")
            return None
    
    async def _enhance_image_prompt(self, original_prompt: str, 
                                  platform: SocialPlatform,
                                  context: ConversationContext) -> str:
        """Enhance image prompt with brand and platform context"""
        try:
            enhancement_prompt = f"""
            Enhance this image prompt for {platform.value} social media post:
            
            Original prompt: {original_prompt}
            
            Brand context:
            - Company: {context.company_info.name}
            - Industry: {context.company_info.industry or 'general business'}
            - Brand voice: {context.company_info.brand_voice or 'professional'}
            - Target audience: {context.company_info.target_audience or 'general audience'}
            
            Platform specifications:
            - Platform: {platform.value}
            - Optimal dimensions: {self._get_platform_dimensions(platform)}
            
            Enhance the prompt to:
            1. Include brand-appropriate visual elements
            2. Optimize for the specific platform
            3. Appeal to the target audience
            4. Maintain professional quality
            5. Include relevant visual style cues
            
            Return only the enhanced prompt, nothing else.
            """
            
            enhanced = await self.llm_service.chat_with_system(
                "You are a visual content specialist optimizing image prompts for social media.",
                enhancement_prompt
            )
            
            return enhanced.strip()
        
        except Exception as e:
            logger.error(f"Prompt enhancement error: {e}")
            return original_prompt  # Return original if enhancement fails
    
    def _determine_visual_style(self, context: ConversationContext, 
                              platform: SocialPlatform) -> str:
        """Determine appropriate visual style based on brand and platform"""
        # Base style on industry
        industry_styles = {
            "food_beverage": "vibrant",
            "technology": "modern", 
            "healthcare": "professional",
            "finance": "professional",
            "retail": "vibrant",
            "education": "professional",
            "real_estate": "elegant",
            "automotive": "modern",
            "beauty_fashion": "elegant",
            "fitness_wellness": "vibrant",
            "entertainment": "vibrant"
        }
        
        base_style = "professional"  # Default
        if context.company_info.industry:
            base_style = industry_styles.get(context.company_info.industry.value, "professional")
        
        # Adjust for platform
        platform_adjustments = {
            SocialPlatform.INSTAGRAM: "vibrant",
            SocialPlatform.LINKEDIN: "professional", 
            SocialPlatform.TIKTOK: "vibrant",
            SocialPlatform.FACEBOOK: "casual",
            SocialPlatform.TWITTER: "modern",
            SocialPlatform.YOUTUBE: "engaging"
        }
        
        platform_style = platform_adjustments.get(platform, base_style)
        
        # Combine with brand voice if available
        if context.company_info.brand_voice:
            brand_voice = context.company_info.brand_voice.lower()
            if "fun" in brand_voice or "playful" in brand_voice:
                return "vibrant"
            elif "professional" in brand_voice or "corporate" in brand_voice:
                return "professional"
            elif "elegant" in brand_voice or "luxury" in brand_voice:
                return "elegant"
        
        return platform_style
    
    def _get_platform_dimensions(self, platform: SocialPlatform) -> str:
        """Get platform-specific dimension information"""
        dimensions = {
            SocialPlatform.INSTAGRAM: "1080x1080 (square) or 1080x1920 (story)",
            SocialPlatform.FACEBOOK: "1200x630 (landscape)",
            SocialPlatform.LINKEDIN: "1200x627 (landscape)",
            SocialPlatform.TWITTER: "1200x675 (landscape)",
            SocialPlatform.TIKTOK: "1080x1920 (vertical)",
            SocialPlatform.YOUTUBE: "1280x720 (16:9)",
            SocialPlatform.PINTEREST: "1000x1500 (vertical)"
        }
        
        return dimensions.get(platform, "1080x1080 (square)")
    
    async def generate_carousel_visuals(self, post: SocialPost, 
                                      context: ConversationContext,
                                      num_slides: int = 3) -> List[Optional[str]]:
        """Generate multiple images for carousel posts"""
        try:
            # Create variations of the base prompt for carousel slides
            carousel_prompts = await self._create_carousel_prompts(
                post.image_prompt, num_slides, context
            )
            
            # Generate images for each slide
            visual_style = self._determine_visual_style(context, post.platform)
            
            tasks = [
                self.image_service.generate_image(
                    prompt=prompt,
                    style=visual_style,
                    platform=post.platform.value
                )
                for prompt in carousel_prompts
            ]
            
            images = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid image URLs
            valid_images = [
                img for img in images 
                if not isinstance(img, Exception) and img is not None
            ]
            
            return valid_images
        
        except Exception as e:
            logger.error(f"Carousel visual generation error: {e}")
            return []
    
    async def _create_carousel_prompts(self, base_prompt: str, 
                                     num_slides: int,
                                     context: ConversationContext) -> List[str]:
        """Create varied prompts for carousel slides"""
        try:
            variation_prompt = f"""
            Create {num_slides} varied image prompts based on this base concept:
            
            Base prompt: {base_prompt}
            
            Create variations that:
            1. Maintain the core concept and brand consistency
            2. Show different angles or aspects of the topic
            3. Work well together as a carousel series
            4. Each tell part of a visual story
            
            Format as:
            Slide 1: [prompt]
            Slide 2: [prompt]
            Slide 3: [prompt]
            """
            
            response = await self.llm_service.chat_with_system(
                "You are a visual storytelling expert creating carousel content.",
                variation_prompt
            )
            
            # Parse the response to extract individual prompts
            prompts = self._parse_carousel_prompts(response, num_slides)
            
            return prompts
        
        except Exception as e:
            logger.error(f"Carousel prompt creation error: {e}")
            # Return variations of the base prompt as fallback
            return [f"{base_prompt} - variation {i+1}" for i in range(num_slides)]
    
    def _parse_carousel_prompts(self, response: str, num_slides: int) -> List[str]:
        """Parse carousel prompts from LLM response"""
        try:
            prompts = []
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.lower().startswith('slide') and ':' in line:
                    prompt = line.split(':', 1)[1].strip()
                    prompts.append(prompt)
            
            # Ensure we have enough prompts
            while len(prompts) < num_slides:
                prompts.append(f"Additional visual variation {len(prompts) + 1}")
            
            return prompts[:num_slides]
        
        except Exception as e:
            logger.error(f"Carousel prompt parsing error: {e}")
            return [f"Visual variation {i+1}" for i in range(num_slides)]
    
    async def generate_brand_style_guide(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate visual brand style guidelines"""
        try:
            style_prompt = f"""
            Create visual brand guidelines for social media content based on:
            
            Company: {context.company_info.name}
            Industry: {context.company_info.industry or 'general business'}
            Brand voice: {context.company_info.brand_voice or 'professional'}
            Target audience: {context.company_info.target_audience or 'general audience'}
            Brand values: {', '.join(context.company_info.brand_values or ['quality', 'trust'])}
            
            Provide guidelines for:
            1. Color palette recommendations
            2. Typography style
            3. Photography style
            4. Visual elements and patterns
            5. Logo usage
            6. Platform-specific adaptations
            
            Format as structured guidelines that can be used for consistent visual content creation.
            """
            
            guidelines = await self.llm_service.chat_with_system(
                "You are a brand designer creating visual style guidelines for social media.",
                style_prompt
            )
            
            return {
                "guidelines": guidelines,
                "color_palette": self._extract_color_recommendations(guidelines),
                "typography": self._extract_typography_recommendations(guidelines),
                "photography_style": self._extract_photography_style(guidelines)
            }
        
        except Exception as e:
            logger.error(f"Style guide generation error: {e}")
            return self._get_default_style_guide(context)
    
    def _extract_color_recommendations(self, guidelines: str) -> List[str]:
        """Extract color recommendations from style guidelines"""
        # Simple extraction - in production, would use more sophisticated parsing
        colors = []
        if "blue" in guidelines.lower():
            colors.append("blue")
        if "green" in guidelines.lower():
            colors.append("green")
        if "red" in guidelines.lower():
            colors.append("red")
        
        return colors if colors else ["blue", "white", "gray"]
    
    def _extract_typography_recommendations(self, guidelines: str) -> str:
        """Extract typography recommendations"""
        if "modern" in guidelines.lower():
            return "Modern, clean sans-serif fonts"
        elif "traditional" in guidelines.lower():
            return "Traditional, serif fonts"
        else:
            return "Professional, readable fonts"
    
    def _extract_photography_style(self, guidelines: str) -> str:
        """Extract photography style recommendations"""
        if "lifestyle" in guidelines.lower():
            return "Lifestyle and candid photography"
        elif "professional" in guidelines.lower():
            return "Professional, polished imagery"
        else:
            return "Clean, brand-consistent photography"
    
    def _get_default_style_guide(self, context: ConversationContext) -> Dict[str, Any]:
        """Get default style guide if generation fails"""
        return {
            "guidelines": "Professional visual style with brand consistency",
            "color_palette": ["blue", "white", "gray"],
            "typography": "Modern, readable fonts",
            "photography_style": "Professional, high-quality imagery"
        }