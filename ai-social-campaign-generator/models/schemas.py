from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class Industry(str, Enum):
    RETAIL = "retail"
    FOOD_BEVERAGE = "food_beverage"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    AUTOMOTIVE = "automotive"
    BEAUTY_FASHION = "beauty_fashion"
    FITNESS_WELLNESS = "fitness_wellness"
    ENTERTAINMENT = "entertainment"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"

class CampaignObjective(str, Enum):
    BRAND_AWARENESS = "brand_awareness"
    ENGAGEMENT = "engagement"
    LEAD_GENERATION = "lead_generation"
    SALES_CONVERSION = "sales_conversion"
    WEBSITE_TRAFFIC = "website_traffic"
    APP_DOWNLOADS = "app_downloads"
    EVENT_PROMOTION = "event_promotion"
    CUSTOMER_RETENTION = "customer_retention"

class SocialPlatform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"

class ConversationStage(str, Enum):
    GREETING = "greeting"
    DISCOVERY = "discovery"
    BRAND_ANALYSIS = "brand_analysis"
    STRATEGY_DEVELOPMENT = "strategy_development"
    CONTENT_CREATION = "content_creation"
    REVIEW_REFINEMENT = "review_refinement"
    FINALIZATION = "finalization"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class CompanyInfo(BaseModel):
    name: str
    industry: Optional[Industry] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None
    brand_values: Optional[List[str]] = None
    unique_selling_points: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    website: Optional[str] = None
    current_social_presence: Optional[Dict[str, str]] = None

class CampaignGoals(BaseModel):
    primary_objective: Optional[CampaignObjective] = None
    secondary_objectives: Optional[List[CampaignObjective]] = None
    target_platforms: Optional[List[SocialPlatform]] = None
    budget_range: Optional[str] = None
    duration_weeks: Optional[int] = None
    specific_requirements: Optional[str] = None

class SocialPost(BaseModel):
    platform: SocialPlatform
    content: str
    hashtags: List[str] = []
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    call_to_action: Optional[str] = None
    post_type: str = "standard"  # standard, story, reel, etc.
    optimal_timing: Optional[str] = None
    engagement_hooks: List[str] = []

class CampaignStrategy(BaseModel):
    executive_summary: str
    target_audience_analysis: str
    content_pillars: List[str] = []
    brand_positioning: str
    competitive_differentiation: str
    key_messages: List[str] = []
    success_metrics: List[str] = []
    content_calendar_framework: Optional[str] = None

class CampaignOutput(BaseModel):
    strategy: CampaignStrategy
    posts: List[SocialPost] = []
    visual_guidelines: Optional[str] = None
    hashtag_strategy: Optional[str] = None
    influencer_recommendations: Optional[List[str]] = None
    performance_predictions: Optional[Dict[str, Any]] = None

class ConversationContext(BaseModel):
    session_id: str
    current_stage: ConversationStage = ConversationStage.GREETING
    messages: List[ConversationMessage] = []
    company_info: CompanyInfo = Field(default_factory=lambda: CompanyInfo(name=""))
    campaign_goals: CampaignGoals = Field(default_factory=CampaignGoals)
    extracted_insights: Dict[str, Any] = {}
    pending_questions: List[str] = []
    user_preferences: Dict[str, Any] = {}
    campaign_output: Optional[CampaignOutput] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class AgentResponse(BaseModel):
    message: str
    questions: List[str] = []
    suggestions: List[str] = []
    next_stage: Optional[ConversationStage] = None
    requires_clarification: bool = False
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class DiscoveryQuestion(BaseModel):
    question: str
    category: str  # business_info, target_audience, goals, etc.
    priority: int = Field(ge=1, le=5)  # 1 = highest priority
    follow_up_questions: List[str] = []
    context_needed: Optional[str] = None