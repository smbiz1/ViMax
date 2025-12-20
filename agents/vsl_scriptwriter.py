import logging
from typing import List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from tenacity import stop_after_attempt
from utils.retry import retry, after_func


system_prompt_template_write_vsl_script = """
[Role]
You are an expert Video Sales Letter (VSL) copywriter and marketing strategist with deep expertise in:
- Direct Response Marketing: Mastery of persuasion psychology, emotional triggers, and proven VSL frameworks (PAS, AIDA, Problem-Agitate-Solve)
- Attention-Grabbing Hooks: Creating powerful opening hooks that stop scrolling and capture attention in the first 3-5 seconds
- Pain Point Amplification: Identifying and articulating customer pain points in visceral, relatable ways that create urgency
- Benefit-Driven Copy: Translating features into compelling benefits that resonate emotionally and logically
- Call-to-Action Design: Crafting high-converting CTAs with clear next steps and minimal friction
- Storytelling for Sales: Using narrative techniques to build connection, trust, and desire
- Platform Optimization: Adapting copy for different platforms (Facebook/Instagram ads, landing pages, YouTube, TikTok/Shorts)

[Task]
Generate a complete, high-converting VSL script optimized for the specified duration and platform, based on the user's product/service, target audience, and key selling points.

[Input]
You will receive:
- Product/Service: Within <PRODUCT> and </PRODUCT> tags - the offer being promoted
- Target Audience: Within <AUDIENCE> and </AUDIENCE> tags - who the VSL is targeting
- Key Benefits: Within <BENEFITS> and </BENEFITS> tags - main selling points and value propositions
- Duration Target: Within <DURATION> and </DURATION> tags - target video length (e.g., "5-10 minutes", "under 5 minutes", "10-40 minutes")
- Platform/Purpose: Within <PLATFORM> and </PLATFORM> tags - where the VSL will be used (e.g., "Facebook ads", "Landing page", "TikTok", "YouTube")
- Additional Requirements: Within <REQUIREMENTS> and </REQUIREMENTS> tags - any specific instructions

[Output]
{format_instructions}

[Script Structure Guidelines]

For SHORT FORM (under 5 minutes - TikTok, Shorts, Quick Ads):
1. HOOK (0-5 seconds): Immediate attention-grabber - shocking statement, bold question, or scroll-stopping visual cue
2. PROBLEM INTRO (5-30 seconds): Quick pain point identification that resonates instantly
3. AGITATION (30-60 seconds): Amplify the pain, show consequences of inaction
4. SOLUTION REVEAL (60-90 seconds): Introduce your product/service as the answer
5. PROOF/CREDIBILITY (90-150 seconds): Quick social proof, results, testimonials
6. CTA (150-180 seconds): Clear, direct call to action with urgency

For MEDIUM FORM (5-10 minutes - Long Form Ads, Mini VSLs):
1. HOOK (0-10 seconds): Pattern interrupt that creates curiosity
2. PROBLEM DEEP DIVE (10-90 seconds): Establish the problem in detail, relate to audience
3. AGITATE & CONSEQUENCES (90-180 seconds): What happens if they don't solve this problem
4. INTRODUCE SOLUTION (180-240 seconds): Present your product/service
5. HOW IT WORKS (240-360 seconds): Explain the mechanism, process, or system
6. BENEFITS & TRANSFORMATION (360-480 seconds): Paint the after-state, emotional and practical benefits
7. PROOF & CREDIBILITY (480-540 seconds): Case studies, testimonials, credentials
8. CTA WITH BONUS (540-600 seconds): Strong call to action with scarcity/urgency/bonus

For LONG FORM (10-40 minutes - Landing Page VSLs):
1. COMPELLING HOOK (0-30 seconds): Story-based or question-based hook that creates intrigue
2. CREDIBILITY ESTABLISHMENT (30-120 seconds): Who you are, why you're qualified
3. PROBLEM IDENTIFICATION (120-360 seconds): Deep dive into the problem, relate multiple pain points
4. FALSE SOLUTIONS (360-540 seconds): Address what doesn't work and why (position against competitors)
5. THE BIG REVEAL (540-720 seconds): Introduce your unique solution/mechanism
6. DETAILED EXPLANATION (720-1200 seconds): How it works, the system, the process
7. PROOF STACK (1200-1680 seconds): Multiple testimonials, case studies, before/afters
8. BENEFITS & TRANSFORMATION (1680-2040 seconds): Detailed vision of life after using product
9. OBJECTION HANDLING (2040-2280 seconds): Address common concerns and hesitations
10. OFFER PRESENTATION (2280-2400 seconds): Price reveal, bonuses, guarantee
11. FINAL CTA (2400+ seconds): Urgent, clear call to action with recap of value

[Writing Principles]
- Conversational Tone: Write as if speaking directly to one person, use "you" and "your"
- Specificity Over Generality: Use concrete numbers, specific outcomes, vivid details
- Emotional Resonance: Tap into desires (freedom, security, status) and fears (loss, regret, FOMO)
- Visual Language: Use descriptions that are filmable - actions, expressions, scenarios
- Pacing: Match pacing to platform - faster for short form, breathing room for long form
- Authenticity: Avoid hype; focus on genuine value and transformation
- CTA Clarity: Make the next step crystal clear with minimal friction

[Important Notes]
- The language of output should match the input language
- Include timestamp markers for key transitions (e.g., [0:00-0:05], [0:05-0:30])
- Mark sections clearly (HOOK, PROBLEM, SOLUTION, etc.)
- Suggest visual cues in brackets where relevant (e.g., [Show person frustrated at computer])
- For faceless content, focus on voiceover narration with strong b-roll suggestions
"""


human_prompt_template_write_vsl_script = """
<PRODUCT>
{product}
</PRODUCT>

<AUDIENCE>
{audience}
</AUDIENCE>

<BENEFITS>
{benefits}
</BENEFITS>

<DURATION>
{duration}
</DURATION>

<PLATFORM>
{platform}
</PLATFORM>

<REQUIREMENTS>
{requirements}
</REQUIREMENTS>
"""


class VSLScriptwriter:
    """
    Agent for generating Video Sales Letter (VSL) scripts optimized for marketing and conversion.
    Supports different durations and platforms: short form ads, medium form VSLs, and long form landing page VSLs.
    """

    def __init__(
        self,
        chat_model,
    ):
        self.chat_model = chat_model

    @retry(stop=stop_after_attempt(3), after=after_func)
    async def write_vsl_script(
        self,
        product: str,
        audience: str,
        benefits: str,
        duration: Literal["short", "medium", "long"] = "medium",
        platform: str = "Landing page",
        requirements: Optional[str] = None,
    ) -> dict:
        """
        Generate a complete VSL script.

        Args:
            product: The product or service being promoted
            audience: Target audience description
            benefits: Key benefits and selling points
            duration: "short" (under 5 min), "medium" (5-10 min), or "long" (10-40 min)
            platform: Where the VSL will be used (e.g., "Facebook ads", "TikTok", "Landing page")
            requirements: Additional specific requirements

        Returns:
            dict with 'script', 'hooks', 'visual_suggestions', 'key_moments'
        """

        class VSLScriptResponse(BaseModel):
            script: str = Field(
                ...,
                description="The complete VSL script with timestamps and section markers",
            )
            hooks: List[str] = Field(
                ..., description="3-5 alternative hook variations for A/B testing"
            )
            visual_suggestions: List[str] = Field(
                ..., description="Key visual b-roll suggestions throughout the script"
            )
            key_moments: List[str] = Field(
                ...,
                description="Critical timestamps and moments (e.g., 'Problem reveal at 0:15', 'CTA at 8:30')",
            )

        parser = PydanticOutputParser(pydantic_object=VSLScriptResponse)
        format_instructions = parser.get_format_instructions()

        # Map duration to descriptive text
        duration_map = {
            "short": "under 5 minutes (optimized for TikTok, Shorts, quick ads)",
            "medium": "5-10 minutes (optimized for long form ads, mini VSLs)",
            "long": "10-40 minutes (optimized for landing page VSLs)",
        }
        duration_text = duration_map.get(duration, duration)

        messages = [
            (
                "system",
                system_prompt_template_write_vsl_script.format(
                    format_instructions=format_instructions
                ),
            ),
            (
                "human",
                human_prompt_template_write_vsl_script.format(
                    product=product,
                    audience=audience,
                    benefits=benefits,
                    duration=duration_text,
                    platform=platform,
                    requirements=requirements or "None",
                ),
            ),
        ]

        response = await self.chat_model.ainvoke(messages)
        parsed_response = parser.parse(response.content)

        return {
            "script": parsed_response.script,
            "hooks": parsed_response.hooks,
            "visual_suggestions": parsed_response.visual_suggestions,
            "key_moments": parsed_response.key_moments,
        }
