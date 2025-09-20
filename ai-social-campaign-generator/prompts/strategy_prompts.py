"""
Strategy Development Prompts for Social Media Campaign Generation
"""

STRATEGY_DEVELOPMENT_SYSTEM_PROMPT = """
You are an expert social media strategist with deep knowledge of platform algorithms, audience behavior, and campaign optimization. Your role is to develop comprehensive, data-driven social media strategies that align with business objectives.

Key Responsibilities:
1. Translate business goals into actionable social media strategies
2. Recommend optimal platform mix and content approaches
3. Develop content pillars and messaging frameworks
4. Create performance metrics and success indicators
5. Provide strategic recommendations based on industry best practices

Strategy Focus Areas:
- Platform selection and optimization
- Content strategy and themes
- Audience targeting and engagement
- Performance measurement and KPIs
- Campaign timeline and execution

Maintain a strategic, analytical approach while being practical and actionable.
"""

CAMPAIGN_STRATEGY_PROMPT = """
Develop a comprehensive social media campaign strategy based on the brand analysis and business objectives.

Brand Analysis:
{brand_analysis}

Campaign Objectives:
{campaign_objectives}

Target Platforms:
{target_platforms}

Budget Considerations:
{budget_info}

Timeline:
{timeline}

Create a detailed strategy including:

1. **Strategic Overview**
   - Campaign objectives and success metrics
   - Target audience segmentation strategy
   - Key performance indicators (KPIs)
   - Overall campaign theme and narrative

2. **Platform Strategy**
   - Platform-specific objectives and approaches
   - Content format recommendations for each platform
   - Posting frequency and timing strategy
   - Platform-specific audience targeting

3. **Content Strategy Framework**
   - 4-6 core content pillars
   - Content mix and balance (educational, entertaining, promotional, etc.)
   - Storytelling themes and narrative arcs
   - Visual style and brand consistency guidelines

4. **Audience Engagement Strategy**
   - Community building approach
   - Engagement tactics and response strategies
   - User-generated content opportunities
   - Influencer collaboration possibilities

5. **Performance and Optimization**
   - Key metrics to track for each platform
   - A/B testing recommendations
   - Optimization strategies for underperforming content
   - Reporting and analysis framework

Provide a strategic foundation that will guide content creation and campaign execution.
"""

CONTENT_PILLAR_GENERATOR = """
Generate content pillars for a social media strategy based on brand identity and business objectives.

Brand Information:
{brand_info}

Business Objectives:
{objectives}

Target Audience:
{audience}

Industry Context:
{industry}

Create 4-6 content pillars that:

1. **Align with Brand Values**
   - Reflect the brand's core identity and mission
   - Support brand positioning and differentiation
   - Maintain consistency across all platforms

2. **Serve Audience Needs**
   - Address target audience pain points
   - Provide value through education, entertainment, or inspiration
   - Encourage engagement and community building

3. **Support Business Goals**
   - Drive awareness, engagement, or conversions as appropriate
   - Create opportunities for lead generation
   - Build brand authority and trust

For each content pillar, provide:
- **Pillar Name & Theme**
- **Core Message/Value Proposition**
- **Content Types** (educational, behind-the-scenes, user-generated, etc.)
- **Example Post Ideas** (3-4 specific examples)
- **Platform Optimization** (which platforms this pillar works best on)
- **Engagement Opportunities** (how this content encourages interaction)

Ensure pillars are diverse, engaging, and sustainable for long-term content creation.
"""

PLATFORM_OPTIMIZATION_PROMPT = """
Optimize the social media strategy for specific platforms based on their unique characteristics and audience behaviors.

Strategy Overview:
{strategy_overview}

Target Platforms:
{platforms}

For each platform, provide:

1. **Platform-Specific Strategy**
   - Optimal content formats and styles
   - Recommended posting frequency and timing
   - Platform-specific features to leverage (Stories, Reels, LinkedIn Articles, etc.)
   - Audience behavior patterns and engagement preferences

2. **Content Adaptation Guidelines**
   - How to adapt core content pillars for this platform
   - Platform-specific hashtag and keyword strategies
   - Visual content requirements and best practices
   - Caption length and style recommendations

3. **Engagement Optimization**
   - Platform algorithm considerations
   - Best practices for maximizing reach and engagement
   - Community building strategies specific to this platform
   - Influencer collaboration opportunities

4. **Performance Metrics**
   - Platform-specific KPIs to track
   - Benchmark goals for engagement, reach, and conversions
   - A/B testing opportunities unique to this platform

Provide actionable, platform-specific recommendations that maximize the effectiveness of each social media channel.
"""

COMPETITIVE_STRATEGY_PROMPT = """
Develop competitive social media strategies based on market analysis and competitor activity.

Competitive Landscape:
{competitive_analysis}

Brand Positioning:
{brand_positioning}

Market Opportunities:
{opportunities}

Provide strategic recommendations for:

1. **Differentiation Strategy**
   - How to position content uniquely in the market
   - Untapped content themes and angles
   - Unique value propositions to emphasize

2. **Competitive Advantages**
   - Strengths to leverage in social media content
   - Gaps in competitor strategies to exploit
   - Emerging trends to capitalize on

3. **Market Positioning**
   - Strategic messaging to differentiate from competitors
   - Content themes that establish thought leadership
   - Engagement strategies that build stronger community

4. **Risk Mitigation**
   - Potential competitive threats to monitor
   - Defensive strategies for maintaining market position
   - Proactive approaches to stay ahead of trends

Focus on actionable strategies that give this brand a competitive edge in social media marketing.
"""

KPI_FRAMEWORK_PROMPT = """
Develop a comprehensive KPI framework for measuring social media campaign success.

Campaign Objectives:
{objectives}

Business Goals:
{business_goals}

Target Platforms:
{platforms}

Timeline:
{timeline}

Create a measurement framework including:

1. **Primary KPIs** (directly tied to business objectives)
   - Awareness metrics (reach, impressions, brand mention tracking)
   - Engagement metrics (likes, comments, shares, saves)
   - Conversion metrics (click-through rates, lead generation, sales)
   - Community growth metrics (follower growth, audience quality)

2. **Secondary KPIs** (supporting metrics)
   - Content performance indicators
   - Audience behavior metrics
   - Platform-specific engagement rates
   - Share of voice in industry conversations

3. **Benchmark Goals**
   - Realistic targets for each metric based on industry standards
   - Progressive goals for different campaign phases
   - Platform-specific benchmarks

4. **Reporting Structure**
   - Daily/weekly/monthly reporting requirements
   - Key stakeholder dashboard requirements
   - Performance review and optimization schedule

Provide specific, measurable targets that align with business objectives and enable data-driven optimization.
"""