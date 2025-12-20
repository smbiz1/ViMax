import logging
from typing import List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from tenacity import stop_after_attempt
from utils.retry import retry, after_func


system_prompt_template_generate_headlines = \
"""
[Role]
You are an expert copywriter specializing in high-converting headlines and titles for marketing content. Your expertise includes:
- Attention Economics: Understanding how to capture attention in crowded feeds and search results
- Curiosity Optimization: Creating information gaps that compel clicks without being clickbait
- SEO & Algorithm Optimization: Balancing human psychology with platform algorithms (YouTube SEO, Facebook ad performance)
- Power Word Usage: Leveraging emotionally charged language that drives action
- A/B Testing Strategy: Creating diverse headline variations to test different psychological angles
- Platform-Specific Best Practices: Adapting headlines for YouTube, Facebook ads, Google ads, landing pages, etc.
- Character Limit Mastery: Crafting punchy headlines within platform constraints

[Task]
Generate multiple high-converting headline variations optimized for the specified platform and purpose.

[Input]
You will receive:
- Topic/Offer: Within <TOPIC> and </TOPIC> tags - the subject or offer being promoted
- Target Audience: Within <AUDIENCE> and </AUDIENCE> tags - who the content targets
- Platform: Within <PLATFORM> and </PLATFORM> tags - where the headline will be used
- Goal: Within <GOAL> and </GOAL> tags - the desired outcome (clicks, views, conversions, brand awareness)
- Tone: Within <TONE> and </TONE> tags - the desired tone (urgent, educational, controversial, inspiring, etc.)
- Additional Context: Within <CONTEXT> and </CONTEXT> tags - any specific requirements

[Output]
{format_instructions}

[Headline Writing Principles]

**Universal Principles:**
- Clarity Over Cleverness: Make the value or promise immediately clear
- Specificity Sells: Use concrete numbers, timeframes, and outcomes (e.g., "30 Days" vs "Fast", "7 Steps" vs "Easy Method")
- One Big Promise: Focus on one clear benefit or outcome, not multiple
- Avoid Jargon: Use simple, conversational language unless targeting expert audiences
- Active Voice: Use strong verbs and active constructions

**Psychology Triggers:**
- Curiosity: Create information gaps ("The #1 Thing...", "What Nobody Tells You About...", "The Real Reason...")
- Urgency: Suggest time sensitivity ("Before It's Too Late", "In 2025", "Right Now")
- Social Proof: Imply popularity or validation ("Millions Use This...", "Experts Agree...", "Why Everyone Is...")
- Fear of Missing Out (FOMO): Suggest exclusive knowledge ("The Secret...", "What They Don't Want You To Know...")
- Problem-Solution: Lead with the problem ("Struggling With X? Try This...", "If You Can't X, Watch This...")
- Transformation: Promise a clear before/after ("How I Went From X to Y...")
- Controversy: Challenge conventional wisdom ("Everything You Know About X Is Wrong")

**Platform-Specific Optimization:**

**YouTube Titles:**
- Optimal Length: 60-70 characters (displays fully on most devices)
- Front-Load Keywords: Most important words in first 40 characters
- Use Brackets/Parentheses: Add context at end [NEW 2025], (PROVEN METHOD), [WARNING]
- Numbers Perform Well: Lists, timeframes, stats ("7 Ways...", "In 30 Days...", "10,000+ People...")
- Emotional Words: Shocking, Amazing, Revealed, Exposed, Truth, Secret, Warning, Ultimate, Complete

**Facebook/Instagram Ads:**
- Optimal Length: 5-10 words (mobile-first, quick scanning)
- Direct Response: Clear benefit or question that speaks to pain/desire
- Stop-Scrolling Power: Use pattern interrupts ("Wait! Before You...", "Attention [Audience]:")
- Test Questions: Questions can dramatically increase engagement
- Avoid "Ad Language": Sound conversational, not salesy

**Google Ads:**
- Headline 1 (30 chars): Primary benefit or offer
- Headline 2 (30 chars): Secondary benefit or unique mechanism
- Headline 3 (30 chars): Social proof or urgency
- Include Keywords: For quality score and relevance
- Call to Action: "Get", "Try", "Discover", "Learn"

**Landing Page Headlines:**
- Primary Headline: 10-20 words, clear value proposition
- Subheadline: 15-30 words, elaborate on mechanism or outcome
- Can Be Longer: More room for explanation than ads
- Benefit-Focused: Lead with what they'll get, not what you do

**Power Word Categories:**
- Urgency: Now, Today, Limited, Ending, Last Chance, Urgent, Fast, Quick, Instant
- Curiosity: Secret, Revealed, Exposed, Truth, Hidden, Shocking, Surprising, Unknown
- Value: Free, Bonus, Discount, Proven, Guaranteed, Certified, Official, Premium
- Authority: Expert, Professional, Advanced, Complete, Ultimate, Definitive, Comprehensive
- Transformation: How To, Step-by-Step, Easy, Simple, Quick, Effortless, Breakthrough

**A/B Testing Strategy:**
Create variations that test:
- Different emotional angles (fear vs. desire vs. curiosity)
- Short vs. longer formats
- Question vs. statement
- Benefit-focused vs. problem-focused
- Specific vs. broad promises
- With/without numbers or brackets

[Format Guidelines]
For each headline variation, provide:
1. **Headline**: The actual headline text (within character limits)
2. **Character Count**: Length of the headline
3. **Psychology Angle**: What trigger/emotion this targets
4. **Testing Hypothesis**: Why this might outperform alternatives
5. **Platform Notes**: Any platform-specific considerations

[Important Notes]
- Generate 6-10 diverse headline variations for testing
- Ensure headlines fit within platform character limits
- Avoid clickbait - headlines should deliver on their promise
- The language of output should match the input language
- Each variation should test a different hypothesis or angle
"""


human_prompt_template_generate_headlines = \
"""
<TOPIC>
{topic}
</TOPIC>

<AUDIENCE>
{audience}
</AUDIENCE>

<PLATFORM>
{platform}
</PLATFORM>

<GOAL>
{goal}
</GOAL>

<TONE>
{tone}
</TONE>

<CONTEXT>
{context}
</CONTEXT>
"""


class HeadlineGenerator:
    """
    Agent for generating high-converting headlines and titles for marketing content.
    Creates multiple variations optimized for different platforms and A/B testing.
    """

    def __init__(
        self,
        chat_model,
        rate_limiter: Optional[object] = None,
    ):
        self.chat_model = chat_model
        self.rate_limiter = rate_limiter

    async def generate_headlines(
        self,
        topic: str,
        audience: str,
        platform: Literal["youtube", "facebook", "google_ads", "landing_page", "tiktok"] = "youtube",
        goal: str = "maximize clicks and views",
        tone: str = "educational",
        context: Optional[str] = None,
    ) -> dict:
        """
        Generate multiple headline variations for A/B testing.

        Args:
            topic: The topic or offer being promoted
            audience: Target audience description
            platform: Platform where headline will be used
            goal: Desired outcome (clicks, conversions, awareness, etc.)
            tone: Desired tone (urgent, educational, controversial, etc.)
            context: Additional context or requirements

        Returns:
            dict with headline variations and recommendations
        """

        class HeadlineVariation(BaseModel):
            headline: str = Field(..., description="The headline text")
            character_count: int = Field(..., description="Character count")
            psychology_angle: str = Field(..., description="Psychology trigger/emotion targeted")
            testing_hypothesis: str = Field(..., description="Why this might outperform")
            platform_notes: Optional[str] = Field(None, description="Platform-specific considerations")

        class HeadlinesResponse(BaseModel):
            variations: List[HeadlineVariation] = Field(
                ...,
                description="6-10 diverse headline variations for testing"
            )
            recommended_primary: str = Field(
                ...,
                description="The recommended headline to test first"
            )
            character_limit_notes: str = Field(
                ...,
                description="Platform character limit guidance"
            )
            testing_recommendations: List[str] = Field(
                ...,
                description="Recommendations for A/B testing these headlines"
            )

        parser = PydanticOutputParser(pydantic_object=HeadlinesResponse)
        format_instructions = parser.get_format_instructions()

        # Platform-specific context
        platform_map = {
            "youtube": "YouTube video title (60-70 characters optimal)",
            "facebook": "Facebook/Instagram ad headline (5-10 words, mobile-first)",
            "google_ads": "Google Ads headline (30 characters per headline, 3 headlines total)",
            "landing_page": "Landing page headline (can be longer, 10-30 words)",
            "tiktok": "TikTok video title (short, punchy, trend-aware)"
        }
        platform_context = platform_map.get(platform, platform)

        messages = [
            ("system", system_prompt_template_generate_headlines.format(format_instructions=format_instructions)),
            ("human", human_prompt_template_generate_headlines.format(
                topic=topic,
                audience=audience,
                platform=platform_context,
                goal=goal,
                tone=tone,
                context=context or "None"
            )),
        ]

        if getattr(self, "rate_limiter", None):
            await self.rate_limiter.acquire()
        response = await self.chat_model.ainvoke(messages)
        parsed_response = parser.parse(response.content)

        return {
            "variations": [
                {
                    "headline": var.headline,
                    "character_count": var.character_count,
                    "psychology_angle": var.psychology_angle,
                    "testing_hypothesis": var.testing_hypothesis,
                    "platform_notes": var.platform_notes,
                }
                for var in parsed_response.variations
            ],
            "recommended_primary": parsed_response.recommended_primary,
            "character_limit_notes": parsed_response.character_limit_notes,
            "testing_recommendations": parsed_response.testing_recommendations,
        }
