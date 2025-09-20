"""
Brand Analysis Prompts for Social Media Campaign Generation
"""

BRAND_DISCOVERY_SYSTEM_PROMPT = """
You are a skilled brand strategist and marketing consultant. Your role is to conduct a natural, conversational discovery process to understand a business's brand identity, target audience, and marketing goals.

Key Responsibilities:
1. Ask thoughtful, strategic questions to uncover brand essence
2. Listen actively and build on user responses
3. Identify gaps in brand understanding
4. Extract insights about target audience and positioning
5. Maintain a consultative, professional yet friendly tone

Conversation Guidelines:
- Ask 1-2 focused questions at a time (never overwhelm)
- Build on previous answers to go deeper
- Use business terminology appropriately
- Show genuine interest in their business
- Identify opportunities and challenges
- Be concise but thorough in your questioning

Current Focus: {focus_area}
"""

BRAND_ANALYSIS_PROMPT = """
Based on the conversation and information gathered, analyze this business's brand profile:

Company Information:
{company_info}

Conversation Context:
{conversation_history}

Provide a comprehensive brand analysis including:

1. **Brand Identity Summary**
   - Core brand essence and personality
   - Key differentiators and unique value proposition
   - Brand voice and tone characteristics

2. **Target Audience Profile**
   - Primary demographic details
   - Psychographic characteristics
   - Pain points and motivations
   - Social media behavior patterns

3. **Market Positioning**
   - Competitive landscape insights
   - Market opportunities
   - Brand positioning strategy recommendations

4. **Brand Strengths & Challenges**
   - Current brand strengths to leverage
   - Areas needing development
   - Potential market challenges

5. **Social Media Brand Guidelines**
   - Visual style recommendations
   - Content themes that align with brand
   - Voice and messaging guidelines
   - Platform-specific considerations

Format your response as a structured analysis that will inform social media strategy development.
"""

DISCOVERY_QUESTIONS_GENERATOR = """
Generate strategic discovery questions based on the current conversation context and missing information.

Context:
{context}

Known Information:
{known_info}

Information Gaps:
{gaps}

Generate 2-3 priority questions that would:
1. Fill critical information gaps
2. Deepen understanding of the business
3. Uncover strategic opportunities
4. Maintain natural conversation flow

Format as:
- Primary Question: [most important question]
- Follow-up Question: [builds on expected response]
- Insight Question: [uncovers strategic opportunity]

Focus on questions that lead to actionable social media strategy insights.
"""

BRAND_VOICE_ANALYZER = """
Analyze the brand voice and communication style based on the business information provided.

Business Context:
{business_context}

Industry: {industry}
Target Audience: {target_audience}
Brand Values: {brand_values}

Determine the optimal brand voice by analyzing:

1. **Industry Communication Norms**
   - How does this industry typically communicate?
   - What tone resonates with their audience?

2. **Audience Preferences**
   - What communication style appeals to their target market?
   - What level of formality is appropriate?

3. **Brand Personality Traits**
   - Professional vs. Casual
   - Authoritative vs. Approachable
   - Traditional vs. Innovative
   - Conservative vs. Bold

4. **Voice Characteristics**
   - Tone (friendly, professional, inspiring, etc.)
   - Language style (simple, technical, creative, etc.)
   - Personality traits (expert, mentor, friend, etc.)
   - Communication approach (educational, entertaining, inspiring, etc.)

Provide specific brand voice guidelines that will inform social media content creation.
"""

COMPETITIVE_ANALYSIS_PROMPT = """
Analyze the competitive landscape and positioning opportunities for this business.

Business: {business_name}
Industry: {industry}
Known Competitors: {competitors}
Target Audience: {target_audience}

Provide insights on:

1. **Competitive Differentiation**
   - How can this brand stand out from competitors?
   - What unique angles can be emphasized?
   - What gaps exist in the market?

2. **Social Media Opportunities**
   - What content themes are competitors missing?
   - What platforms might be underutilized?
   - What audience segments might be underserved?

3. **Positioning Strategy**
   - Recommended brand positioning
   - Key messages to emphasize
   - Content themes to focus on

4. **Competitive Advantages**
   - Unique strengths to highlight
   - Potential competitive weaknesses to address
   - Market opportunities to pursue

Focus on actionable insights that inform social media strategy and content creation.
"""