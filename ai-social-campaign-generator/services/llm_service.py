from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from config.settings import settings, LLMProvider
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        try:
            if settings.llm_provider == LLMProvider.OPENAI:
                return self._init_openai()
            elif settings.llm_provider == LLMProvider.ANTHROPIC:
                return self._init_anthropic()
            elif settings.llm_provider == LLMProvider.GEMINI:
                return self._init_gemini()
            else:
                raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI LLM"""
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model or "gpt-4",
            temperature=0.7,
            max_tokens=4000
        )
    
    def _init_anthropic(self):
        """Initialize Anthropic LLM"""
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model or "claude-3-sonnet-20240229",
            temperature=0.7,
            max_tokens=4000
        )

    def _init_gemini(self):
        """Initialize Gemini LLM"""
        return ChatGoogleGenerativeAI(
            google_api_key=settings.gemini_api_key,
            model=settings.llm_model or "gemini-2.5-flash",
            temperature=0.7,
            max_output_tokens=4000
        )
    
    async def chat(self, messages: List[BaseMessage]) -> str:
        """Send messages to LLM and return response"""
        try:
            logger.info(f"Sending {len(messages)} messages to {settings.llm_provider}")
            response = await self.llm.ainvoke(messages)
            logger.info(f"Received response: {response.content[:100]}...")
            return response.content
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise
    
    async def chat_with_system(self, system_prompt: str, user_message: str) -> str:
        """Chat with system prompt and user message"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        return await self.chat(messages)
    
    async def continue_conversation(self, 
                                 conversation_history: List[Dict[str, str]], 
                                 new_message: str,
                                 system_prompt: Optional[str] = None) -> str:
        """Continue a conversation with history"""
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=new_message))
        
        return await self.chat(messages)

def get_llm_service() -> LLMService:
    """Factory function to get LLM service instance"""
    return LLMService()

# Backward compatibility
def get_llm():
    """Legacy function for backward compatibility"""
    return get_llm_service().llm