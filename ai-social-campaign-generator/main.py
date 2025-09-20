"""
CLI Interface for AI Social Media Campaign Generator
"""

import asyncio
import json
import argparse
from typing import Optional
from pathlib import Path
import sys

from services.llm_service import LLMService
from services.image_service import ImageService
from agents.orchestrator import CampaignOrchestrator
from utils.memory_manager import MemoryManager
from utils.helpers import create_campaign_report
from config.settings import settings
from demo_mode import DemoOrchestrator

class CLIInterface:
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        if demo_mode:
            print("🎯 Running in DEMO MODE - No API keys required!")
            self.orchestrator = DemoOrchestrator()
        else:
            self.llm_service = LLMService()
            self.image_service = ImageService()
            self.orchestrator = CampaignOrchestrator(self.llm_service, self.image_service)
        
        self.memory_manager = MemoryManager()
        self.current_session_id = None
    
    async def start_interactive_session(self):
        """Start an interactive conversation session"""
        print("🚀 AI Social Media Campaign Generator")
        print("=" * 50)
        print("Welcome! I'm your AI marketing consultant.")
        print("I'll help you create a comprehensive social media campaign through conversation.")
        print("Type 'quit' to exit, 'help' for commands, or 'new' to start over.\n")
        
        # Start new conversation
        response = await self.orchestrator.start_conversation()
        self.current_session_id = response["session_id"]
        
        print(f"🤖 Assistant: {response['message']}\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    await self._handle_quit()
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'new':
                    await self._start_new_conversation()
                    continue
                elif user_input.lower() == 'status':
                    await self._show_status()
                    continue
                elif user_input.lower() == 'export':
                    await self._export_campaign()
                    continue
                elif not user_input:
                    print("Please enter a message or type 'help' for commands.\n")
                    continue
                
                # Continue conversation
                response = await self.orchestrator.continue_conversation(
                    self.current_session_id, user_input
                )
                
                if response.get("status") == "error":
                    print(f"❌ Error: {response.get('message', 'Unknown error')}\n")
                    continue
                
                print(f"\n🤖 Assistant: {response['message']}")
                
                # Show questions if any
                if response.get("questions"):
                    print("\n💡 Suggested questions:")
                    for q in response["questions"]:
                        print(f"   • {q}")
                
                # Show suggestions if any
                if response.get("suggestions"):
                    print("\n✨ Suggestions:")
                    for s in response["suggestions"]:
                        print(f"   • {s}")
                
                print()  # Add spacing
                
                # Auto-save context (only in non-demo mode)
                if not self.demo_mode:
                    context = self.orchestrator.active_contexts.get(self.current_session_id)
                    if context:
                        await self.memory_manager.save_context(context)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again or type 'help' for assistance.\n")
    
    async def _handle_quit(self):
        """Handle quit command"""
        if self.current_session_id:
            context = self.orchestrator.active_contexts.get(self.current_session_id)
            if context:
                await self.memory_manager.save_context(context)
            
            # Offer to export campaign if ready
            campaign = await self.orchestrator.get_campaign_output(self.current_session_id)
            if not campaign.get("error"):
                export_choice = input("Would you like to export your campaign before leaving? (y/n): ")
                if export_choice.lower().startswith('y'):
                    await self._export_campaign()
        
        print("Thanks for using AI Social Campaign Generator! 👋")
    
    async def _start_new_conversation(self):
        """Start a new conversation"""
        if self.current_session_id:
            # Save current session
            context = self.orchestrator.active_contexts.get(self.current_session_id)
            if context:
                await self.memory_manager.save_context(context)
        
        print("\n🔄 Starting a new conversation...\n")
        response = await self.orchestrator.start_conversation()
        self.current_session_id = response["session_id"]
        print(f"🤖 Assistant: {response['message']}\n")
    
    async def _show_status(self):
        """Show current conversation status"""
        if not self.current_session_id:
            print("❌ No active conversation session.\n")
            return
        
        summary = await self.orchestrator.get_conversation_summary(self.current_session_id)
        if summary.get("error"):
            print(f"❌ Error getting status: {summary['error']}\n")
            return
        
        print(f"\n📊 Conversation Status:")
        print(f"   • Session ID: {summary['session_id'][:8]}...")
        print(f"   • Current Stage: {summary['stage'].replace('_', ' ').title()}")
        print(f"   • Progress: {summary['progress']:.1%}")
        print(f"   • Messages Exchanged: {summary['message_count']}")
        print(f"   • Insights Collected: {len(summary['insights_collected'])}")
        
        if summary['insights_collected']:
            print(f"   • Available Data: {', '.join(summary['insights_collected'])}")
        
        print()
    
    async def _export_campaign(self):
        """Export campaign to file"""
        if not self.current_session_id:
            print("❌ No active conversation session.\n")
            return
        
        campaign = await self.orchestrator.get_campaign_output(self.current_session_id)
        if campaign.get("error"):
            print(f"❌ Campaign not ready: {campaign['error']}\n")
            return
        
        # Create output directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = campaign["campaign"]["strategy"]["executive_summary"][:20] if campaign["campaign"]["strategy"]["executive_summary"] else "campaign"
        filename = f"campaign_{self.current_session_id[:8]}_{timestamp.replace(' ', '_')}.json"
        output_path = output_dir / filename
        
        # Create comprehensive report
        context = self.orchestrator.active_contexts.get(self.current_session_id)
        report_data = {
            "session_info": {
                "session_id": self.current_session_id,
                "generated_at": campaign["campaign"]["strategy"]["executive_summary"],
                "company": context.company_info.name if context else "Unknown"
            },
            "campaign": campaign["campaign"],
            "conversation_summary": await self.orchestrator.get_conversation_summary(self.current_session_id)
        }
        
        # Add performance report
        if context:
            report_data["performance_report"] = create_campaign_report({
                "company_name": context.company_info.name,
                "primary_objective": context.campaign_goals.primary_objective.value if context.campaign_goals.primary_objective else None,
                "platforms": [p.value for p in context.campaign_goals.target_platforms] if context.campaign_goals.target_platforms else [],
                "duration_weeks": context.campaign_goals.duration_weeks,
                "posts": [post.dict() for post in campaign["campaign"]["posts"]]
            })
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"✅ Campaign exported to: {output_path}")
        print(f"   • {len(campaign['campaign']['posts'])} posts included")
        print(f"   • Complete strategy and implementation guide")
        print()
    
    def _show_help(self):
        """Show help information"""
        print("\n📖 Available Commands:")
        print("   • help     - Show this help message")
        print("   • status   - Show current conversation status")
        print("   • export   - Export your campaign to a file")
        print("   • new      - Start a new conversation")
        print("   • quit     - Exit the application")
        print("\n💡 Tips:")
        print("   • Be specific about your business and goals")
        print("   • Answer questions thoroughly for better results")
        print("   • Ask for clarification if you need help")
        print("   • The AI learns about your brand through conversation")
        print()

def main():
    parser = argparse.ArgumentParser(description="AI Social Media Campaign Generator")
    parser.add_argument("--demo", action="store_true", help="Run demo mode with sample data")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--export-session", help="Export specific session ID")
    parser.add_argument("--list-sessions", action="store_true", help="List all saved sessions")
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            print("🎯 Starting demo mode...")
            cli = CLIInterface(demo_mode=True)
            asyncio.run(cli.start_interactive_session())
        elif args.list_sessions:
            print("📋 Saved Sessions:")
            # Could implement session listing
            print("   (Session listing not implemented)")
        elif args.export_session:
            print(f"📤 Exporting session {args.export_session}...")
            # Could implement specific session export
            print("   (Specific session export not implemented)")
        else:
            cli = CLIInterface(demo_mode=False)
            asyncio.run(cli.start_interactive_session())
    
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()