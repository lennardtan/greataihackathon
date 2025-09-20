"""
Main Conversational AI Orchestrator for Social Media Campaign Generation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
import logging
import re

from models.schemas import (
    ConversationContext, ConversationMessage, MessageRole, 
    ConversationStage, AgentResponse, CompanyInfo, CampaignGoals,
    Industry, CampaignObjective, SocialPlatform
)
from services.llm_service import LLMService
from services.image_service import ImageService
from agents.brand_analyzer import BrandAnalyzer
from agents.strategy_agent import StrategyAgent
from agents.content_creator import ContentCreator
from agents.visual_agent import VisualAgent

logger = logging.getLogger(__name__)

class CampaignOrchestrator:
    """
    Main orchestrator that manages the conversational flow for social media campaign generation.
    Acts like a personal marketing consultant through natural conversation.
    """
    
    def __init__(self, llm_service: LLMService, image_service: ImageService):
        self.llm_service = llm_service
        self.image_service = image_service
        
        # Initialize specialized agents
        self.brand_analyzer = BrandAnalyzer(llm_service)
        self.strategy_agent = StrategyAgent(llm_service)
        self.content_creator = ContentCreator(llm_service, image_service)
        self.visual_agent = VisualAgent(image_service, llm_service)
        
        # Conversation management
        self.active_contexts: Dict[str, ConversationContext] = {}
        
    async def start_conversation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new conversation session"""
        session_id = str(uuid.uuid4())
        
        # Pre-populate with ProteinRX information
        from models.schemas import Industry, CampaignObjective, SocialPlatform

        proteinrx_company = CompanyInfo(
            name="ProteinRX",
            industry=Industry.FITNESS_WELLNESS,
            description="Health & Fitness - Protein Smoothie Drinks",
            target_audience="Gym-goers and fitness enthusiasts (20-45 years old)",
            brand_voice="Luxury and strong",
            unique_selling_points=["Convenient canned format for accessibility", "Available everywhere"],
            competitors=["Traditional protein powder brands"]
        )

        proteinrx_goals = CampaignGoals(
            primary_objective=CampaignObjective.BRAND_AWARENESS,
            target_platforms=[SocialPlatform.INSTAGRAM]
        )

        context = ConversationContext(
            session_id=session_id,
            current_stage=ConversationStage.GREETING,
            messages=[],
            company_info=proteinrx_company,
            campaign_goals=proteinrx_goals,
            extracted_insights={
                "brand_assets": {
                    "colors": "Red and black",
                    "font": "Lato",
                    "logo": "Dumbbell symbol"
                }
            },
            pending_questions=[],
            user_preferences={}
        )
        
        self.active_contexts[session_id] = context
        
        # Generate initial greeting
        greeting = await self._generate_greeting()
        
        # Add to conversation history
        await self._add_message(context, MessageRole.ASSISTANT, greeting)
        
        return {
            "session_id": session_id,
            "message": greeting,
            "stage": ConversationStage.GREETING.value,
            "status": "active"
        }
    
    async def continue_conversation(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Continue an existing conversation"""
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                return {"error": "Session not found", "status": "error"}
            
            # Add user message to history
            await self._add_message(context, MessageRole.USER, user_message)
            
            # Extract information from user message
            await self._extract_information(context, user_message)

            # Check if user provided comprehensive info (force progression)
            if self._user_provided_comprehensive_info(user_message):
                # User provided lots of details, force move to strategy
                context.current_stage = ConversationStage.STRATEGY_DEVELOPMENT

                try:
                    ai_response = await self.llm_service.chat_with_system(
                        "You are a marketing consultant who just received comprehensive business information. Acknowledge what you learned and say you'll create their strategy now.",
                        f"The user provided detailed information: {user_message}\n\nAcknowledge their details and transition to creating their social media strategy."
                    )

                    response = AgentResponse(
                        message=ai_response,
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )
                except Exception:
                    response = AgentResponse(
                        message="Perfect! I have all the information I need about your antique chair business. Let me create a comprehensive social media strategy for you now.",
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )
            else:
                # Determine next action based on current stage
                response = await self._process_conversation_stage(context)
            
            # Add assistant response to history
            await self._add_message(context, MessageRole.ASSISTANT, response.message)
            
            # Update conversation stage if needed
            if response.next_stage:
                context.current_stage = response.next_stage
            
            context.last_updated = datetime.utcnow()
            
            return {
                "session_id": session_id,
                "message": response.message,
                "stage": context.current_stage.value,
                "questions": response.questions,
                "suggestions": response.suggestions,
                "requires_clarification": response.requires_clarification,
                "confidence": response.confidence_score,
                "metadata": response.metadata,
                "status": "active"
            }
        
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            return {
                "session_id": session_id,
                "message": "I apologize, but I encountered an issue. Could you please rephrase your message?",
                "stage": context.current_stage.value if context else "error",
                "status": "error"
            }
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the current conversation state"""
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
            "progress": self._calculate_progress(context)
        }
    
    async def get_campaign_output(self, session_id: str) -> Dict[str, Any]:
        """Get the final campaign output if available"""
        context = self.active_contexts.get(session_id)
        if not context or not context.campaign_output:
            return {"error": "Campaign not ready or session not found"}
        
        return {
            "session_id": session_id,
            "campaign": context.campaign_output.dict(),
            "ready": True
        }
    
    async def _generate_greeting(self) -> str:
        """Generate a personalized greeting message"""
        return "Hi! I'm your dedicated marketing consultant for ProteinRX. I know all about your luxury protein smoothie brand - the convenient canned drinks targeting gym-goers (20-45), your red & black branding with the dumbbell logo, and focus on Instagram for brand awareness. Do you have any specific campaign ideas or themes you'd like to implement for ProteinRX?"
    
    async def _process_conversation_stage(self, context: ConversationContext) -> AgentResponse:
        """Process the conversation based on current stage"""
        stage = context.current_stage
        
        try:
            if stage == ConversationStage.GREETING:
                return await self._handle_greeting_stage(context)
            elif stage == ConversationStage.DISCOVERY:
                return await self._handle_discovery_stage(context)
            elif stage == ConversationStage.BRAND_ANALYSIS:
                return await self.brand_analyzer.analyze_conversation(context)
            elif stage == ConversationStage.STRATEGY_DEVELOPMENT:
                return await self.strategy_agent.develop_strategy(context)
            elif stage == ConversationStage.CONTENT_CREATION:
                return await self.content_creator.create_campaign_content(context)
            elif stage == ConversationStage.REVIEW_REFINEMENT:
                return await self._handle_review_stage(context)
            elif stage == ConversationStage.FINALIZATION:
                return await self._handle_finalization_stage(context)
            else:
                return AgentResponse(
                    message="Let me help you with that. What would you like to know about your social media strategy?",
                    requires_clarification=True
                )
        
        except Exception as e:
            logger.error(f"Stage processing error: {e}")
            return AgentResponse(
                message="I'm analyzing your information. Could you tell me more about your business goals?",
                requires_clarification=True
            )
    
    async def _handle_greeting_stage(self, context: ConversationContext) -> AgentResponse:
        """Handle the initial greeting and campaign idea collection"""
        last_message = context.messages[-1] if context.messages else None

        if last_message and last_message.role == MessageRole.USER:
            # User has provided campaign ideas - generate multiple plans
            user_input = last_message.content

            campaign_generation_prompt = f"""Based on the user's idea "{user_input}", create 3 complete Instagram campaign concepts for ProteinRX protein smoothies.

ProteinRX Brand Details:
- Luxury canned protein smoothies
- Target: Gym-goers and fitness enthusiasts (20-45 years old)
- Brand Colors: Red and Black
- Logo: Dumbbell symbol
- Focus: Convenience, accessibility, premium quality

For each campaign, provide:

## Campaign 1:
**Name:** [Creative campaign name]
**Strategy:** [2-3 sentence description of approach]
**Image Prompt:** [Detailed description for AI image generation including colors, props, mood, setting]
**Instagram Caption:** [Complete caption with emojis and hashtags]

## Campaign 2:
**Name:** [Creative campaign name]
**Strategy:** [2-3 sentence description of approach]
**Image Prompt:** [Detailed description for AI image generation including colors, props, mood, setting]
**Instagram Caption:** [Complete caption with emojis and hashtags]

## Campaign 3:
**Name:** [Creative campaign name]
**Strategy:** [2-3 sentence description of approach]
**Image Prompt:** [Detailed description for AI image generation including colors, props, mood, setting]
**Instagram Caption:** [Complete caption with emojis and hashtags]

Make each campaign distinct and actionable for immediate implementation."""

            try:
                logger.info(f"Attempting to generate campaigns for input: {user_input}")
                ai_response = await self.llm_service.chat_with_system(
                    "You are a specialized marketing consultant for ProteinRX. Generate multiple campaign plans based on the user's input idea.",
                    campaign_generation_prompt
                )

                logger.info(f"Successfully generated response: {ai_response[:100]}...")
                logger.info(f"Full response: {ai_response}")
                return AgentResponse(
                    message=ai_response,
                    next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                    requires_clarification=False
                )
            except Exception as e:
                logger.error(f"Campaign generation error: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {str(e)}")

                # Instead of fallback, let's try a simpler approach
                try:
                    logger.info("Attempting simpler campaign generation...")
                    simple_prompt = f"""Create 3 campaign ideas for ProteinRX protein smoothies based on this user idea: {user_input}

For each campaign, include:
- Campaign Name
- Strategy
- Instagram Caption

Be specific and actionable."""

                    simple_response = await self.llm_service.chat_with_system(
                        "You are a marketing consultant for ProteinRX.",
                        simple_prompt
                    )

                    logger.info(f"Simple approach worked: {simple_response[:100]}...")
                    return AgentResponse(
                        message=simple_response,
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )
                except Exception as e2:
                    logger.error(f"Even simple approach failed: {e2}")
                    return AgentResponse(
                        message=f"I encountered an error generating campaigns. Error: {str(e)}. Let me try a different approach for your '{user_input}' campaign idea.",
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )

        return AgentResponse(
            message="Hi! I'm your dedicated marketing consultant for ProteinRX. I know all about your luxury protein smoothie brand - the convenient canned drinks targeting gym-goers (20-45), your red & black branding with the dumbbell logo, and focus on Instagram for brand awareness. Do you have any specific campaign ideas or themes you'd like to implement for ProteinRX?",
            requires_clarification=True
        )
    
    async def _handle_discovery_stage(self, context: ConversationContext) -> AgentResponse:
        """Handle the discovery phase using brand analyzer"""
        return await self.brand_analyzer.analyze_conversation(context)
    
    async def _handle_review_stage(self, context: ConversationContext) -> AgentResponse:
        """Handle the review and refinement stage"""
        if not context.campaign_output:
            return AgentResponse(
                message="I'm still working on your campaign content. Let me finish that up for you.",
                next_stage=ConversationStage.CONTENT_CREATION,
                requires_clarification=False
            )
        
        posts_count = len(context.campaign_output.posts)
        platforms = list(set([post.platform.value for post in context.campaign_output.posts]))
        
        review_message = f"Perfect! I've created your complete social media campaign with {posts_count} posts across {', '.join(platforms)}. "
        review_message += "Would you like me to:\n\n"
        review_message += "• Show you the specific posts I've created\n"
        review_message += "• Adjust the content style or messaging\n"
        review_message += "• Create additional posts for other platforms\n"
        review_message += "• Finalize everything and provide your campaign package\n\n"
        review_message += "What would you prefer?"
        
        return AgentResponse(
            message=review_message,
            suggestions=[
                "Show me the posts",
                "Adjust the content style", 
                "Add more platforms",
                "Finalize the campaign"
            ],
            next_stage=ConversationStage.FINALIZATION,
            requires_clarification=True
        )
    
    async def _handle_finalization_stage(self, context: ConversationContext) -> AgentResponse:
        """Handle campaign finalization"""
        if not context.campaign_output:
            return AgentResponse(
                message="Let me complete your campaign first.",
                next_stage=ConversationStage.CONTENT_CREATION,
                requires_clarification=False
            )
        
        # Generate final campaign package
        campaign_summary = await self._generate_campaign_summary(context)
        
        return AgentResponse(
            message=campaign_summary,
            requires_clarification=False,
            metadata={"campaign_finalized": True}
        )
    
    async def _extract_information(self, context: ConversationContext, user_message: str):
        """Extract business information from user message using simple keyword matching"""
        try:
            message_lower = user_message.lower()

            # Check if this looks like a structured response (numbered list)
            if self._user_provided_comprehensive_info(user_message):
                await self._extract_structured_information(context, user_message)
                return

            # Extract company name if mentioned
            if not context.company_info.name:
                # Look for common business name patterns
                if "i sell" in message_lower or "i run" in message_lower or "my business" in message_lower:
                    # Basic name extraction from common patterns
                    words = user_message.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["sell", "run", "business", "company"] and i > 0:
                            potential_name = words[i-1]
                            if len(potential_name) > 2:
                                context.company_info.name = potential_name.capitalize()
                                break

            # Extract industry/business type
            if not context.company_info.description:
                business_types = {
                    "bread": "Food & Bakery",
                    "food": "Food & Restaurant",
                    "restaurant": "Food & Restaurant",
                    "clothing": "Fashion & Retail",
                    "tech": "Technology",
                    "software": "Technology",
                    "consulting": "Professional Services",
                    "fitness": "Health & Fitness",
                    "beauty": "Beauty & Wellness",
                    "antique": "Antiques & Collectibles",
                    "chairs": "Furniture & Antiques",
                    "furniture": "Furniture & Home Decor"
                }

                for keyword, description in business_types.items():
                    if keyword in message_lower:
                        context.company_info.description = description
                        break

            # Extract target audience hints
            audience_keywords = {
                "young": "Young adults",
                "families": "Families",
                "professionals": "Working professionals",
                "students": "Students",
                "seniors": "Seniors",
                "women": "Women",
                "men": "Men",
                "collectors": "Collectors and enthusiasts"
            }

            if not context.company_info.target_audience:
                for keyword, audience in audience_keywords.items():
                    if keyword in message_lower:
                        context.company_info.target_audience = audience
                        break

        except Exception as e:
            logger.error(f"Information extraction error: {e}")

    async def _extract_structured_information(self, context: ConversationContext, user_message: str):
        """Extract information from structured/numbered responses"""
        try:
            # Use AI to parse the structured information
            prompt = f"""Parse this business information and extract key details:

User message: "{user_message}"

Extract the following if mentioned:
- Company/Business name
- Business type/industry
- Products/services
- Brand voice/tone
- Target audience
- Customer needs
- Goals
- Platform preferences
- Budget
- Brand colors
- Fonts
- Logo description
- Competitors

Return a simple summary of what you found, not JSON."""

            parsed_info = await self.llm_service.chat_with_system(
                "You are an information extraction specialist. Parse the business data and summarize key points clearly.",
                prompt
            )

            # Store the parsed information in context for later use
            context.extracted_insights["structured_response"] = user_message
            context.extracted_insights["parsed_info"] = parsed_info

            # Extract key details using keyword matching
            message_lower = user_message.lower()

            # Extract company name
            if "proteinrx" in message_lower:
                context.company_info.name = "ProteinRX"
            elif "ccc" in message_lower:
                context.company_info.name = "CCC"

            # Extract business type and products
            if "protein" in message_lower and "smoothie" in message_lower:
                context.company_info.description = "Health & Fitness - Protein Smoothie Drinks"
            elif "protein" in message_lower and "drink" in message_lower:
                context.company_info.description = "Health & Fitness - Protein Beverages"
            elif "antique" in message_lower and "chairs" in message_lower:
                context.company_info.description = "Antiques & Collectibles"

            # Extract target audience
            if "gym" in message_lower and ("20-45" in user_message or "age" in message_lower):
                context.company_info.target_audience = "Gym-goers and fitness enthusiasts (20-45 years old)"
            elif "collectors" in message_lower:
                context.company_info.target_audience = "Collectors and enthusiasts"

            # Extract brand voice
            if "luxury" in message_lower and "strong" in message_lower:
                context.company_info.brand_voice = "Luxury and strong"

            # Extract unique selling points
            unique_points = []
            if "accessible" in message_lower and "canned" in message_lower:
                unique_points.append("Convenient canned format for accessibility")
            if "everywhere" in message_lower:
                unique_points.append("Available everywhere")
            if unique_points:
                context.company_info.unique_selling_points = unique_points

            # Extract competitors
            if "traditional protein powder" in message_lower or "protein powder" in message_lower:
                context.company_info.competitors = ["Traditional protein powder brands"]

            # Extract goals
            if "brand awareness" in message_lower:
                from models.schemas import CampaignObjective
                context.campaign_goals.primary_objective = CampaignObjective.BRAND_AWARENESS
            elif "online presence" in message_lower:
                from models.schemas import CampaignObjective
                context.campaign_goals.primary_objective = CampaignObjective.BRAND_AWARENESS
            elif "sales" in message_lower:
                from models.schemas import CampaignObjective
                context.campaign_goals.primary_objective = CampaignObjective.SALES_CONVERSION

            # Extract platform
            if "instagram" in message_lower:
                from models.schemas import SocialPlatform
                context.campaign_goals.target_platforms = [SocialPlatform.INSTAGRAM]
            elif "facebook" in message_lower:
                from models.schemas import SocialPlatform
                context.campaign_goals.target_platforms = [SocialPlatform.FACEBOOK]

            # Extract brand assets
            brand_assets = {}
            if "red and black" in message_lower or ("red" in message_lower and "black" in message_lower):
                brand_assets["colors"] = "Red and black"
            if "lato" in message_lower:
                brand_assets["font"] = "Lato"
            if "dumbbell" in message_lower or "dumbell" in message_lower:
                brand_assets["logo"] = "Dumbbell symbol"

            if brand_assets:
                context.extracted_insights["brand_assets"] = brand_assets

            # Extract budget
            budget_match = re.search(r'\$?\s*(\d+)\s*(?:per\s*day|\/day|daily)', user_message.lower())
            if budget_match:
                context.campaign_goals.budget_range = f"${budget_match.group(1)}/day"

        except Exception as e:
            logger.error(f"Structured extraction error: {e}")
    
    async def _update_context_with_extracted_data(self, context: ConversationContext, data: Dict[str, Any]):
        """Update conversation context with extracted data"""
        try:
            # Update company info
            company_updates = {}
            for field in ['name', 'description', 'target_audience', 'brand_voice']:
                if field in data and data[field]:
                    company_updates[field] = data[field]
            
            # Handle industry enum
            if 'industry' in data and data['industry']:
                try:
                    company_updates['industry'] = Industry(data['industry'])
                except ValueError:
                    pass  # Invalid industry value
            
            # Handle array fields
            for field in ['brand_values', 'unique_selling_points', 'competitors']:
                if field in data and isinstance(data[field], list):
                    company_updates[field] = data[field]
            
            # Update company info
            if company_updates:
                for key, value in company_updates.items():
                    setattr(context.company_info, key, value)
            
            # Update campaign goals
            goal_updates = {}
            for field in ['budget_range', 'duration_weeks', 'specific_requirements']:
                if field in data and data[field]:
                    goal_updates[field] = data[field]
            
            # Handle objective enum
            if 'primary_objective' in data and data['primary_objective']:
                try:
                    goal_updates['primary_objective'] = CampaignObjective(data['primary_objective'])
                except ValueError:
                    pass
            
            # Handle platforms enum
            if 'target_platforms' in data and isinstance(data['target_platforms'], list):
                try:
                    platforms = [SocialPlatform(p) for p in data['target_platforms']]
                    goal_updates['target_platforms'] = platforms
                except ValueError:
                    pass
            
            # Update campaign goals
            if goal_updates:
                for key, value in goal_updates.items():
                    setattr(context.campaign_goals, key, value)
        
        except Exception as e:
            logger.error(f"Context update error: {e}")
    
    async def _add_message(self, context: ConversationContext, 
                         role: MessageRole, content: str):
        """Add a message to the conversation history"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        context.messages.append(message)
        
        # Keep conversation history manageable
        if len(context.messages) > 50:
            context.messages = context.messages[-40:]  # Keep last 40 messages
    
    def _has_basic_business_info(self, context: ConversationContext) -> bool:
        """Check if we have basic business information"""
        company = context.company_info
        return bool(company.name and (company.industry or company.description))

    def _user_provided_comprehensive_info(self, message: str) -> bool:
        """Check if user provided comprehensive business information in numbered/structured format"""
        # Look for numbered lists or comprehensive information
        has_numbers = bool(re.search(r'\d+\.\s', message))
        is_long = len(message) > 100
        has_multiple_details = message.count('.') > 3 or message.count(',') > 3

        return has_numbers or (is_long and has_multiple_details)
    
    def _calculate_progress(self, context: ConversationContext) -> float:
        """Calculate conversation progress as percentage"""
        stage_weights = {
            ConversationStage.GREETING: 0.1,
            ConversationStage.DISCOVERY: 0.3,
            ConversationStage.BRAND_ANALYSIS: 0.5,
            ConversationStage.STRATEGY_DEVELOPMENT: 0.7,
            ConversationStage.CONTENT_CREATION: 0.9,
            ConversationStage.REVIEW_REFINEMENT: 0.95,
            ConversationStage.FINALIZATION: 1.0
        }
        
        base_progress = stage_weights.get(context.current_stage, 0.0)
        
        # Adjust based on information completeness
        info_bonus = 0.0
        if context.company_info.name:
            info_bonus += 0.02
        if context.company_info.industry:
            info_bonus += 0.02
        if context.company_info.target_audience:
            info_bonus += 0.02
        if context.campaign_goals.primary_objective:
            info_bonus += 0.02
        if context.campaign_goals.target_platforms:
            info_bonus += 0.02
        
        return min(1.0, base_progress + info_bonus)
    
    async def _generate_campaign_summary(self, context: ConversationContext) -> str:
        """Generate final campaign summary"""
        if not context.campaign_output:
            return "Your campaign is still being prepared. Please wait a moment."
        
        posts_count = len(context.campaign_output.posts)
        platforms = list(set([post.platform.value for post in context.campaign_output.posts]))
        
        summary = f"🎉 **Your Social Media Campaign is Ready!**\n\n"
        summary += f"**Campaign Overview:**\n"
        summary += f"• Company: {context.company_info.name}\n"
        summary += f"• Industry: {context.company_info.industry.value if context.company_info.industry else 'General Business'}\n"
        summary += f"• Target Audience: {context.company_info.target_audience or 'Your defined audience'}\n\n"
        
        summary += f"**Content Package:**\n"
        summary += f"• {posts_count} social media posts created\n"
        summary += f"• Platforms: {', '.join([p.title() for p in platforms])}\n"
        summary += f"• Complete visual concepts for each post\n"
        summary += f"• Strategic hashtag recommendations\n"
        summary += f"• Optimized posting schedule\n\n"
        
        summary += f"**What's Included:**\n"
        summary += f"• Comprehensive brand strategy\n"
        summary += f"• Platform-specific content optimization\n"
        summary += f"• Visual design specifications\n"
        summary += f"• Performance tracking guidelines\n"
        summary += f"• Content calendar framework\n\n"
        
        summary += f"Your campaign is ready to launch! You can now implement these posts and start building your social media presence. "
        summary += f"Would you like me to explain any specific aspect of your campaign or help you with implementation planning?"
        
        return summary
    
    def close_session(self, session_id: str) -> bool:
        """Close a conversation session"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_contexts.keys())

# Removed fallback function for now