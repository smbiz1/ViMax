"""
Main entry point for Documentary video generation.

This script demonstrates how to use the Documentary2Video pipeline to create
faceless YouTube documentary content:
- Short form (under 10 min): Test segments to validate ideas
- Long form (10-40 min): Full detailed documentary on proven topics

Usage:
    python main_documentary.py
"""

import asyncio
from pipelines.documentary2video_pipeline import Documentary2VideoPipeline


# ========================================
# CONFIGURE YOUR DOCUMENTARY HERE
# ========================================

# Documentary topic
TOPIC = """
The Rise and Fall of Nokia: How the Mobile Phone Giant Lost Its Dominance
"""

# Target audience
AUDIENCE = """
Tech enthusiasts, business students, and general YouTube viewers aged 18-45
interested in business history, technology, and corporate strategy lessons.
"""

# Duration: "short" (under 10 min test) or "long" (10-40 min full documentary)
DURATION = "long"

# Angle/perspective for the documentary
ANGLE = """
Educational deep dive with a focus on strategic mistakes and lessons for modern companies.
Present it as a cautionary tale about complacency and failure to adapt to market changes.
Use a narrative style that builds suspense around each critical decision point.
"""

# Key points to cover (optional - AI will expand on these)
KEY_POINTS = """
- Nokia's dominance in the early 2000s mobile phone market (40% market share)
- The company's innovative features and design leadership
- The introduction of the iPhone and touchscreen revolution
- Nokia's decision to stick with Symbian OS instead of adopting Android
- The failed Microsoft partnership and Windows Phone strategy
- Cultural issues: bureaucracy, internal politics, and resistance to change
- The final collapse and sale to Microsoft in 2013
- Legacy and lessons for modern tech companies
- Where Nokia is today (network infrastructure business)
"""

# Additional requirements (optional)
REQUIREMENTS = """
- Include actual historical footage and photos where possible
- Use dramatic music to build tension during key decision moments
- Include expert quotes or perspectives (can be paraphrased)
- Make it feel like a Netflix-quality documentary
- Target runtime: 25-30 minutes
- Structure with clear chapters for YouTube timestamps
"""

# Config file based on duration
CONFIG_MAP = {
    "short": "configs/documentary_short.yaml",
    "long": "configs/documentary_long.yaml",
}


async def main():
    """Run the Documentary2Video pipeline."""
    # Initialize pipeline from config
    config_path = CONFIG_MAP.get(DURATION, "configs/documentary_long.yaml")
    print(f"📋 Using config: {config_path}")

    pipeline = Documentary2VideoPipeline.init_from_config(config_path=config_path)

    # Run the complete pipeline
    results = await pipeline(
        topic=TOPIC,
        audience=AUDIENCE,
        duration=DURATION,
        angle=ANGLE,
        key_points=KEY_POINTS,
        requirements=REQUIREMENTS,
        generate_thumbnails=True,  # Generate thumbnail variations
        generate_headlines=True,    # Generate YouTube title variations
    )

    print("\n" + "=" * 80)
    print("✅ Documentary Generation Complete!")
    print("=" * 80)
    print(f"\n📂 Output directory: {pipeline.working_dir}")
    print("\nGenerated files:")
    print("  • documentary_script.json - Complete script with chapters and timing")
    print("  • documentary_script.txt - Human-readable script for voiceover")
    print("  • thumbnails.json - Thumbnail concepts for A/B testing")
    print("  • thumbnails/*.png - Generated thumbnail images")
    print("  • youtube_titles.json - Title variations for testing")
    print("  • youtube_description.txt - YouTube description with chapters")
    print("\nNext steps:")
    print("  1. Review the documentary script and narration")
    print("  2. Record voiceover or use text-to-speech")
    print("  3. Gather b-roll footage based on the visual guide")
    print("  4. Edit video with chapters matching the timestamps")
    print("  5. Test different thumbnail and title combinations")
    print("  6. Upload to YouTube with the generated description and chapters")


if __name__ == "__main__":
    asyncio.run(main())
