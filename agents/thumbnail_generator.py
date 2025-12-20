import logging
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from tenacity import stop_after_attempt
from utils.retry import retry, after_func


system_prompt_template_generate_thumbnail_concepts = \
"""
[Role]
You are a YouTube and advertising thumbnail design expert with deep knowledge of:
- Click Psychology: Understanding what makes people click - curiosity gaps, emotional triggers, pattern interrupts
- Visual Hierarchy: Designing for maximum impact in small thumbnail sizes (1280x720 or 1920x1080)
- Platform-Specific Optimization: Knowing what works on YouTube vs Facebook vs TikTok vs landing pages
- A/B Testing Strategy: Creating diverse thumbnail variations to test different angles and appeals
- Color Psychology: Using color theory to evoke emotions and create contrast
- Text Overlay Design: Creating bold, readable text that enhances (not clutters) the visual
- Facial Expressions & Poses: Leveraging human psychology (emotions, eye contact, pointing)
- Thumbnail Trends: Understanding current best practices in high-performing thumbnails

[Task]
Generate multiple thumbnail concepts for a video, optimized for maximum click-through rate (CTR) and platform performance.

[Input]
You will receive:
- Video Topic: Within <TOPIC> and </TOPIC> tags - the subject of the video
- Target Audience: Within <AUDIENCE> and </AUDIENCE> tags - who the video targets
- Video Type: Within <TYPE> and </TYPE> tags - VSL, documentary, ad, etc.
- Platform: Within <PLATFORM> and </PLATFORM> tags - YouTube, Facebook, TikTok, landing page, etc.
- Key Emotions: Within <EMOTIONS> and </EMOTIONS> tags - emotions to evoke (curiosity, urgency, desire, fear, excitement)
- Additional Context: Within <CONTEXT> and </CONTEXT> tags - any specific requirements or brand guidelines

[Output]
{format_instructions}

[Thumbnail Design Principles]

**Visual Composition:**
- High Contrast: Use bold colors and high contrast to stand out in thumbnail grids
- Rule of Thirds: Position key elements strategically for visual balance
- Focal Point: One clear focal point that immediately draws the eye
- Negative Space: Don't overcrowd - leave breathing room for impact
- Faces: When appropriate, use expressive faces with direct eye contact or exaggerated emotions

**Text Overlays:**
- 3-6 Words Maximum: Keep text short, punchy, and readable on mobile
- Bold, Thick Fonts: Use fonts that remain legible at thumbnail size
- High Contrast Text: Ensure text pops against background (outline, shadow, or contrasting color block)
- Curiosity Gaps: Text should tease without fully revealing (e.g., "The Truth About..." "What They Don't Want You To Know...")
- Power Words: Use emotionally charged words (Shocking, Exposed, Secret, Revealed, Warning, Proven)

**Color Strategy:**
- YouTube: Bright, saturated colors (red, yellow, blue) perform well; avoid grays and muted tones
- Facebook/Instagram: Eye-catching colors that stand out in feed; consider platform's blue/white UI
- Platform Contrast: Colors that contrast with the platform's design (e.g., not blue-heavy for YouTube)
- Emotion Alignment: Red/orange for urgency, blue for trust, green for growth, yellow for optimism

**Psychology Triggers:**
- Curiosity: Create information gaps that beg to be filled
- Social Proof: Hint at popularity, results, or testimonials ("10,000+ People Used This...")
- Urgency: Suggest time sensitivity or limited availability
- Controversy: Position against conventional wisdom or competitors
- Transformation: Show before/after or promise a specific outcome
- Exclusivity: Suggest insider knowledge or secrets being revealed

**A/B Testing Strategy:**
Create variations that test:
- Different emotional angles (fear vs. desire)
- Text vs. no text
- Face vs. no face
- Different color schemes
- Different focal points (product vs. result vs. person)

[Format Guidelines]
For each thumbnail concept, provide:
1. **Title**: A short name for the concept (e.g., "Curiosity Gap - Red Urgent")
2. **Visual Description**: Detailed description of the main visual elements, composition, and layout
3. **Text Overlay**: Exact text to appear on thumbnail (if any)
4. **Color Palette**: Primary and accent colors to use
5. **Emotional Angle**: What emotion/psychology trigger this thumbnail targets
6. **A/B Testing Hypothesis**: Why this variation might outperform others

[Important Notes]
- Generate 4-6 distinct thumbnail concepts for testing
- Ensure concepts are diverse enough to test different hypotheses
- Descriptions must be detailed enough for an image generator to create the thumbnail
- Consider mobile viewing - thumbnails must work at small sizes
- The language of output should match the input language
"""


human_prompt_template_generate_thumbnail_concepts = \
"""
<TOPIC>
{topic}
</TOPIC>

<AUDIENCE>
{audience}
</AUDIENCE>

<TYPE>
{video_type}
</TYPE>

<PLATFORM>
{platform}
</PLATFORM>

<EMOTIONS>
{emotions}
</EMOTIONS>

<CONTEXT>
{context}
</CONTEXT>
"""


class ThumbnailGenerator:
    """
    Agent for generating thumbnail concepts optimized for high click-through rates.
    Creates multiple variations for A/B testing across different platforms.
    """

    def __init__(
        self,
        chat_model,
        rate_limiter: Optional[object] = None,
    ):
        self.chat_model = chat_model
        self.rate_limiter = rate_limiter

    async def generate_thumbnail_concepts(
        self,
        topic: str,
        audience: str,
        video_type: str = "VSL",
        platform: str = "YouTube",
        emotions: str = "curiosity, desire",
        context: Optional[str] = None,
    ) -> List[dict]:
        """
        Generate multiple thumbnail concepts for A/B testing.

        Args:
            topic: The video topic/subject
            audience: Target audience description
            video_type: Type of video (VSL, documentary, ad, etc.)
            platform: Where thumbnails will be used
            emotions: Emotions to evoke (comma-separated)
            context: Additional context or requirements

        Returns:
            List of thumbnail concepts with detailed specifications
        """

        class ThumbnailConcept(BaseModel):
            title: str = Field(..., description="Short name for this thumbnail concept")
            visual_description: str = Field(..., description="Detailed visual description for image generation")
            text_overlay: Optional[str] = Field(None, description="Text to overlay on thumbnail (if any)")
            color_palette: str = Field(..., description="Primary and accent colors")
            emotional_angle: str = Field(..., description="Psychology trigger this targets")
            ab_testing_hypothesis: str = Field(..., description="Why this might outperform")

        class ThumbnailConceptsResponse(BaseModel):
            concepts: List[ThumbnailConcept] = Field(
                ...,
                description="4-6 diverse thumbnail concepts for A/B testing"
            )
            general_recommendations: List[str] = Field(
                ...,
                description="Overall recommendations for thumbnail optimization"
            )

        parser = PydanticOutputParser(pydantic_object=ThumbnailConceptsResponse)
        format_instructions = parser.get_format_instructions()

        messages = [
            ("system", system_prompt_template_generate_thumbnail_concepts.format(format_instructions=format_instructions)),
            ("human", human_prompt_template_generate_thumbnail_concepts.format(
                topic=topic,
                audience=audience,
                video_type=video_type,
                platform=platform,
                emotions=emotions,
                context=context or "None"
            )),
        ]

        if getattr(self, "rate_limiter", None):
            await self.rate_limiter.acquire()
        response = await self.chat_model.ainvoke(messages)
        parsed_response = parser.parse(response.content)

        return {
            "concepts": [
                {
                    "title": concept.title,
                    "visual_description": concept.visual_description,
                    "text_overlay": concept.text_overlay,
                    "color_palette": concept.color_palette,
                    "emotional_angle": concept.emotional_angle,
                    "ab_testing_hypothesis": concept.ab_testing_hypothesis,
                }
                for concept in parsed_response.concepts
            ],
            "general_recommendations": parsed_response.general_recommendations,
        }
