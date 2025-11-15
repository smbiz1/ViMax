from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class VSLSection(BaseModel):
    """
    Represents a section of a Video Sales Letter (VSL).
    """
    section_type: Literal["hook", "problem", "agitation", "solution", "proof", "cta", "bonus", "objection_handling"] = Field(
        description="The type of VSL section",
        examples=["hook", "problem", "solution", "cta"]
    )
    timestamp_start: str = Field(
        description="Start timestamp in MM:SS format",
        examples=["0:00", "1:30", "5:45"]
    )
    timestamp_end: str = Field(
        description="End timestamp in MM:SS format",
        examples=["0:30", "2:00", "6:15"]
    )
    script: str = Field(
        description="The voiceover script for this section"
    )
    visual_description: str = Field(
        description="Detailed description of what should be shown visually during this section"
    )
    key_message: str = Field(
        description="The core message or purpose of this section"
    )


class VSLScript(BaseModel):
    """
    Complete VSL script with all sections and metadata.
    """
    title: str = Field(
        description="The VSL title/headline"
    )
    duration_target: Literal["short", "medium", "long"] = Field(
        description="Target duration category: short (under 5 min), medium (5-10 min), long (10-40 min)"
    )
    platform: str = Field(
        description="Target platform (e.g., 'Facebook ads', 'Landing page', 'TikTok')",
        examples=["Facebook ads", "Landing page", "YouTube", "TikTok"]
    )
    product_name: str = Field(
        description="Name of the product or service being promoted"
    )
    target_audience: str = Field(
        description="Description of the target audience"
    )
    sections: List[VSLSection] = Field(
        description="List of VSL sections in sequence"
    )
    hooks: List[str] = Field(
        description="Alternative hook variations for A/B testing"
    )
    ctas: List[str] = Field(
        description="Alternative CTA variations for testing"
    )
    key_benefits: List[str] = Field(
        description="Main benefits highlighted in the VSL"
    )
    visual_suggestions: List[str] = Field(
        description="Overall visual direction and b-roll suggestions"
    )


class MarketingThumbnail(BaseModel):
    """
    Thumbnail design specification for marketing videos.
    """
    title: str = Field(
        description="Short name for this thumbnail concept",
        examples=["Curiosity Gap - Red Urgent", "Before/After Split", "Expert Authority"]
    )
    visual_description: str = Field(
        description="Detailed description for generating the thumbnail image"
    )
    text_overlay: Optional[str] = Field(
        default=None,
        description="Text to overlay on the thumbnail (3-6 words max)",
        examples=["The Secret They Hide", "Before You Buy...", "Shocking Results"]
    )
    color_palette: str = Field(
        description="Primary and accent colors",
        examples=["Red primary with white text", "Blue/yellow high contrast", "Orange gradient with black text"]
    )
    emotional_angle: str = Field(
        description="Psychology trigger this thumbnail targets",
        examples=["Curiosity", "Urgency", "Social proof", "Transformation"]
    )
    ab_testing_hypothesis: str = Field(
        description="Why this variation might outperform others"
    )
    platform_optimized_for: str = Field(
        description="Primary platform this thumbnail is optimized for",
        examples=["YouTube", "Facebook", "TikTok", "Landing page"]
    )


class MarketingHeadline(BaseModel):
    """
    Headline/title for marketing content.
    """
    headline: str = Field(
        description="The actual headline text"
    )
    character_count: int = Field(
        description="Number of characters in the headline"
    )
    psychology_angle: str = Field(
        description="Psychology trigger or emotion targeted",
        examples=["Curiosity", "Fear of missing out", "Problem-solution", "Social proof"]
    )
    testing_hypothesis: str = Field(
        description="Why this headline might outperform alternatives"
    )
    platform: str = Field(
        description="Platform this headline is optimized for",
        examples=["YouTube", "Facebook", "Google Ads", "Landing page"]
    )
    platform_notes: Optional[str] = Field(
        default=None,
        description="Platform-specific considerations or notes"
    )
    recommended_primary: bool = Field(
        default=False,
        description="Whether this is the recommended headline to test first"
    )


class DocumentarySegment(BaseModel):
    """
    Represents a segment/chapter of a documentary video.
    """
    chapter_number: int = Field(
        description="Sequential chapter number",
        examples=[1, 2, 3]
    )
    chapter_title: str = Field(
        description="Title of this chapter/segment",
        examples=["The Beginning", "The Discovery", "The Revelation"]
    )
    timestamp_start: str = Field(
        description="Start timestamp in MM:SS format"
    )
    timestamp_end: str = Field(
        description="End timestamp in MM:SS format"
    )
    narration: str = Field(
        description="Voiceover narration script for this segment"
    )
    visual_notes: List[str] = Field(
        description="Visual elements needed (b-roll, graphics, stock footage) for this segment"
    )
    key_points: List[str] = Field(
        description="Main facts or story beats covered in this segment"
    )
    retention_hook: Optional[str] = Field(
        default=None,
        description="Specific retention hook or cliffhanger at the end of this segment"
    )


class DocumentaryScript(BaseModel):
    """
    Complete documentary script with all segments and production notes.
    """
    title: str = Field(
        description="The documentary title"
    )
    duration_target: Literal["short", "long"] = Field(
        description="Target duration: short (under 10 min test), long (10-40 min full documentary)"
    )
    topic: str = Field(
        description="The documentary topic/subject"
    )
    target_audience: str = Field(
        description="Target audience description"
    )
    angle: str = Field(
        description="The unique angle or hook for the documentary",
        examples=["conspiracy theory", "historical deep dive", "shocking truth", "educational"]
    )
    segments: List[DocumentarySegment] = Field(
        description="List of documentary segments/chapters in sequence"
    )
    b_roll_categories: List[str] = Field(
        description="Categories of b-roll footage needed",
        examples=["Historical photos", "Modern city footage", "Interview clips", "Nature shots"]
    )
    music_sfx_suggestions: List[str] = Field(
        description="Music and sound effect suggestions for different sections"
    )
    retention_strategy: List[str] = Field(
        description="Key retention hooks and their timestamps"
    )
    is_faceless: bool = Field(
        default=True,
        description="Whether this is faceless content (voiceover + b-roll)"
    )
