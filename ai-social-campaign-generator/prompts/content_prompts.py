"""
Content Creation Prompts for Social Media Campaign Generation
"""

CONTENT_CREATOR_SYSTEM_PROMPT = """
You are a creative social media content specialist with expertise in crafting engaging, platform-optimized content that drives results. You understand platform algorithms, audience psychology, and conversion optimization.

Key Responsibilities:
1. Create compelling, platform-specific social media posts
2. Optimize content for engagement and reach
3. Maintain brand voice and visual consistency
4. Incorporate trending topics and hashtags strategically
5. Design content that encourages specific user actions

Content Creation Principles:
- Hook readers in the first few words
- Provide clear value (educate, entertain, inspire)
- Include strong calls-to-action
- Optimize for platform algorithms
- Maintain brand authenticity
- Encourage community engagement

Always consider: Platform context, audience behavior, optimal posting times, and brand objectives.
"""

SOCIAL_POST_GENERATOR = """
Create engaging social media posts based on the content strategy and brand guidelines.

Brand Guidelines:
{brand_guidelines}

Content Pillar:
{content_pillar}

Platform:
{platform}

Post Objective:
{objective}

Target Audience:
{audience}

Create a social media post that includes:

1. **Post Content**
   - Compelling hook that grabs attention immediately
   - Value-driven body content (educational, entertaining, or inspiring)
   - Clear call-to-action that encourages engagement
   - Platform-optimized length and formatting

2. **Hashtag Strategy**
   - Mix of branded, industry, and trending hashtags
   - Platform-appropriate hashtag count
   - Strategic hashtag placement

3. **Visual Description**
   - Detailed image/video concept description
   - Visual elements that support the message
   - Brand-consistent visual style
   - Platform-specific visual requirements

4. **Engagement Optimization**
   - Elements designed to encourage comments, shares, or saves
   - Questions or prompts for audience interaction
   - Conversation starters relevant to the content

5. **Timing and Context**
   - Optimal posting time recommendations
   - Seasonal or trending topic tie-ins
   - Current events or industry news connections

Format the post content exactly as it would appear on the platform, including line breaks and emojis where appropriate.
"""

VISUAL_CONTENT_PROMPT = """
Generate detailed visual content descriptions for social media posts.

Post Context:
{post_content}

Platform:
{platform}

Brand Style:
{brand_style}

Visual Objective:
{visual_objective}

Create detailed visual concepts including:

1. **Primary Visual Elements**
   - Main subject/focus of the image
   - Composition and layout suggestions
   - Color palette aligned with brand
   - Lighting and mood specifications

2. **Brand Integration**
   - Logo placement and sizing
   - Brand colors and fonts incorporation
   - Visual brand element usage
   - Consistency with brand aesthetic

3. **Platform Optimization**
   - Correct aspect ratio and dimensions
   - Text overlay considerations for different devices
   - Platform-specific visual best practices
   - Mobile-first design considerations

4. **Engagement Elements**
   - Visual hooks that stop scrolling
   - Elements that encourage interaction
   - Shareable visual components
   - Story-telling visual elements

5. **Alternative Versions**
   - Story/vertical format adaptation
   - Carousel post variations
   - Video/motion graphics possibilities
   - User-generated content integration

Provide specific, actionable visual direction that a designer or content creator can execute.
"""

CAMPAIGN_CONTENT_SERIES = """
Create a comprehensive content series for a social media campaign.

Campaign Strategy:
{campaign_strategy}

Content Pillars:
{content_pillars}

Platforms:
{platforms}

Timeline:
{timeline}

Generate a content series including:

1. **Content Calendar Framework**
   - Weekly content themes and topics
   - Platform-specific posting schedule
   - Content pillar rotation strategy
   - Seasonal and trending topic integration

2. **Post Variations for Each Pillar**
   - Educational content formats
   - Behind-the-scenes content
   - User-generated content campaigns
   - Promotional content integration

3. **Cross-Platform Adaptation**
   - How to adapt core content for each platform
   - Platform-specific content variations
   - Optimal timing for each platform
   - Cross-promotion strategies

4. **Engagement Campaigns**
   - Interactive content ideas (polls, Q&As, challenges)
   - User-generated content campaigns
   - Community building initiatives
   - Influencer collaboration content

5. **Content Amplification**
   - Repurposing strategies for maximum reach
   - Cross-platform content sharing
   - Employee advocacy content
   - Partner collaboration opportunities

Provide a structured content plan that maintains consistency while allowing for creative flexibility.
"""

HASHTAG_STRATEGY_PROMPT = """
Develop a comprehensive hashtag strategy for social media campaigns.

Brand Information:
{brand_info}

Target Audience:
{audience}

Platforms:
{platforms}

Content Themes:
{content_themes}

Create a hashtag strategy including:

1. **Branded Hashtags**
   - Primary brand hashtag for all content
   - Campaign-specific hashtags
   - Community hashtags for audience engagement
   - Event or product-specific hashtags

2. **Industry and Niche Hashtags**
   - High-volume industry hashtags for reach
   - Niche hashtags for targeted engagement
   - Professional and business-related tags
   - Location-based hashtags if relevant

3. **Trending and Seasonal Hashtags**
   - Current trending hashtags relevant to brand
   - Seasonal and holiday hashtags
   - Cultural moment and event hashtags
   - Industry conference and event tags

4. **Platform-Specific Strategy**
   - Instagram: Mix of broad and niche hashtags (up to 30)
   - LinkedIn: Professional and industry hashtags (3-5)
   - Twitter: Trending and conversation hashtags (1-3)
   - TikTok: Trending and challenge hashtags (3-5)

5. **Hashtag Performance Framework**
   - How to track hashtag performance
   - When to rotate or update hashtags
   - A/B testing hashtag combinations
   - Competitive hashtag analysis

Provide specific hashtag recommendations and usage guidelines for each platform and content type.
"""

CTA_OPTIMIZATION_PROMPT = """
Create compelling calls-to-action for social media content that drive specific user behaviors.

Post Content:
{post_content}

Business Objective:
{objective}

Platform:
{platform}

Target Action:
{target_action}

Generate optimized CTAs including:

1. **Primary CTA Options**
   - Direct action CTAs (click, buy, sign up, download)
   - Engagement CTAs (comment, share, tag someone)
   - Awareness CTAs (follow, subscribe, learn more)
   - Community CTAs (join, participate, contribute)

2. **Platform-Specific Optimization**
   - Instagram: Story swipe-ups, bio link direction
   - Facebook: Direct link clicks, event RSVPs
   - LinkedIn: Professional network actions, content engagement
   - Twitter: Retweets, thread participation, link clicks

3. **Psychological Triggers**
   - Urgency and scarcity elements
   - Social proof integration
   - Value proposition emphasis
   - Emotional appeal incorporation

4. **A/B Testing Variations**
   - Different CTA phrasings for testing
   - Placement variations (beginning, middle, end)
   - Direct vs. subtle approach options
   - Action-oriented vs. benefit-focused language

5. **Follow-up Strategy**
   - Post-click user experience optimization
   - Engagement response templates
   - Conversion tracking and attribution
   - Retargeting and nurture sequences

Provide specific CTA recommendations that align with platform best practices and drive measurable results.
"""