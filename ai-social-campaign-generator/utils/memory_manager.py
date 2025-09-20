"""
Memory and Context Management for Conversational AI Sessions
"""

import json
import pickle
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging

from models.schemas import ConversationContext, ConversationMessage
from config.settings import settings

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages conversation memory, context persistence, and user preferences
    """
    
    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for active sessions
        self.memory_cache: Dict[str, ConversationContext] = {}
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
        # Memory limits
        self.max_messages_per_session = settings.memory_window_size * 2
        self.session_timeout_hours = 24
    
    async def save_context(self, context: ConversationContext) -> bool:
        """Save conversation context to persistent storage"""
        try:
            # Update cache
            self.memory_cache[context.session_id] = context
            
            # Save to file
            file_path = self.storage_path / f"{context.session_id}.json"
            
            # Convert to dict for JSON serialization
            context_dict = self._context_to_dict(context)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(context_dict, f, indent=2, default=str)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save context {context.session_id}: {e}")
            return False
    
    async def load_context(self, session_id: str) -> Optional[ConversationContext]:
        """Load conversation context from storage"""
        try:
            # Check cache first
            if session_id in self.memory_cache:
                return self.memory_cache[session_id]
            
            # Load from file
            file_path = self.storage_path / f"{session_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                context_dict = json.load(f)
            
            # Convert back to ConversationContext
            context = self._dict_to_context(context_dict)
            
            # Check if session is expired
            if self._is_session_expired(context):
                logger.info(f"Session {session_id} has expired")
                await self.delete_context(session_id)
                return None
            
            # Update cache
            self.memory_cache[session_id] = context
            
            return context
        
        except Exception as e:
            logger.error(f"Failed to load context {session_id}: {e}")
            return None
    
    async def delete_context(self, session_id: str) -> bool:
        """Delete conversation context"""
        try:
            # Remove from cache
            if session_id in self.memory_cache:
                del self.memory_cache[session_id]
            
            # Remove file
            file_path = self.storage_path / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete context {session_id}: {e}")
            return False
    
    async def compress_conversation_history(self, context: ConversationContext):
        """Compress conversation history to maintain memory limits"""
        if len(context.messages) <= self.max_messages_per_session:
            return
        
        try:
            # Keep the most recent messages
            recent_messages = context.messages[-self.max_messages_per_session:]
            
            # Create a summary of older messages
            older_messages = context.messages[:-self.max_messages_per_session]
            summary = await self._create_conversation_summary(older_messages)
            
            # Store summary in extracted insights
            context.extracted_insights["conversation_summary"] = summary
            
            # Replace message history with recent messages
            context.messages = recent_messages
            
            logger.info(f"Compressed conversation history for session {context.session_id}")
        
        except Exception as e:
            logger.error(f"Failed to compress conversation history: {e}")
    
    async def _create_conversation_summary(self, messages: List[ConversationMessage]) -> str:
        """Create a summary of conversation messages"""
        try:
            # Simple summarization - in production, could use LLM for better summaries
            user_messages = [msg.content for msg in messages if msg.role.value == "user"]
            assistant_messages = [msg.content for msg in messages if msg.role.value == "assistant"]
            
            summary = {
                "user_inputs": user_messages[-5:],  # Last 5 user inputs
                "key_assistant_responses": assistant_messages[-5:],  # Last 5 responses
                "total_exchanges": len(user_messages),
                "time_period": f"{messages[0].timestamp} to {messages[-1].timestamp}"
            }
            
            return json.dumps(summary)
        
        except Exception as e:
            logger.error(f"Failed to create conversation summary: {e}")
            return "Conversation summary unavailable"
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for personalization"""
        return self.user_preferences.get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id].update(preferences)
        
        # Save to file
        self._save_user_preferences()
    
    def _save_user_preferences(self):
        """Save user preferences to file"""
        try:
            prefs_file = self.storage_path / "user_preferences.json"
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
    
    def _load_user_preferences(self):
        """Load user preferences from file"""
        try:
            prefs_file = self.storage_path / "user_preferences.json"
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")
    
    def _context_to_dict(self, context: ConversationContext) -> Dict[str, Any]:
        """Convert ConversationContext to dictionary for JSON serialization"""
        return {
            "session_id": context.session_id,
            "current_stage": context.current_stage.value,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in context.messages
            ],
            "company_info": context.company_info.dict(),
            "campaign_goals": context.campaign_goals.dict(),
            "extracted_insights": context.extracted_insights,
            "pending_questions": context.pending_questions,
            "user_preferences": context.user_preferences,
            "campaign_output": context.campaign_output.dict() if context.campaign_output else None,
            "created_at": context.created_at.isoformat(),
            "last_updated": context.last_updated.isoformat()
        }
    
    def _dict_to_context(self, context_dict: Dict[str, Any]) -> ConversationContext:
        """Convert dictionary back to ConversationContext"""
        from models.schemas import (
            ConversationStage, MessageRole, CompanyInfo, 
            CampaignGoals, CampaignOutput
        )
        
        # Reconstruct messages
        messages = []
        for msg_dict in context_dict.get("messages", []):
            message = ConversationMessage(
                role=MessageRole(msg_dict["role"]),
                content=msg_dict["content"],
                timestamp=datetime.fromisoformat(msg_dict["timestamp"]),
                metadata=msg_dict.get("metadata")
            )
            messages.append(message)
        
        # Reconstruct company info
        company_info = CompanyInfo(**context_dict.get("company_info", {"name": ""}))
        
        # Reconstruct campaign goals
        campaign_goals = CampaignGoals(**context_dict.get("campaign_goals", {}))
        
        # Reconstruct campaign output if exists
        campaign_output = None
        if context_dict.get("campaign_output"):
            campaign_output = CampaignOutput(**context_dict["campaign_output"])
        
        return ConversationContext(
            session_id=context_dict["session_id"],
            current_stage=ConversationStage(context_dict["current_stage"]),
            messages=messages,
            company_info=company_info,
            campaign_goals=campaign_goals,
            extracted_insights=context_dict.get("extracted_insights", {}),
            pending_questions=context_dict.get("pending_questions", []),
            user_preferences=context_dict.get("user_preferences", {}),
            campaign_output=campaign_output,
            created_at=datetime.fromisoformat(context_dict["created_at"]),
            last_updated=datetime.fromisoformat(context_dict["last_updated"])
        )
    
    def _is_session_expired(self, context: ConversationContext) -> bool:
        """Check if a session has expired"""
        expiry_time = context.last_updated + timedelta(hours=self.session_timeout_hours)
        return datetime.utcnow() > expiry_time
    
    async def cleanup_expired_sessions(self):
        """Clean up expired conversation sessions"""
        try:
            expired_sessions = []
            
            # Check cache
            for session_id, context in self.memory_cache.items():
                if self._is_session_expired(context):
                    expired_sessions.append(session_id)
            
            # Check files
            for file_path in self.storage_path.glob("*.json"):
                if file_path.name == "user_preferences.json":
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        context_dict = json.load(f)
                    
                    last_updated = datetime.fromisoformat(context_dict["last_updated"])
                    if datetime.utcnow() > last_updated + timedelta(hours=self.session_timeout_hours):
                        session_id = context_dict["session_id"]
                        if session_id not in expired_sessions:
                            expired_sessions.append(session_id)
                
                except Exception as e:
                    logger.error(f"Error checking file {file_path}: {e}")
            
            # Delete expired sessions
            for session_id in expired_sessions:
                await self.delete_context(session_id)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about stored sessions"""
        try:
            total_sessions = len(list(self.storage_path.glob("*.json"))) - 1  # Exclude preferences file
            active_in_cache = len(self.memory_cache)
            
            # Calculate storage size
            total_size = sum(f.stat().st_size for f in self.storage_path.glob("*.json"))
            
            return {
                "total_sessions": total_sessions,
                "active_in_cache": active_in_cache,
                "storage_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_path)
            }
        
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {"error": str(e)}