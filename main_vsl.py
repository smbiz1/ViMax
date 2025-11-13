"""
Main entry point for VSL (Video Sales Letter) generation.

This script demonstrates how to use the VSL2Video pipeline to create
marketing videos optimized for different platforms and durations:
- Short form (under 5 min): TikTok, Shorts, quick ads
- Medium form (5-10 min): Long form ads, mini VSLs
- Long form (10-40 min): Landing page VSLs

Usage:
    python main_vsl.py
"""

import asyncio
from pipelines.vsl2video_pipeline import VSL2VideoPipeline


# ========================================
# CONFIGURE YOUR VSL HERE
# ========================================

# Product or service being promoted
PRODUCT = """
AI-powered video creation tool that transforms ideas into complete videos in minutes.
No video editing experience required. Perfect for content creators, marketers, and businesses.
"""

# Target audience
AUDIENCE = """
Content creators, digital marketers, small business owners, and entrepreneurs aged 25-45
who want to create professional videos quickly without technical skills or expensive equipment.
"""

# Key benefits and selling points
BENEFITS = """
- Create professional videos in minutes, not hours or days
- No video editing experience or expensive equipment needed
- AI handles scripting, visuals, voiceovers, and editing
- Perfect for YouTube, social media, ads, and marketing
- 10x faster than traditional video production
- Affordable pricing starting at $29/month
- 14-day money-back guarantee
"""

# Duration: "short" (under 5 min), "medium" (5-10 min), or "long" (10-40 min)
DURATION = "medium"

# Platform: "Facebook ads", "Landing page", "TikTok", "YouTube", etc.
PLATFORM = "Facebook ads"

# Additional requirements (optional)
REQUIREMENTS = """
- Focus on the time-saving benefit as the primary hook
- Include social proof and testimonials in the proof section
- Create urgency with limited-time pricing
- Target tone: Professional but conversational
"""

# Config file based on duration
CONFIG_MAP = {
    "short": "configs/vsl_short_form.yaml",
    "medium": "configs/vsl_medium_form.yaml",
    "long": "configs/vsl_long_form.yaml",
}


async def main():
    """Run the VSL2Video pipeline."""
    # Initialize pipeline from config
    config_path = CONFIG_MAP.get(DURATION, "configs/vsl_medium_form.yaml")
    print(f"📋 Using config: {config_path}")

    pipeline = VSL2VideoPipeline.init_from_config(config_path=config_path)

    # Run the complete pipeline
    results = await pipeline(
        product=PRODUCT,
        audience=AUDIENCE,
        benefits=BENEFITS,
        duration=DURATION,
        platform=PLATFORM,
        requirements=REQUIREMENTS,
        generate_thumbnails=True,  # Generate thumbnail variations
        generate_headlines=True,    # Generate headline variations
    )

    print("\n" + "=" * 80)
    print("✅ VSL Generation Complete!")
    print("=" * 80)
    print(f"\n📂 Output directory: {pipeline.working_dir}")
    print("\nGenerated files:")
    print("  • vsl_script.json - Complete VSL script with sections")
    print("  • thumbnails.json - Thumbnail concepts for A/B testing")
    print("  • thumbnails/*.png - Generated thumbnail images")
    print("  • headlines.json - Headline variations for testing")
    print("\nNext steps:")
    print("  1. Review the VSL script and customize if needed")
    print("  2. Test different thumbnail and headline combinations")
    print("  3. Record voiceover or use text-to-speech")
    print("  4. Generate video with b-roll matching the visual suggestions")
    print("  5. A/B test different versions on your target platform")


if __name__ == "__main__":
    asyncio.run(main())
