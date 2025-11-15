import os
import json
import logging
import asyncio
import yaml
import importlib
from typing import Optional, List, Literal
from moviepy import VideoFileClip, concatenate_videoclips
from PIL import Image

from agents import DocumentaryScriptwriter, ThumbnailGenerator, HeadlineGenerator
from langchain.chat_models import init_chat_model
from utils.timer import Timer


class Documentary2VideoPipeline:
    """
    Pipeline for generating faceless YouTube documentary content.
    Supports short test segments (under 10 min) and full long-form documentaries (10-40 min).

    This pipeline:
    1. Generates documentary script with chapters and narration
    2. Creates b-roll planning and visual guidelines
    3. Generates multiple thumbnail variations for A/B testing
    4. Generates headline variations for YouTube titles
    5. Produces storyboard for visual elements
    6. Generates video content with voiceover and b-roll
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
        self.documentary_scriptwriter = DocumentaryScriptwriter(chat_model=self.chat_model)
        self.thumbnail_generator = ThumbnailGenerator(chat_model=self.chat_model)
        self.headline_generator = HeadlineGenerator(chat_model=self.chat_model)

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

    async def generate_documentary_script(
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
            topic: Documentary topic/subject
            audience: Target audience description
            duration: "short" (under 10 min test) or "long" (10-40 min full documentary)
            angle: Unique angle or hook for the documentary
            key_points: Main facts or story beats to cover
            requirements: Additional specific requirements

        Returns:
            dict with documentary script, chapters, visual guide, and b-roll list
        """
        print(f"🔍 Generating documentary script on '{topic}' ({duration} duration)...")

        timer = Timer()
        timer.start()

        doc_script = await self.documentary_scriptwriter.write_documentary_script(
            topic=topic,
            audience=audience,
            duration=duration,
            angle=angle,
            key_points=key_points,
            requirements=requirements,
        )

        timer.stop()
        print(f"✅ Documentary script generated in {timer.elapsed_time:.2f}s")

        # Save script to working directory
        script_path = os.path.join(self.working_dir, "documentary_script.json")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(doc_script, f, ensure_ascii=False, indent=2)
        print(f"💾 Script saved to {script_path}")

        # Also save a human-readable text version
        readable_path = os.path.join(self.working_dir, "documentary_script.txt")
        with open(readable_path, "w", encoding="utf-8") as f:
            f.write(doc_script["script"])
        print(f"💾 Readable script saved to {readable_path}")

        return doc_script

    async def generate_thumbnails(
        self,
        topic: str,
        audience: str,
        video_type: str = "Documentary",
        platform: str = "YouTube",
        emotions: str = "curiosity, intrigue, fascination",
        context: Optional[str] = None,
    ) -> dict:
        """
        Generate multiple thumbnail concepts for A/B testing.

        Args:
            topic: Documentary topic
            audience: Target audience
            video_type: Type of video
            platform: Target platform (typically YouTube)
            emotions: Emotions to evoke
            context: Additional context

        Returns:
            dict with thumbnail concepts and recommendations
        """
        print(f"🎨 Generating thumbnail variations for YouTube...")

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
        tone: str = "educational and intriguing",
        context: Optional[str] = None,
    ) -> dict:
        """
        Generate multiple YouTube title variations for A/B testing.

        Args:
            topic: Documentary topic
            audience: Target audience
            tone: Desired tone
            context: Additional context

        Returns:
            dict with headline variations and recommendations
        """
        print(f"📝 Generating YouTube title variations...")

        timer = Timer()
        timer.start()

        headlines_data = await self.headline_generator.generate_headlines(
            topic=topic,
            audience=audience,
            platform="youtube",
            goal="maximize views and watch time",
            tone=tone,
            context=context,
        )

        timer.stop()
        print(f"✅ {len(headlines_data['variations'])} titles generated in {timer.elapsed_time:.2f}s")

        # Save headlines to working directory
        headlines_path = os.path.join(self.working_dir, "youtube_titles.json")
        with open(headlines_path, "w", encoding="utf-8") as f:
            json.dump(headlines_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Titles saved to {headlines_path}")

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
            output_dir: Directory to save images

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
                image_output = await self.image_generator.generate_single_image(
                    prompt=image_prompt,
                    reference_image_paths=[],
                    size="1920x1080",  # YouTube thumbnail size
                )

                # Save image
                thumbnail_path = os.path.join(output_dir, f"thumbnail_{i+1}_{concept['title'].replace(' ', '_')}.png")
                image_output.save(thumbnail_path)

                thumbnail_paths.append(thumbnail_path)
                print(f"  ✅ Saved to {thumbnail_path}")

            except Exception as e:
                print(f"  ❌ Error generating thumbnail {i+1}: {e}")
                continue

        print(f"✅ Generated {len(thumbnail_paths)} thumbnail images")
        return thumbnail_paths

    async def export_youtube_description(
        self,
        doc_script: dict,
        headlines_data: dict,
        additional_info: Optional[str] = None,
    ) -> str:
        """
        Generate a YouTube description with chapters/timestamps.

        Args:
            doc_script: Documentary script with chapters
            headlines_data: Headlines data (for including alternatives)
            additional_info: Additional info to include (links, CTAs, etc.)

        Returns:
            Formatted YouTube description string
        """
        description_lines = []

        # Add alternative title suggestions
        if headlines_data and "variations" in headlines_data:
            description_lines.append("📌 Alternative Title Ideas for Testing:")
            for var in headlines_data["variations"][:3]:
                description_lines.append(f"   • {var['headline']}")
            description_lines.append("")

        # Add chapters/timestamps
        if "chapters" in doc_script:
            description_lines.append("📖 Chapters:")
            for chapter in doc_script["chapters"]:
                timestamp = chapter.get("timestamp", chapter.get("timestamp_start", "0:00"))
                title = chapter.get("title", chapter.get("chapter_title", f"Chapter {chapter.get('chapter_number', '')}"))
                description_lines.append(f"{timestamp} - {title}")
            description_lines.append("")

        # Add additional info if provided
        if additional_info:
            description_lines.append(additional_info)
            description_lines.append("")

        # Add standard YouTube elements
        description_lines.append("👍 If you enjoyed this video, please like and subscribe for more content!")
        description_lines.append("")
        description_lines.append("📢 Turn on notifications to never miss an upload!")

        description = "\n".join(description_lines)

        # Save to file
        desc_path = os.path.join(self.working_dir, "youtube_description.txt")
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"💾 YouTube description saved to {desc_path}")

        return description

    async def __call__(
        self,
        topic: str,
        audience: str,
        duration: Literal["short", "long"] = "long",
        angle: str = "educational deep dive",
        key_points: Optional[str] = None,
        requirements: Optional[str] = None,
        generate_thumbnails: bool = True,
        generate_headlines: bool = True,
    ) -> dict:
        """
        Run the complete Documentary2Video pipeline.

        Args:
            topic: Documentary topic/subject
            audience: Target audience description
            duration: "short" (under 10 min) or "long" (10-40 min)
            angle: Unique angle or hook
            key_points: Main facts to cover
            requirements: Additional requirements
            generate_thumbnails: Whether to generate thumbnail variations
            generate_headlines: Whether to generate YouTube title variations

        Returns:
            dict with all generated assets (script, thumbnails, headlines, description)
        """
        print("=" * 80)
        print("🚀 Starting Documentary2Video Pipeline")
        print("=" * 80)

        results = {}

        # 1. Generate documentary script
        doc_script = await self.generate_documentary_script(
            topic=topic,
            audience=audience,
            duration=duration,
            angle=angle,
            key_points=key_points,
            requirements=requirements,
        )
        results["documentary_script"] = doc_script

        # 2. Generate thumbnails (optional)
        if generate_thumbnails:
            thumbnails = await self.generate_thumbnails(
                topic=topic,
                audience=audience,
                video_type="Documentary",
                platform="YouTube",
            )
            results["thumbnails"] = thumbnails

            # Generate actual thumbnail images
            thumbnail_paths = await self.generate_thumbnail_images(
                thumbnail_concepts=thumbnails["concepts"]
            )
            results["thumbnail_paths"] = thumbnail_paths

        # 3. Generate YouTube titles (optional)
        headlines_data = None
        if generate_headlines:
            headlines_data = await self.generate_headlines(
                topic=topic,
                audience=audience,
            )
            results["youtube_titles"] = headlines_data

        # 4. Generate YouTube description with chapters
        youtube_description = await self.export_youtube_description(
            doc_script=doc_script,
            headlines_data=headlines_data,
        )
        results["youtube_description"] = youtube_description

        print("=" * 80)
        print("✅ Documentary2Video Pipeline Complete!")
        print("=" * 80)
        print(f"📁 All files saved to: {self.working_dir}")

        return results
