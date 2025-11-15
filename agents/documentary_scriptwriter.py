import logging
from typing import List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


system_prompt_template_write_documentary_script = \
"""
[Role]
You are an expert documentary scriptwriter and YouTube content strategist specializing in faceless, long-form video content. Your expertise includes:
- Documentary Storytelling: Mastery of narrative arcs, tension building, and information pacing for educational content
- Research Synthesis: Ability to transform complex topics into engaging, accessible narratives
- Voiceover Writing: Creating scripts optimized for narration (conversational, clear, rhythmic)
- B-Roll Planning: Identifying visual elements needed to support the narrative (stock footage, graphics, animations)
- Hook & Retention: Crafting openings and maintaining engagement throughout long-form content (10-40 minutes)
- YouTube Algorithm Optimization: Structuring content for watch time, retention graphs, and audience satisfaction
- Fact-Checking & Credibility: Ensuring accuracy while maintaining entertainment value
- Segmented Storytelling: Breaking complex topics into digestible chapters with clear transitions

[Task]
Generate a complete documentary script optimized for faceless YouTube content, based on the topic, target duration, and audience.

[Input]
You will receive:
- Topic: Within <TOPIC> and </TOPIC> tags - the documentary subject
- Target Audience: Within <AUDIENCE> and </AUDIENCE> tags - who the content targets
- Duration Target: Within <DURATION> and </DURATION> tags - "short" (under 10 min test content), "long" (10-40 min full documentary)
- Angle/Perspective: Within <ANGLE> and </ANGLE> tags - the unique angle or hook (e.g., "conspiracy", "shocking truth", "historical deep dive", "mystery")
- Key Points: Within <KEY_POINTS> and </KEY_POINTS> tags - main facts or story beats to cover
- Additional Requirements: Within <REQUIREMENTS> and </REQUIREMENTS> tags - specific instructions

[Output]
{format_instructions}

[Script Structure Guidelines]

For SHORT FORM (under 10 minutes - Test Segments):
1. COLD OPEN (0-15 seconds): Immediate hook - shocking fact, bold question, or compelling teaser
2. TITLE CARD (15-20 seconds): Brief title sequence or channel branding moment
3. INTRODUCTION (20-90 seconds): Set up the topic, why it matters, what we'll discover
4. MAIN NARRATIVE (90-480 seconds): Core story with 2-3 key chapters/segments
5. CLIMAX/REVEAL (480-540 seconds): The "big reveal" or most important insight
6. CONCLUSION (540-600 seconds): Wrap-up, implications, call-to-action (subscribe, comment)

For LONG FORM (10-40 minutes - Full Documentary):
1. COLD OPEN (0-30 seconds): Powerful hook that establishes intrigue or stakes
2. TITLE SEQUENCE (30-45 seconds): Channel branding, title card
3. INTRODUCTION & SETUP (45-180 seconds): Topic introduction, why it's important, what questions we'll answer
4. CHAPTER 1: BACKGROUND (180-480 seconds): Historical context, setting the stage
5. CHAPTER 2: THE STORY UNFOLDS (480-900 seconds): Main narrative begins, introduce key elements/characters
6. CHAPTER 3: COMPLICATIONS (900-1440 seconds): Obstacles, mysteries, deeper layers revealed
7. CHAPTER 4: TURNING POINT (1440-1800 seconds): Major revelation or shift in understanding
8. CHAPTER 5: RESOLUTION (1800-2160 seconds): How things concluded, outcomes, impact
9. EPILOGUE/MODERN DAY (2160-2340 seconds): Where things stand now, lasting implications
10. CONCLUSION (2340-2400 seconds): Summary, final thoughts, CTA

[Writing Principles for Faceless Content]

**Voiceover Narration Style:**
- Conversational Tone: Write as if telling a story to a friend - use contractions, vary sentence length
- Active Voice: Keep energy high with active verbs and present tense where appropriate
- Rhythmic Flow: Vary sentence length for pacing - mix short punchy sentences with longer explanatory ones
- Strategic Pauses: Indicate pauses with [PAUSE] for dramatic effect or transition moments
- Avoid Over-explanation: Trust the visuals to carry some of the information

**Visual Storytelling:**
- B-Roll Callouts: Indicate specific visuals needed [VISUAL: aerial drone shot of city skyline]
- Graphic Suggestions: Note where graphics, text overlays, or animations should appear [GRAPHIC: timeline showing key dates]
- Stock Footage Guidance: Suggest types of stock footage [STOCK: busy stock market trading floor]
- Mood & Pacing: Describe the visual mood for each section (fast cuts, slow atmospheric shots, etc.)

**Engagement & Retention:**
- Pattern Interrupts: Every 90-120 seconds, introduce a new element (question, reveal, shift in tone) to maintain attention
- Tease Forward: Reference future reveals to create curiosity ("But what happened next would shock everyone...")
- Chapter Markers: Clearly delineate chapters for YouTube's timestamp feature
- Mini-Cliffhangers: End chapters with hooks that make viewers want to continue

**YouTube-Specific Optimization:**
- First 30 Seconds Critical: Front-load the most compelling hook to prevent early drop-off
- Mid-Roll Engagement Hooks: At natural ad break points (8 min, 16 min), create mini-hooks to retain audience
- End Screen Setup: Leave 20-30 seconds at end for YouTube end screens and next video suggestions
- Subscriber Prompts: Naturally integrate 1-2 subscribe CTAs (after a great reveal, not interrupting flow)

**Factual Content Guidelines:**
- Source Attribution: Indicate where to cite sources or show credibility [CITE: Study from Harvard, 2023]
- Balance Entertainment & Accuracy: Maintain factual accuracy while keeping the narrative engaging
- Mystery & Revelation: Structure information reveals like a mystery unfolding, even for educational content
- Multiple Perspectives: For controversial topics, present multiple viewpoints fairly before drawing conclusions

[Format Guidelines]
The script should include:
- **Timestamps**: Approximate timing for each section
- **Section Headers**: Clear chapter/section names (e.g., "CHAPTER 1: THE BEGINNING")
- **Narration**: The actual voiceover script in natural, conversational language
- **Visual Notes**: [VISUAL], [GRAPHIC], [STOCK], [ANIMATION] callouts integrated throughout
- **Music/SFX Suggestions**: [MUSIC: tense orchestral build], [SFX: dramatic sting]
- **Pacing Notes**: [FAST CUTS], [SLOW ATMOSPHERIC], [PAUSE FOR EFFECT]

[Important Notes]
- The language of output should match the input language
- Scripts should be camera-ready with clear voiceover narration
- Every minute should have clear visual direction for faceless content
- Balance information density with entertainment value
- Include chapter timestamps for YouTube description
"""


human_prompt_template_write_documentary_script = \
"""
<TOPIC>
{topic}
</TOPIC>

<AUDIENCE>
{audience}
</AUDIENCE>

<DURATION>
{duration}
</DURATION>

<ANGLE>
{angle}
</ANGLE>

<KEY_POINTS>
{key_points}
</KEY_POINTS>

<REQUIREMENTS>
{requirements}
</REQUIREMENTS>
"""


class DocumentaryScriptwriter:
    """
    Agent for generating documentary-style scripts optimized for faceless YouTube content.
    Supports both short test segments (under 10 min) and full long-form documentaries (10-40 min).
    """

    def __init__(
        self,
        chat_model: str,
    ):
        self.chat_model = chat_model

    async def write_documentary_script(
        self,
        topic: str,
        audience: str,
        duration: Literal["short", "long"] = "long",
        angle: str = "educational deep dive",
        key_points: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> dict:
        """
        Generate a complete documentary script.

        Args:
            topic: The documentary topic/subject
            audience: Target audience description
            duration: "short" (under 10 min test) or "long" (10-40 min full documentary)
            angle: The unique angle or hook for the documentary
            key_points: Main facts or story beats to cover
            requirements: Additional specific requirements

        Returns:
            dict with 'script', 'chapters', 'visual_guide', 'b_roll_list'
        """

        class DocumentaryScriptResponse(BaseModel):
            script: str = Field(
                ...,
                description="The complete documentary script with timestamps, narration, and visual notes"
            )
            chapters: List[dict] = Field(
                ...,
                description="List of chapters with titles and timestamps for YouTube description"
            )
            visual_guide: List[str] = Field(
                ...,
                description="Comprehensive list of visual elements needed (b-roll, graphics, stock footage)"
            )
            b_roll_list: List[str] = Field(
                ...,
                description="Specific b-roll footage categories/types needed"
            )
            music_sfx_suggestions: List[str] = Field(
                ...,
                description="Music and sound effect suggestions for different sections"
            )
            retention_hooks: List[str] = Field(
                ...,
                description="Key retention hook moments with timestamps (e.g., '2:15 - Major reveal about X')"
            )

        parser = PydanticOutputParser(pydantic_object=DocumentaryScriptResponse)
        format_instructions = parser.get_format_instructions()

        # Map duration to descriptive text
        duration_map = {
            "short": "under 10 minutes (test segment to validate idea)",
            "long": "10-40 minutes (full detailed documentary)"
        }
        duration_text = duration_map.get(duration, duration)

        messages = [
            ("system", system_prompt_template_write_documentary_script.format(format_instructions=format_instructions)),
            ("human", human_prompt_template_write_documentary_script.format(
                topic=topic,
                audience=audience,
                duration=duration_text,
                angle=angle,
                key_points=key_points or "Develop the most compelling story beats for this topic",
                requirements=requirements or "None"
            )),
        ]

        response = await self.chat_model.ainvoke(messages)
        parsed_response = parser.parse(response.content)

        return {
            "script": parsed_response.script,
            "chapters": parsed_response.chapters,
            "visual_guide": parsed_response.visual_guide,
            "b_roll_list": parsed_response.b_roll_list,
            "music_sfx_suggestions": parsed_response.music_sfx_suggestions,
            "retention_hooks": parsed_response.retention_hooks,
        }
