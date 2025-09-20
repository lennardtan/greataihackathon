"""
Strategy Development Agent for creating comprehensive social media strategies
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    ConversationContext, AgentResponse, CampaignStrategy, 
    ConversationStage, CampaignObjective, SocialPlatform
)
from services.llm_service import LLMService
from prompts.strategy_prompts import (
    STRATEGY_DEVELOPMENT_SYSTEM_PROMPT, CAMPAIGN_STRATEGY_PROMPT,
    CONTENT_PILLAR_GENERATOR, PLATFORM_OPTIMIZATION_PROMPT,
    COMPETITIVE_STRATEGY_PROMPT, KPI_FRAMEWORK_PROMPT
)
import json
import logging

logger = logging.getLogger(__name__)

class StrategyAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.strategy_components = [
            "objectives_definition",
            "audience_targeting", 
            "platform_strategy",
            "content_pillars",
            "kpi_framework"
        ]
    
    async def develop_strategy(self, context: ConversationContext) -> AgentResponse:
        """Develop comprehensive social media strategy"""
        try:
            # Check if we have enough information for strategy development
            if not self._has_sufficient_info_for_strategy(context):
                return AgentResponse(
                    message="I need a bit more information to develop an effective strategy. What are your primary goals for social media marketing?",
                    questions=self._get_strategy_clarification_questions(context),
                    requires_clarification=True
                )
            
            # Develop the strategy
            strategy = await self._create_comprehensive_strategy(context)
            
            # Generate content pillars
            content_pillars = await self._generate_content_pillars(context)
            
            # Create platform-specific recommendations
            platform_strategy = await self._optimize_for_platforms(context, strategy)
            
            # Develop KPI framework
            kpi_framework = await self._create_kpi_framework(context)
            
            # Compile strategy response
            strategy_summary = self._format_strategy_summary(strategy, content_pillars)
            
            # Store in context
            context.extracted_insights.update({
                "campaign_strategy": strategy,
                "content_pillars": content_pillars,
                "platform_strategy": platform_strategy,
                "kpi_framework": kpi_framework
            })
            
            return AgentResponse(
                message=strategy_summary,
                next_stage=ConversationStage.CONTENT_CREATION,
                requires_clarification=False,
                metadata={
                    "strategy": strategy,
                    "content_pillars": content_pillars,
                    "platform_strategy": platform_strategy
                }
            )
        
        except Exception as e:
            logger.error(f"Strategy development error: {e}")
            return AgentResponse(
                message="I'm working on developing your strategy. Let me ask a few questions to ensure it's perfectly tailored to your needs.",
                questions=["What's your primary goal with social media - brand awareness, lead generation, or sales?"],
                requires_clarification=True
            )
    
    def _has_sufficient_info_for_strategy(self, context: ConversationContext) -> bool:
        """Check if we have enough information to develop strategy"""
        company = context.company_info
        goals = context.campaign_goals
        
        required_info = [
            company.name,
            company.industry or company.description,
            company.target_audience,
            goals.primary_objective or goals.target_platforms
        ]
        
        return all(info for info in required_info)
    
    def _get_strategy_clarification_questions(self, context: ConversationContext) -> List[str]:
        """Generate questions to clarify strategy requirements"""
        questions = []
        
        if not context.campaign_goals.primary_objective:
            questions.append("What's your main goal for social media - increasing brand awareness, generating leads, or driving sales?")
        
        if not context.campaign_goals.target_platforms:
            questions.append("Which social media platforms are most important for reaching your target audience?")
        
        if not context.campaign_goals.budget_range:
            questions.append("What's your approximate monthly budget for social media marketing?")
        
        return questions[:2]  # Limit to 2 questions
    
    async def _create_comprehensive_strategy(self, context: ConversationContext) -> str:
        """Create comprehensive campaign strategy"""
        try:
            brand_analysis = context.extracted_insights.get("brand_analysis", "")
            
            prompt = CAMPAIGN_STRATEGY_PROMPT.format(
                brand_analysis=brand_analysis,
                campaign_objectives=self._format_campaign_objectives(context),
                target_platforms=self._format_target_platforms(context),
                budget_info=context.campaign_goals.budget_range or "Budget flexible",
                timeline=f"{context.campaign_goals.duration_weeks or 12} weeks"
            )
            
            strategy = await self.llm_service.chat_with_system(
                STRATEGY_DEVELOPMENT_SYSTEM_PROMPT,
                prompt
            )
            
            return strategy
        
        except Exception as e:
            logger.error(f"Strategy creation error: {e}")
            return "Comprehensive social media strategy developed focusing on brand awareness and audience engagement."
    
    async def _generate_content_pillars(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Generate content pillars for the strategy"""
        try:
            prompt = CONTENT_PILLAR_GENERATOR.format(
                brand_info=self._format_brand_info(context),
                objectives=self._format_campaign_objectives(context),
                audience=context.company_info.target_audience or "target audience",
                industry=context.company_info.industry or "general business"
            )
            
            pillars_response = await self.llm_service.chat_with_system(
                "You are a content strategist developing content pillars for social media campaigns.",
                prompt
            )
            
            # Parse content pillars from response
            pillars = self._parse_content_pillars(pillars_response)
            return pillars
        
        except Exception as e:
            logger.error(f"Content pillar generation error: {e}")
            return self._get_default_content_pillars(context)
    
    async def _optimize_for_platforms(self, context: ConversationContext, strategy: str) -> str:
        """Create platform-specific optimization strategies"""
        try:
            platforms = context.campaign_goals.target_platforms or [SocialPlatform.FACEBOOK, SocialPlatform.INSTAGRAM]
            
            prompt = PLATFORM_OPTIMIZATION_PROMPT.format(
                strategy_overview=strategy[:1000],  # Truncate for context
                platforms=[p.value for p in platforms]
            )
            
            platform_strategy = await self.llm_service.chat_with_system(
                "You are a platform optimization specialist for social media marketing.",
                prompt
            )
            
            return platform_strategy
        
        except Exception as e:
            logger.error(f"Platform optimization error: {e}")
            return "Platform-specific strategies developed for optimal performance across selected channels."
    
    async def _create_kpi_framework(self, context: ConversationContext) -> str:
        """Create KPI measurement framework"""
        try:
            prompt = KPI_FRAMEWORK_PROMPT.format(
                objectives=self._format_campaign_objectives(context),
                business_goals=context.campaign_goals.specific_requirements or "General business growth",
                platforms=[p.value for p in (context.campaign_goals.target_platforms or [])],
                timeline=f"{context.campaign_goals.duration_weeks or 12} weeks"
            )
            
            kpi_framework = await self.llm_service.chat_with_system(
                "You are a social media analytics specialist developing KPI frameworks.",
                prompt
            )
            
            return kpi_framework
        
        except Exception as e:
            logger.error(f"KPI framework creation error: {e}")
            return "KPI framework established focusing on engagement, reach, and conversion metrics."
    
    def _parse_content_pillars(self, response: str) -> List[Dict[str, Any]]:
        """Parse content pillars from LLM response"""
        try:
            pillars = []
            current_pillar = {}
            
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for pillar headers
                if 'pillar' in line.lower() and (':' in line or line.endswith(':')):
                    if current_pillar:
                        pillars.append(current_pillar)
                    current_pillar = {
                        'name': line.replace(':', '').strip(),
                        'description': '',
                        'content_types': [],
                        'examples': []
                    }
                elif current_pillar:
                    # Add content to current pillar
                    if line.startswith('- '):
                        if 'example' in current_pillar.get('description', '').lower():
                            current_pillar['examples'].append(line[2:])
                        else:
                            current_pillar['content_types'].append(line[2:])
                    else:
                        current_pillar['description'] += ' ' + line
            
            if current_pillar:
                pillars.append(current_pillar)
            
            return pillars if pillars else self._get_default_content_pillars(context)
        
        except Exception as e:
            logger.error(f"Content pillar parsing error: {e}")
            return self._get_default_content_pillars(context)
    
    def _get_default_content_pillars(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Get default content pillars based on industry"""
        industry = context.company_info.industry
        
        default_pillars = [
            {
                "name": "Educational Content",
                "description": "Share valuable insights and tips related to your industry",
                "content_types": ["How-to guides", "Industry insights", "Tips and tricks"],
                "examples": ["Behind-the-scenes content", "Expert interviews", "Tutorial videos"]
            },
            {
                "name": "Brand Story",
                "description": "Showcase your company culture and values",
                "content_types": ["Company culture", "Team highlights", "Mission and values"],
                "examples": ["Employee spotlights", "Company milestones", "Value-driven content"]
            },
            {
                "name": "Customer Success",
                "description": "Highlight customer achievements and testimonials",
                "content_types": ["Success stories", "Testimonials", "Case studies"],
                "examples": ["Customer features", "Before/after showcases", "Review highlights"]
            },
            {
                "name": "Industry Leadership",
                "description": "Position your brand as a thought leader",
                "content_types": ["Industry trends", "Expert opinions", "Innovation updates"],
                "examples": ["Trend analysis", "Industry commentary", "Innovation showcases"]
            }
        ]
        
        return default_pillars
    
    def _format_strategy_summary(self, strategy: str, content_pillars: List[Dict]) -> str:
        """Format strategy into a conversational summary"""
        pillar_names = [pillar.get('name', 'Content Theme') for pillar in content_pillars[:4]]
        
        summary = f"Perfect! I've developed a comprehensive social media strategy for you.\n\n"
        summary += f"**Key Strategy Elements:**\n"
        summary += f"• **Content Pillars:** {', '.join(pillar_names)}\n"
        summary += f"• **Platform Focus:** Optimized for your target platforms\n"
        summary += f"• **Engagement Strategy:** Built around your brand voice and audience preferences\n"
        summary += f"• **Performance Tracking:** Clear KPIs and success metrics\n\n"
        summary += f"Would you like me to start creating specific social media posts based on this strategy, or would you like to refine any particular aspect first?"
        
        return summary
    
    def _format_campaign_objectives(self, context: ConversationContext) -> str:
        """Format campaign objectives for prompts"""
        goals = context.campaign_goals
        objectives = []
        
        if goals.primary_objective:
            objectives.append(f"Primary: {goals.primary_objective.value}")
        
        if goals.secondary_objectives:
            secondary = [obj.value for obj in goals.secondary_objectives]
            objectives.append(f"Secondary: {', '.join(secondary)}")
        
        if goals.specific_requirements:
            objectives.append(f"Requirements: {goals.specific_requirements}")
        
        return "; ".join(objectives) if objectives else "General brand awareness and engagement"
    
    def _format_target_platforms(self, context: ConversationContext) -> str:
        """Format target platforms for prompts"""
        platforms = context.campaign_goals.target_platforms
        if platforms:
            return ", ".join([p.value for p in platforms])
        return "Facebook, Instagram, LinkedIn"
    
    def _format_brand_info(self, context: ConversationContext) -> str:
        """Format brand information for prompts"""
        company = context.company_info
        info_parts = []
        
        if company.name:
            info_parts.append(f"Company: {company.name}")
        if company.industry:
            info_parts.append(f"Industry: {company.industry}")
        if company.description:
            info_parts.append(f"Description: {company.description}")
        if company.brand_values:
            info_parts.append(f"Values: {', '.join(company.brand_values)}")
        if company.unique_selling_points:
            info_parts.append(f"USPs: {', '.join(company.unique_selling_points)}")
        
        return "\n".join(info_parts)