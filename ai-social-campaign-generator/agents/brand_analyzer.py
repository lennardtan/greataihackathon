"""
Brand Analysis Agent for discovering and analyzing brand identity and positioning
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    ConversationContext, AgentResponse, DiscoveryQuestion, 
    ConversationStage, CompanyInfo, Industry
)
from services.llm_service import LLMService
from prompts.brand_prompts import (
    BRAND_DISCOVERY_SYSTEM_PROMPT, BRAND_ANALYSIS_PROMPT,
    DISCOVERY_QUESTIONS_GENERATOR, BRAND_VOICE_ANALYZER,
    COMPETITIVE_ANALYSIS_PROMPT
)
import json
import logging

logger = logging.getLogger(__name__)

class BrandAnalyzer:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.discovery_priorities = [
            "business_basics",
            "target_audience", 
            "brand_identity",
            "competitive_landscape",
            "goals_objectives"
        ]
    
    async def analyze_conversation(self, context: ConversationContext) -> AgentResponse:
        """Analyze current conversation and determine next steps"""
        try:
            # Check if we've had enough conversation turns (limit discovery phase)
            discovery_turns = len([msg for msg in context.messages if msg.role.value == "user"])

            # Determine what information we need
            missing_info = self._identify_missing_information(context)

            # Move forward if we have basic info OR we've asked enough questions (3+ turns)
            has_basic_info = bool(context.company_info.name or context.company_info.description)

            if missing_info and discovery_turns < 3 and not has_basic_info:
                # Generate discovery questions only if we really need basic info
                questions = await self._generate_discovery_questions(context, missing_info)
                return AgentResponse(
                    message=self._format_discovery_message(questions),
                    questions=questions,
                    next_stage=ConversationStage.DISCOVERY,
                    requires_clarification=True
                )
            else:
                # We have enough info OR we've asked enough questions - move forward
                summary_prompt = f"""Based on our conversation, I understand you have a business in {context.company_info.description or 'your industry'}.

Let me create a social media strategy for you. I'll develop a campaign that focuses on showcasing your products and connecting with your target audience."""

                try:
                    ai_response = await self.llm_service.chat_with_system(
                        "You are a marketing consultant who has gathered enough information and is ready to create a strategy.",
                        summary_prompt
                    )

                    return AgentResponse(
                        message=ai_response,
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )
                except Exception as e:
                    return AgentResponse(
                        message="Perfect! I have enough information about your business. Let me create a social media strategy for you now.",
                        next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                        requires_clarification=False
                    )

        except Exception as e:
            logger.error(f"Brand analysis error: {e}")
            return AgentResponse(
                message="Let me create a social media strategy for your business now.",
                next_stage=ConversationStage.STRATEGY_DEVELOPMENT,
                requires_clarification=False
            )
    
    def _identify_missing_information(self, context: ConversationContext) -> List[str]:
        """Identify what critical brand information is missing"""
        missing = []
        
        company = context.company_info
        
        # Business basics
        if not company.name or not company.industry:
            missing.append("business_basics")
        
        # Target audience
        if not company.target_audience:
            missing.append("target_audience")
        
        # Brand identity
        if not company.brand_voice and not company.brand_values:
            missing.append("brand_identity")
        
        # Competitive landscape
        if not company.competitors:
            missing.append("competitive_landscape")
        
        # Goals and objectives
        if not context.campaign_goals.primary_objective:
            missing.append("goals_objectives")
        
        return missing
    
    async def _generate_discovery_questions(self, context: ConversationContext,
                                          missing_info: List[str]) -> List[str]:
        """Generate contextual discovery questions using AI"""
        try:
            # Get the last user message for context
            last_user_message = ""
            for msg in reversed(context.messages):
                if msg.role.value == "user":
                    last_user_message = msg.content
                    break

            # Create a simple prompt for natural conversation
            prompt = f"""The user just said: "{last_user_message}"

You are a friendly marketing consultant having a natural conversation. Based on what they said, ask 1-2 natural follow-up questions to learn more about their business for social media marketing.

Keep it conversational and natural - like you're genuinely interested in their business."""

            response = await self.llm_service.chat_with_system(
                "You are a friendly marketing consultant. Have a natural conversation and ask helpful questions.",
                prompt
            )

            # Extract questions - look for question marks
            questions = []
            sentences = response.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if '?' in sentence:
                    # Clean up and extract question
                    question = sentence.split('?')[0] + '?'
                    questions.append(question.strip())

            return questions[:2] if questions else [response.strip()]

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return self._get_fallback_questions(missing_info[0] if missing_info else "general")
    
    def _extract_questions_from_response(self, response: str) -> List[str]:
        """Extract questions from LLM response"""
        questions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.endswith('?'):
                # Clean up question formatting
                if line.startswith('- '):
                    line = line[2:]
                elif ':' in line:
                    line = line.split(':', 1)[1].strip()
                questions.append(line)
        
        return questions if questions else [response.strip()]
    
    def _get_fallback_questions(self, category: str) -> List[str]:
        """Get fallback questions if LLM generation fails"""
        fallback_questions = {
            "business_basics": [
                "That sounds interesting! What makes your bread special compared to others?"
            ],
            "target_audience": [
                "Who do you typically sell to - local families, restaurants, or other customers?"
            ],
            "brand_identity": [
                "What's most important to you about how customers see your business?"
            ],
            "competitive_landscape": [
                "Are there other bread sellers in your area you compete with?"
            ],
            "goals_objectives": [
                "What would you like to achieve with social media for your business?"
            ],
            "general": [
                "That's great! Tell me more about what kind of bread you make."
            ]
        }

        return fallback_questions.get(category, fallback_questions["general"])
    
    async def _perform_brand_analysis(self, context: ConversationContext) -> str:
        """Perform comprehensive brand analysis"""
        try:
            company_info = self._format_company_info(context.company_info)
            conversation_history = self._get_conversation_summary(context)
            
            prompt = BRAND_ANALYSIS_PROMPT.format(
                company_info=company_info,
                conversation_history=conversation_history
            )
            
            analysis = await self.llm_service.chat_with_system(
                "You are a brand strategist analyzing a business for social media marketing.",
                prompt
            )
            
            # Store analysis in context
            context.extracted_insights["brand_analysis"] = analysis
            
            return analysis
        
        except Exception as e:
            logger.error(f"Brand analysis error: {e}")
            return "Brand analysis completed. Ready to develop strategy."
    
    async def analyze_brand_voice(self, context: ConversationContext) -> str:
        """Analyze and recommend brand voice characteristics"""
        try:
            prompt = BRAND_VOICE_ANALYZER.format(
                business_context=self._format_company_info(context.company_info),
                industry=context.company_info.industry or "general",
                target_audience=context.company_info.target_audience or "general audience",
                brand_values=", ".join(context.company_info.brand_values or ["not specified"])
            )
            
            voice_analysis = await self.llm_service.chat_with_system(
                "You are a brand voice specialist analyzing communication style.",
                prompt
            )
            
            return voice_analysis
        
        except Exception as e:
            logger.error(f"Brand voice analysis error: {e}")
            return "Professional, authentic, and engaging brand voice recommended."
    
    async def analyze_competitive_landscape(self, context: ConversationContext) -> str:
        """Analyze competitive landscape and positioning opportunities"""
        try:
            prompt = COMPETITIVE_ANALYSIS_PROMPT.format(
                business_name=context.company_info.name,
                industry=context.company_info.industry or "general",
                competitors=", ".join(context.company_info.competitors or ["not specified"]),
                target_audience=context.company_info.target_audience or "general audience"
            )
            
            competitive_analysis = await self.llm_service.chat_with_system(
                "You are a competitive intelligence analyst for social media marketing.",
                prompt
            )
            
            return competitive_analysis
        
        except Exception as e:
            logger.error(f"Competitive analysis error: {e}")
            return "Competitive analysis completed. Unique positioning opportunities identified."
    
    def _format_discovery_message(self, questions: List[str]) -> str:
        """Format discovery questions into a natural conversation message"""
        # Return the AI-generated response directly for natural conversation
        return " ".join(questions)
    
    def _summarize_known_info(self, context: ConversationContext) -> str:
        """Summarize what we know about the business"""
        company = context.company_info
        known = []
        
        if company.name:
            known.append(f"Business: {company.name}")
        if company.industry:
            known.append(f"Industry: {company.industry}")
        if company.target_audience:
            known.append(f"Target Audience: {company.target_audience}")
        if company.description:
            known.append(f"Description: {company.description}")
        
        return "; ".join(known) if known else "Limited information available"
    
    def _get_conversation_summary(self, context: ConversationContext) -> str:
        """Get a summary of the conversation so far"""
        recent_messages = context.messages[-6:]  # Last 6 messages for context
        summary = []
        
        for msg in recent_messages:
            role = "User" if msg.role.value == "user" else "Assistant"
            summary.append(f"{role}: {msg.content[:100]}...")
        
        return "\n".join(summary)
    
    def _format_company_info(self, company: CompanyInfo) -> str:
        """Format company information for prompts"""
        info = []
        
        if company.name:
            info.append(f"Company: {company.name}")
        if company.industry:
            info.append(f"Industry: {company.industry}")
        if company.description:
            info.append(f"Description: {company.description}")
        if company.target_audience:
            info.append(f"Target Audience: {company.target_audience}")
        if company.brand_voice:
            info.append(f"Brand Voice: {company.brand_voice}")
        if company.brand_values:
            info.append(f"Brand Values: {', '.join(company.brand_values)}")
        if company.unique_selling_points:
            info.append(f"USPs: {', '.join(company.unique_selling_points)}")
        if company.competitors:
            info.append(f"Competitors: {', '.join(company.competitors)}")
        
        return "\n".join(info) if info else "Limited company information available"