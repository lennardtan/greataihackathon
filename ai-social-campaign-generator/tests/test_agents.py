"""
Test cases for AI Social Media Campaign Generator agents
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from models.schemas import (
    ConversationContext, CompanyInfo, CampaignGoals, 
    ConversationStage, Industry, CampaignObjective, SocialPlatform
)
from agents.brand_analyzer import BrandAnalyzer
from agents.strategy_agent import StrategyAgent
from agents.content_creator import ContentCreator
from agents.orchestrator import CampaignOrchestrator
from services.llm_service import LLMService
from services.image_service import ImageService

@pytest.fixture
def mock_llm_service():
    """Mock LLM service"""
    service = Mock(spec=LLMService)
    service.chat_with_system = AsyncMock(return_value="Test response")
    return service

@pytest.fixture
def mock_image_service():
    """Mock image service"""
    service = Mock(spec=ImageService)
    service.generate_image = AsyncMock(return_value="http://example.com/image.jpg")
    return service

@pytest.fixture
def sample_context():
    """Sample conversation context"""
    return ConversationContext(
        session_id="test-session-123",
        current_stage=ConversationStage.DISCOVERY,
        company_info=CompanyInfo(
            name="Test Restaurant",
            industry=Industry.FOOD_BEVERAGE,
            target_audience="Young professionals aged 25-40",
            description="Modern Malaysian cuisine restaurant"
        ),
        campaign_goals=CampaignGoals(
            primary_objective=CampaignObjective.BRAND_AWARENESS,
            target_platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK]
        )
    )

class TestBrandAnalyzer:
    """Test cases for BrandAnalyzer"""
    
    @pytest.mark.asyncio
    async def test_analyze_conversation_missing_info(self, mock_llm_service, sample_context):
        """Test brand analysis with missing information"""
        # Clear some required info
        sample_context.company_info.name = ""
        
        analyzer = BrandAnalyzer(mock_llm_service)
        response = await analyzer.analyze_conversation(sample_context)
        
        assert response.requires_clarification is True
        assert len(response.questions) > 0
        assert response.next_stage == ConversationStage.DISCOVERY
    
    @pytest.mark.asyncio
    async def test_analyze_conversation_sufficient_info(self, mock_llm_service, sample_context):
        """Test brand analysis with sufficient information"""
        analyzer = BrandAnalyzer(mock_llm_service)
        response = await analyzer.analyze_conversation(sample_context)
        
        assert response.next_stage == ConversationStage.STRATEGY_DEVELOPMENT
        assert response.requires_clarification is False
    
    @pytest.mark.asyncio
    async def test_brand_voice_analysis(self, mock_llm_service, sample_context):
        """Test brand voice analysis"""
        analyzer = BrandAnalyzer(mock_llm_service)
        voice_analysis = await analyzer.analyze_brand_voice(sample_context)
        
        assert isinstance(voice_analysis, str)
        assert len(voice_analysis) > 0
        mock_llm_service.chat_with_system.assert_called_once()

class TestStrategyAgent:
    """Test cases for StrategyAgent"""
    
    @pytest.mark.asyncio
    async def test_develop_strategy_insufficient_info(self, mock_llm_service, sample_context):
        """Test strategy development with insufficient information"""
        # Clear required info
        sample_context.company_info.target_audience = ""
        
        agent = StrategyAgent(mock_llm_service)
        response = await agent.develop_strategy(sample_context)
        
        assert response.requires_clarification is True
        assert len(response.questions) > 0
    
    @pytest.mark.asyncio
    async def test_develop_strategy_sufficient_info(self, mock_llm_service, sample_context):
        """Test strategy development with sufficient information"""
        agent = StrategyAgent(mock_llm_service)
        response = await agent.develop_strategy(sample_context)
        
        assert response.next_stage == ConversationStage.CONTENT_CREATION
        assert response.requires_clarification is False

class TestContentCreator:
    """Test cases for ContentCreator"""
    
    @pytest.mark.asyncio
    async def test_create_single_post(self, mock_llm_service, mock_image_service, sample_context):
        """Test single post creation"""
        creator = ContentCreator(mock_llm_service, mock_image_service)
        
        pillar = {
            "name": "Food Showcase",
            "description": "Showcase delicious dishes",
            "content_types": ["Food photos", "Behind the scenes"],
            "examples": ["Chef preparing dishes", "Signature meals"]
        }
        
        post = await creator.create_single_post(
            sample_context, 
            SocialPlatform.INSTAGRAM, 
            pillar
        )
        
        assert post.platform == SocialPlatform.INSTAGRAM
        assert len(post.content) > 0
        assert isinstance(post.hashtags, list)
    
    @pytest.mark.asyncio
    async def test_create_campaign_content_no_strategy(self, mock_llm_service, mock_image_service, sample_context):
        """Test campaign content creation without strategy foundation"""
        creator = ContentCreator(mock_llm_service, mock_image_service)
        response = await creator.create_campaign_content(sample_context)
        
        assert response.requires_clarification is True

class TestCampaignOrchestrator:
    """Test cases for CampaignOrchestrator"""
    
    @pytest.mark.asyncio
    async def test_start_conversation(self, mock_llm_service, mock_image_service):
        """Test starting a new conversation"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        response = await orchestrator.start_conversation()
        
        assert "session_id" in response
        assert "message" in response
        assert response["status"] == "active"
        assert len(response["session_id"]) > 0
    
    @pytest.mark.asyncio
    async def test_continue_conversation(self, mock_llm_service, mock_image_service):
        """Test continuing a conversation"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        
        # Start conversation first
        start_response = await orchestrator.start_conversation()
        session_id = start_response["session_id"]
        
        # Continue conversation
        response = await orchestrator.continue_conversation(
            session_id, "I run a Malaysian restaurant in downtown"
        )
        
        assert response["status"] == "active"
        assert "message" in response
        assert len(response["message"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_conversation_summary(self, mock_llm_service, mock_image_service):
        """Test getting conversation summary"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        
        # Start conversation
        start_response = await orchestrator.start_conversation()
        session_id = start_response["session_id"]
        
        # Get summary
        summary = await orchestrator.get_conversation_summary(session_id)
        
        assert "session_id" in summary
        assert "stage" in summary
        assert "progress" in summary
        assert summary["session_id"] == session_id
    
    def test_close_session(self, mock_llm_service, mock_image_service):
        """Test closing a session"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        
        # Add a mock session
        session_id = "test-session"
        orchestrator.active_contexts[session_id] = Mock()
        
        # Close session
        result = orchestrator.close_session(session_id)
        
        assert result is True
        assert session_id not in orchestrator.active_contexts
    
    def test_close_nonexistent_session(self, mock_llm_service, mock_image_service):
        """Test closing a non-existent session"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        
        result = orchestrator.close_session("nonexistent-session")
        
        assert result is False

class TestIntegration:
    """Integration test cases"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, mock_llm_service, mock_image_service):
        """Test complete conversation flow"""
        orchestrator = CampaignOrchestrator(mock_llm_service, mock_image_service)
        
        # Start conversation
        response = await orchestrator.start_conversation()
        session_id = response["session_id"]
        
        # Simulate user inputs
        user_inputs = [
            "I run a Malaysian restaurant called Nasi Lemak Express",
            "We target young professionals aged 25-40 in urban areas",
            "Our goal is to increase brand awareness and attract new customers",
            "We want to focus on Instagram and Facebook",
            "Yes, let's create the campaign"
        ]
        
        for user_input in user_inputs:
            response = await orchestrator.continue_conversation(session_id, user_input)
            assert response["status"] == "active"
        
        # Check if we have an active context
        assert session_id in orchestrator.active_contexts
        context = orchestrator.active_contexts[session_id]
        assert context.company_info.name == "Nasi Lemak Express"

if __name__ == "__main__":
    pytest.main([__file__])