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
        """Generate image using Hugging Face DALL-E Mini API (free alternative)"""
        try:
            enhanced_prompt = self._enhance_prompt(prompt, style, platform)
            logger.info(f"Generating image with Hugging Face API for prompt: {enhanced_prompt[:50]}...")

            # Use Hugging Face Inference API for DALL-E Mini (free)
            url = "https://api-inference.huggingface.co/models/dalle-mini/dalle-mini"

            headers = {
                "Authorization": f"Bearer {self.api_key}",  # Use your API key as HF token
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": enhanced_prompt[:100],  # Limit prompt length
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    logger.info(f"Hugging Face API response status: {response.status}")

                    if response.status == 200:
                        # Response should be binary image data
                        image_bytes = await response.read()
                        logger.info(f"Received image data: {len(image_bytes)} bytes")

                        # Convert to base64
                        import base64
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        return f"data:image/png;base64,{image_base64}"

                    elif response.status == 503:
                        # Model loading, try fallback
                        logger.warning("Model loading, trying alternative API...")
                        return await self._generate_with_pollinations(enhanced_prompt, style, platform)

                    else:
                        error_text = await response.text()
                        logger.error(f"Hugging Face API error {response.status}: {error_text}")
                        return await self._generate_with_pollinations(enhanced_prompt, style, platform)

        except Exception as e:
            logger.error(f"Hugging Face image generation error: {e}")
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