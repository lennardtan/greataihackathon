# 🚀 AI Social Media Campaign Generator

A conversational AI marketing consultant that creates comprehensive social media campaigns through natural dialogue. Powered by LangChain and AWS Bedrock, this tool acts like a personal marketing team member that learns your business and creates increasingly targeted campaigns.

## ✨ Key Features

### 🤖 Conversational AI Marketing Consultant
- **Natural Conversation Flow**: Talk to the AI like you would with a human marketing consultant
- **Strategic Discovery**: Intelligently asks questions to understand your business, brand, and goals  
- **Learning & Adaptation**: Remembers your preferences and improves recommendations over time
- **Iterative Refinement**: Collaboratively develops and refines campaigns based on your feedback

### 📊 Comprehensive Campaign Development
- **Brand Analysis**: Deep dive into brand identity, voice, and positioning
- **Strategic Planning**: Multi-platform social media strategy development
- **Content Creation**: Platform-optimized posts with visuals and engagement hooks
- **Performance Framework**: KPI tracking and optimization recommendations

### 🎯 Platform-Specific Optimization
- **Multi-Platform Support**: Facebook, Instagram, LinkedIn, Twitter, TikTok, YouTube, Pinterest
- **Content Adaptation**: Automatically optimizes content format, length, and style for each platform
- **Visual Specifications**: Platform-specific image dimensions and visual guidelines
- **Hashtag Strategy**: Intelligent hashtag recommendations based on platform algorithms

### 🎨 Visual Content Generation
- **AI-Generated Visuals**: Integrated image generation using AWS Bedrock Titan or custom APIs
- **Brand-Consistent Design**: Visual concepts that align with your brand identity
- **Platform Optimization**: Images sized and styled for each social media platform
- **Style Guidelines**: Comprehensive visual brand guidelines for consistent content

## 🏗️ Architecture

### Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Orchestrator   │───▶│   AI Agents     │
│                 │    │                 │    │                 │
│ • CLI Interface │    │ • Conversation  │    │ • Brand Analyzer│
│ • Web Interface │    │   Management    │    │ • Strategy Agent│
│ • Chat System   │    │ • Context Flow  │    │ • Content Creator│
└─────────────────┘    │ • Memory Mgmt   │    │ • Visual Agent  │
                       └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │    Services     │
                       │                 │
                       │ • LLM Service   │
                       │ • Image Service │
                       │ • Memory Store  │
                       └─────────────────┘
```

### Conversation Flow
1. **Greeting**: Initial engagement and rapport building
2. **Discovery**: Strategic questioning about business and goals
3. **Brand Analysis**: Deep analysis of brand identity and positioning
4. **Strategy Development**: Multi-platform social media strategy creation
5. **Content Creation**: Platform-specific post generation with visuals
6. **Review & Refinement**: Collaborative improvement based on feedback
7. **Finalization**: Complete campaign package delivery

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account (for Bedrock) or OpenAI/Anthropic API keys
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/ai-social-campaign-generator.git
cd ai-social-campaign-generator
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Environment Configuration

Edit `.env` file with your API credentials:

```env
# LLM Configuration
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1
LLM_PROVIDER=aws_bedrock
LLM_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Alternative: OpenAI
# OPENAI_API_KEY=your_openai_key_here
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4

# Alternative: Anthropic
# ANTHROPIC_API_KEY=your_anthropic_key_here
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-sonnet-20240229

# Image Generation (Optional)
IMAGE_API_URL=your_image_api_endpoint
IMAGE_API_KEY=your_image_api_key
```

### Running the Application

#### CLI Interface (Recommended for first-time users)
```bash
python main.py
```

#### Web Interface
```bash
streamlit run app.py
```

#### Demo Mode
```bash
python main.py --demo
```

## 💬 Example Conversation

```
🤖 Assistant: Hi there! I'm your AI marketing consultant, and I'm excited to help you create an amazing social media campaign. What's your business about?

👤 You: I run a Malaysian restaurant called Nasi Lemak Express in downtown

🤖 Assistant: That sounds fantastic! Malaysian cuisine has such rich flavors and cultural stories to share. I'd love to learn more about your target audience and marketing goals. Who are you trying to reach with your social media?

👤 You: We want to attract young professionals aged 25-40 who work downtown, especially people who are curious about trying authentic Asian food

🤖 Assistant: Perfect! Food-curious young professionals are a great audience for authentic cultural experiences. Let me ask about your brand personality - how would you describe the voice and feeling you want your restaurant to convey? Are you more casual and approachable, or sophisticated and refined?

👤 You: We're warm and welcoming, really passionate about sharing Malaysian culture through food. We want people to feel like they're experiencing authentic Malaysian hospitality

🤖 Assistant: I love that! Authentic cultural hospitality is such a powerful brand position. Now, what are your main goals for social media marketing? Are you looking to increase brand awareness, drive foot traffic, or something else?

👤 You: Mainly brand awareness and getting more people to visit for lunch and dinner

🤖 Assistant: Excellent! I have a comprehensive understanding of your brand now. Let me develop a strategy that showcases authentic Malaysian culture, targets food-curious professionals, and drives foot traffic through compelling storytelling and food photography.

*[AI develops strategy and creates campaign...]*

🤖 Assistant: Perfect! I've created your complete social media campaign with 12 posts across Instagram and Facebook. Your strategy focuses on four content pillars:

• **Food Showcase**: Stunning photography of signature dishes with cultural context
• **Cultural Stories**: Educational content about Malaysian food traditions  
• **Behind the Scenes**: Morning prep and traditional cooking techniques
• **Community Connection**: Customer experiences and cultural celebrations

Would you like me to show you the specific posts I've created, or shall we finalize your campaign package?
```

## 📋 Features in Detail

### 🧠 AI Agents

#### Brand Analyzer
- Conducts strategic discovery conversations
- Analyzes brand identity and positioning
- Identifies target audience insights
- Recommends brand voice and messaging

#### Strategy Agent  
- Develops comprehensive social media strategies
- Creates platform-specific approaches
- Defines content pillars and themes
- Establishes KPI frameworks

#### Content Creator
- Generates platform-optimized posts
- Creates engaging copy with CTAs
- Develops hashtag strategies
- Designs visual concepts

#### Visual Agent
- Generates AI-powered images
- Creates brand-consistent visuals
- Optimizes for platform specifications
- Develops visual style guidelines

### 🗄️ Memory Management
- **Session Persistence**: Conversations saved across sessions
- **Context Awareness**: Remembers previous interactions and preferences
- **Smart Compression**: Efficiently manages long conversation histories
- **User Preferences**: Learns and adapts to your communication style

### 📊 Campaign Output
- **Complete Strategy Document**: Comprehensive social media strategy
- **Ready-to-Use Posts**: Platform-optimized content with visuals
- **Implementation Guide**: Step-by-step campaign execution plan
- **Performance Framework**: KPIs and success metrics
- **Content Calendar**: Structured posting schedule

## 🔧 Advanced Usage

### Custom Prompts
Modify prompts in the `prompts/` directory to customize AI behavior:
- `brand_prompts.py`: Brand discovery and analysis
- `strategy_prompts.py`: Strategy development
- `content_prompts.py`: Content creation

### LangChain Integration
Use the `chains/campaign_chain.py` for programmatic campaign generation:

```python
from chains.campaign_chain import SequentialCampaignChain
from services.llm_service import LLMService

llm_service = LLMService()
chain = SequentialCampaignChain(llm_service)

inputs = {
    "business_info": "Malaysian restaurant downtown",
    "campaign_objectives": "Brand awareness and foot traffic",
    "target_platforms": ["instagram", "facebook"]
}

campaign = await chain.run_full_campaign_generation(inputs)
```

### API Integration
Extend the image service for custom image generation APIs:

```python
from services.image_service import ImageService

class CustomImageService(ImageService):
    async def generate_image(self, prompt, style=None, platform=None):
        # Integrate with your preferred image generation API
        return image_url
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test categories:
```bash
# Test agents
pytest tests/test_agents.py -v

# Test with coverage
pytest tests/ --cov=agents --cov=services
```

## 📁 Project Structure

```
ai-social-campaign-generator/
│
├── .env                          # Environment configuration
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── main.py                      # CLI interface
├── app.py                       # Streamlit web interface
│
├── config/
│   └── settings.py              # Configuration management
│
├── agents/                      # AI agents
│   ├── orchestrator.py          # Main conversation orchestrator
│   ├── brand_analyzer.py        # Brand analysis agent
│   ├── strategy_agent.py        # Strategy development agent
│   ├── content_creator.py       # Content generation agent
│   └── visual_agent.py          # Visual content agent
│
├── chains/
│   └── campaign_chain.py        # LangChain workflow chains
│
├── prompts/                     # AI prompts
│   ├── brand_prompts.py         # Brand analysis prompts
│   ├── strategy_prompts.py      # Strategy prompts
│   └── content_prompts.py       # Content generation prompts
│
├── models/
│   └── schemas.py               # Pydantic data models
│
├── services/                    # Core services
│   ├── llm_service.py          # LLM integration
│   └── image_service.py        # Image generation
│
├── utils/                       # Utilities
│   ├── memory_manager.py       # Conversation memory
│   └── helpers.py              # Helper functions
│
├── data/                        # Sample data and templates
│   ├── sample_brands/           # Example brand profiles
│   └── templates/               # Content templates
│
└── tests/                       # Test suite
    ├── test_agents.py
    └── test_chains.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Check code quality
flake8 .
black .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Full documentation available at [docs/](docs/)
- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: Join the community discussion in [GitHub Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- **LangChain**: Framework for building LLM applications
- **AWS Bedrock**: Foundation model service
- **Streamlit**: Web application framework
- **OpenAI/Anthropic**: LLM providers

---

**Built with ❤️ for small and medium enterprises who need professional marketing support without the enterprise budget.**