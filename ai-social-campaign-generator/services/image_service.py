import requests
import base64
import json
from typing import Optional, Dict, Any
from config.settings import settings
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.api_url = settings.image_api_url
        self.api_key = settings.image_api_key
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    async def generate_image(self, prompt: str, style: Optional[str] = None,
                           platform: Optional[str] = None) -> Optional[str]:
        """Generate image from text prompt using available APIs"""
        try:
            # Log the attempt
            logger.info(f"Starting image generation for prompt: {prompt[:50]}...")
            logger.info(f"API key available: {bool(self.api_key)}")

            # Use Gemini 2.5 Flash if API key is available
            if self.api_key:
                result = await self._generate_with_gemini(prompt, style, platform)
                if result:
                    logger.info("Successfully generated image with Gemini")
                    return result
                else:
                    logger.warning("Gemini generation failed, trying custom API")
                    # Try custom API as fallback
                    if self.api_url:
                        return await self._generate_with_custom_api(prompt, style, platform)
                    else:
                        logger.warning("No custom API URL configured")
                        return None
            else:
                logger.warning("No API key configured for image generation")
                return None

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return None
    
    
    async def _generate_with_gemini(self, prompt: str, style: Optional[str] = None,
                                  platform: Optional[str] = None) -> Optional[str]:
        """Generate image using Gemini 2.5 Flash Image Preview API (official implementation)"""
        try:
            enhanced_prompt = self._enhance_prompt(prompt, style, platform)
            logger.info(f"Generating image with Gemini 2.5 Flash Image Preview: {enhanced_prompt[:50]}...")

            # Official Gemini 2.5 Flash Image Preview API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={self.api_key}"

            # Correct payload structure based on official documentation
            payload = {
                "contents": [{
                    "parts": [{
                        "text": enhanced_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 1.0,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 4096,
                    "responseMimeType": "application/json"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=120) as response:
                    logger.info(f"Gemini Image API response status: {response.status}")

                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Gemini response structure: {list(result.keys())}")

                        # Check for generated images in the response
                        if 'candidates' in result and result['candidates']:
                            candidate = result['candidates'][0]
                            logger.info(f"Candidate structure: {list(candidate.keys())}")

                            # Look for content with parts containing inline data (images)
                            if 'content' in candidate and 'parts' in candidate['content']:
                                for part in candidate['content']['parts']:
                                    logger.info(f"Part structure: {list(part.keys())}")

                                    # Check for inline data (base64 encoded image)
                                    if 'inlineData' in part:
                                        inline_data = part['inlineData']
                                        if 'data' in inline_data:
                                            image_data = inline_data['data']
                                            mime_type = inline_data.get('mimeType', 'image/png')
                                            logger.info(f"Found Gemini image: {len(image_data)} chars, type: {mime_type}")
                                            return f"data:{mime_type};base64,{image_data}"

                        # If no image found in Gemini response, try fallback
                        logger.warning("No image data found in Gemini response, trying fallback...")
                        logger.info(f"Full response for debugging: {result}")
                        return await self._generate_with_pollinations(enhanced_prompt, style, platform)

                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini API error {response.status}: {error_text}")
                        # Try fallback API
                        return await self._generate_with_pollinations(enhanced_prompt, style, platform)

        except Exception as e:
            logger.error(f"Gemini image generation error: {e}")
            # Try fallback API
            return await self._generate_with_pollinations(enhanced_prompt, style, platform)

    async def _generate_with_pollinations(self, prompt: str, style: Optional[str] = None,
                                        platform: Optional[str] = None) -> Optional[str]:
        """Generate image using Pollinations.ai (free, no API key required)"""
        try:
            enhanced_prompt = self._enhance_prompt(prompt, style, platform)
            logger.info(f"Generating image with Pollinations.ai for prompt: {enhanced_prompt[:50]}...")

            # Pollinations.ai free API - no key required
            import urllib.parse
            encoded_prompt = urllib.parse.quote(enhanced_prompt[:200])

            # Add model and style parameters
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=1024&nologo=true&enhance=true"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=120) as response:
                    logger.info(f"Pollinations API response status: {response.status}")

                    if response.status == 200:
                        # Response is binary image data
                        image_bytes = await response.read()
                        logger.info(f"Received image data: {len(image_bytes)} bytes")

                        # Convert to base64
                        import base64
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        return f"data:image/jpeg;base64,{image_base64}"

                    else:
                        error_text = await response.text()
                        logger.error(f"Pollinations API error {response.status}: {error_text}")
                        return None

        except Exception as e:
            logger.error(f"Pollinations image generation error: {e}")
            return None

    async def _generate_with_custom_api(self, prompt: str, style: Optional[str] = None,
                                      platform: Optional[str] = None) -> Optional[str]:
        """Generate image using custom API (fallback method)"""
        try:
            enhanced_prompt = self._enhance_prompt(prompt, style, platform)

            payload = {
                "prompt": enhanced_prompt,
                "platform": platform,
                "style": style
            }

            # Add platform-specific dimensions
            if platform:
                payload.update(self._get_platform_dimensions(platform))

            response = self.session.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=settings.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("image_url")
            else:
                logger.error(f"Custom API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Custom API image generation error: {e}")
            return None
    
    def _enhance_prompt(self, prompt: str, style: Optional[str] = None, 
                       platform: Optional[str] = None) -> str:
        """Enhance the image prompt based on style and platform"""
        enhanced = prompt
        
        # Add style specifications
        if style:
            style_modifiers = {
                "professional": "professional, clean, corporate style",
                "casual": "casual, friendly, approachable style",
                "modern": "modern, minimalist, contemporary design",
                "vibrant": "vibrant colors, energetic, eye-catching",
                "elegant": "elegant, sophisticated, luxury aesthetic"
            }
            if style.lower() in style_modifiers:
                enhanced += f", {style_modifiers[style.lower()]}"
        
        # Add platform-specific considerations
        platform_specs = {
            "instagram": "Instagram-optimized, square format, visually striking",
            "facebook": "Facebook-optimized, engaging, shareable",
            "linkedin": "LinkedIn-optimized, professional, business-appropriate",
            "twitter": "Twitter-optimized, attention-grabbing, concise visual",
            "tiktok": "TikTok-optimized, vertical format, trendy, youth-oriented"
        }
        
        if platform and platform.lower() in platform_specs:
            enhanced += f", {platform_specs[platform.lower()]}"
        
        # Add general quality modifiers
        enhanced += ", high quality, professional photography, good lighting"
        
        return enhanced
    
    def _get_platform_dimensions(self, platform: str) -> Dict[str, int]:
        """Get optimal image dimensions for each platform"""
        dimensions = {
            "instagram": {"width": 1080, "height": 1080},  # Square post
            "facebook": {"width": 1200, "height": 630},    # Landscape
            "linkedin": {"width": 1200, "height": 627},    # Landscape
            "twitter": {"width": 1200, "height": 675},     # Landscape
            "tiktok": {"width": 1080, "height": 1920},     # Vertical
            "youtube": {"width": 1280, "height": 720},     # 16:9
            "pinterest": {"width": 1000, "height": 1500}   # Vertical
        }
        
        return dimensions.get(platform.lower(), {"width": 1024, "height": 1024})
    
    async def generate_carousel_images(self, prompts: list[str], 
                                     style: Optional[str] = None,
                                     platform: Optional[str] = None) -> list[Optional[str]]:
        """Generate multiple images for carousel posts"""
        images = []
        for prompt in prompts:
            image_url = await self.generate_image(prompt, style, platform)
            images.append(image_url)
        return images
    
    def get_platform_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific image specifications"""
        specs = {
            "instagram": {
                "feed_post": {"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
                "story": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
                "reel": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"}
            },
            "facebook": {
                "post": {"width": 1200, "height": 630, "aspect_ratio": "1.91:1"},
                "story": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"}
            },
            "linkedin": {
                "post": {"width": 1200, "height": 627, "aspect_ratio": "1.91:1"},
                "article": {"width": 1200, "height": 627, "aspect_ratio": "1.91:1"}
            },
            "twitter": {
                "post": {"width": 1200, "height": 675, "aspect_ratio": "16:9"},
                "header": {"width": 1500, "height": 500, "aspect_ratio": "3:1"}
            }
        }
        
        return specs.get(platform.lower(), {})