import os
import json
import logging
import asyncio
import yaml
import importlib
from typing import Optional, List, Literal
from moviepy import VideoFileClip, concatenate_videoclips
from PIL import Image

from agents import VSLScriptwriter, ThumbnailGenerator, HeadlineGenerator, StoryboardArtist, CameraImageGenerator
from interfaces import VSLScript, VSLSection, MarketingThumbnail, MarketingHeadline
from langchain.chat_models import init_chat_model
from utils.timer import Timer


class VSL2VideoPipeline:
    """
    Pipeline for generating Video Sales Letter (VSL) content.
    Supports short form (under 5 min), medium form (5-10 min), and long form (10-40 min) VSLs.

    This pipeline:
    1. Generates VSL script optimized for conversion
    2. Creates multiple thumbnail variations for A/B testing
    3. Generates headline variations for testing
    4. Produces storyboard for visual elements
    5. Generates video content with voiceover
    """

    def __init__(
        self,
        chat_model,
        image_generator,
        video_generator,
        working_dir: str,
    ):
        self.chat_model = chat_model
        self.image_generator = image_generator
        self.video_generator = video_generator

        # Initialize agents
        self.vsl_scriptwriter = VSLScriptwriter(chat_model=self.chat_model)
        self.thumbnail_generator = ThumbnailGenerator(chat_model=self.chat_model)
        self.headline_generator = HeadlineGenerator(chat_model=self.chat_model)
        self.storyboard_artist = StoryboardArtist(chat_model=self.chat_model)
        self.camera_image_generator = CameraImageGenerator(
            chat_model=self.chat_model,
            image_generator=self.image_generator,
            video_generator=self.video_generator
        )

        self.working_dir = working_dir
        os.makedirs(self.working_dir, exist_ok=True)

    @classmethod
    def init_from_config(cls, config_path: str):
        """Initialize pipeline from YAML configuration file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Initialize chat model
        chat_model_args = config["chat_model"]["init_args"]
        chat_model = init_chat_model(**chat_model_args)

        # Initialize image generator
        image_generator_cls_module, image_generator_cls_name = config["image_generator"]["class_path"].rsplit(".", 1)
        image_generator_cls = getattr(importlib.import_module(image_generator_cls_module), image_generator_cls_name)
        image_generator_args = config["image_generator"]["init_args"]
        image_generator = image_generator_cls(**image_generator_args)

        # Initialize video generator
        video_generator_cls_module, video_generator_cls_name = config["video_generator"]["class_path"].rsplit(".", 1)
        video_generator_cls = getattr(importlib.import_module(video_generator_cls_module), video_generator_cls_name)
        video_generator_args = config["video_generator"]["init_args"]
        video_generator = video_generator_cls(**video_generator_args)

        return cls(
            chat_model=chat_model,
            image_generator=image_generator,
            video_generator=video_generator,
            working_dir=config["working_dir"],
        )

    async def generate_vsl_script(
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
            product: Product or service being promoted
            audience: Target audience description
            benefits: Key benefits and selling points
            duration: "short" (under 5 min), "medium" (5-10 min), or "long" (10-40 min)
            platform: Target platform (e.g., "Facebook ads", "Landing page", "TikTok")
            requirements: Additional specific requirements

        Returns:
            dict with VSL script, hooks, and visual suggestions
        """
        print(f"🔍 Generating VSL script for {platform} ({duration} duration)...")

        timer = Timer()
        timer.start()

        vsl_script = await self.vsl_scriptwriter.write_vsl_script(
            product=product,
            audience=audience,
            benefits=benefits,
            duration=duration,
            platform=platform,
            requirements=requirements,
        )

        timer.stop()
        print(f"✅ VSL script generated in {timer.elapsed_time:.2f}s")

        # Save script to working directory
        script_path = os.path.join(self.working_dir, "vsl_script.json")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(vsl_script, f, ensure_ascii=False, indent=2)
        print(f"💾 Script saved to {script_path}")

        return vsl_script

    async def generate_thumbnails(
        self,
        topic: str,
        audience: str,
        video_type: str = "VSL",
        platform: str = "YouTube",
        emotions: str = "curiosity, desire, urgency",
        context: Optional[str] = None,
        count: int = 5,
    ) -> List[dict]:
        """
        Generate multiple thumbnail concepts for A/B testing.

        Args:
            topic: Video topic/subject
            audience: Target audience
            video_type: Type of video (VSL, ad, etc.)
            platform: Target platform
            emotions: Emotions to evoke (comma-separated)
            context: Additional context
            count: Number of thumbnail variations (default 5)

        Returns:
            List of thumbnail concepts
        """
        print(f"🎨 Generating {count} thumbnail variations...")

        timer = Timer()
        timer.start()

        thumbnail_data = await self.thumbnail_generator.generate_thumbnail_concepts(
            topic=topic,
            audience=audience,
            video_type=video_type,
            platform=platform,
            emotions=emotions,
            context=context,
        )

        timer.stop()
        print(f"✅ {len(thumbnail_data['concepts'])} thumbnails generated in {timer.elapsed_time:.2f}s")

        # Save thumbnails to working directory
        thumbnails_path = os.path.join(self.working_dir, "thumbnails.json")
        with open(thumbnails_path, "w", encoding="utf-8") as f:
            json.dump(thumbnail_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Thumbnails saved to {thumbnails_path}")

        return thumbnail_data

    async def generate_headlines(
        self,
        topic: str,
        audience: str,
        platform: Literal["youtube", "facebook", "google_ads", "landing_page", "tiktok"] = "youtube",
        goal: str = "maximize clicks and conversions",
        tone: str = "urgent and educational",
        context: Optional[str] = None,
    ) -> dict:
        """
        Generate multiple headline variations for A/B testing.

        Args:
            topic: Topic or offer
            audience: Target audience
            platform: Platform for the headline
            goal: Desired outcome
            tone: Desired tone
            context: Additional context

        Returns:
            dict with headline variations and recommendations
        """
        print(f"📝 Generating headlines for {platform}...")

        timer = Timer()
        timer.start()

        headlines_data = await self.headline_generator.generate_headlines(
            topic=topic,
            audience=audience,
            platform=platform,
            goal=goal,
            tone=tone,
            context=context,
        )

        timer.stop()
        print(f"✅ {len(headlines_data['variations'])} headlines generated in {timer.elapsed_time:.2f}s")

        # Save headlines to working directory
        headlines_path = os.path.join(self.working_dir, "headlines.json")
        with open(headlines_path, "w", encoding="utf-8") as f:
            json.dump(headlines_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Headlines saved to {headlines_path}")

        return headlines_data

    async def generate_thumbnail_images(
        self,
        thumbnail_concepts: List[dict],
        output_dir: Optional[str] = None,
    ) -> List[str]:
        """
        Generate actual thumbnail images from concepts.

        Args:
            thumbnail_concepts: List of thumbnail concept dicts
            output_dir: Directory to save images (defaults to working_dir/thumbnails)

        Returns:
            List of paths to generated thumbnail images
        """
        if output_dir is None:
            output_dir = os.path.join(self.working_dir, "thumbnails")
        os.makedirs(output_dir, exist_ok=True)

        print(f"🎨 Generating {len(thumbnail_concepts)} thumbnail images...")

        thumbnail_paths = []

        for i, concept in enumerate(thumbnail_concepts):
            print(f"  Generating thumbnail {i+1}/{len(thumbnail_concepts)}: {concept['title']}...")

            # Generate base image from visual description
            image_prompt = concept['visual_description']
            if concept.get('text_overlay'):
                image_prompt += f" Include large, bold text overlay that says: '{concept['text_overlay']}'"

            try:
                # Generate image using the image generator
                image_output = await self.image_generator.generate(
                    prompt=image_prompt,
                    aspect_ratio="16:9",
                    reference_images=None,
                )

                # Save image
                thumbnail_path = os.path.join(output_dir, f"thumbnail_{i+1}_{concept['title'].replace(' ', '_')}.png")
                if isinstance(image_output, Image.Image):
                    image_output.save(thumbnail_path)
                else:
                    # Handle different image output formats
                    image_output.image.save(thumbnail_path)

                thumbnail_paths.append(thumbnail_path)
                print(f"  ✅ Saved to {thumbnail_path}")

            except Exception as e:
                print(f"  ❌ Error generating thumbnail {i+1}: {e}")
                continue

        print(f"✅ Generated {len(thumbnail_paths)} thumbnail images")
        return thumbnail_paths

    async def __call__(
        self,
        product: str,
        audience: str,
        benefits: str,
        duration: Literal["short", "medium", "long"] = "medium",
        platform: str = "Landing page",
        requirements: Optional[str] = None,
        generate_thumbnails: bool = True,
        generate_headlines: bool = True,
    ) -> dict:
        """
        Run the complete VSL2Video pipeline.

        Args:
            product: Product or service being promoted
            audience: Target audience description
            benefits: Key benefits and selling points
            duration: Target duration ("short", "medium", or "long")
            platform: Target platform
            requirements: Additional requirements
            generate_thumbnails: Whether to generate thumbnail variations
            generate_headlines: Whether to generate headline variations

        Returns:
            dict with all generated assets (script, thumbnails, headlines)
        """
        print("=" * 80)
        print("🚀 Starting VSL2Video Pipeline")
        print("=" * 80)

        results = {}

        # 1. Generate VSL script
        vsl_script = await self.generate_vsl_script(
            product=product,
            audience=audience,
            benefits=benefits,
            duration=duration,
            platform=platform,
            requirements=requirements,
        )
        results["vsl_script"] = vsl_script

        # 2. Generate thumbnails (optional)
        if generate_thumbnails:
            thumbnails = await self.generate_thumbnails(
                topic=product,
                audience=audience,
                video_type="VSL",
                platform=platform,
                emotions="curiosity, desire, urgency",
            )
            results["thumbnails"] = thumbnails

            # Generate actual thumbnail images
            thumbnail_paths = await self.generate_thumbnail_images(
                thumbnail_concepts=thumbnails["concepts"]
            )
            results["thumbnail_paths"] = thumbnail_paths

        # 3. Generate headlines (optional)
        if generate_headlines:
            # Determine platform format
            platform_map = {
                "YouTube": "youtube",
                "Facebook": "facebook",
                "Instagram": "facebook",
                "TikTok": "tiktok",
                "Landing page": "landing_page",
                "Google Ads": "google_ads",
            }
            headline_platform = platform_map.get(platform, "youtube")

            headlines = await self.generate_headlines(
                topic=product,
                audience=audience,
                platform=headline_platform,
            )
            results["headlines"] = headlines

        print("=" * 80)
        print("✅ VSL2Video Pipeline Complete!")
        print("=" * 80)
        print(f"📁 All files saved to: {self.working_dir}")

        return results
