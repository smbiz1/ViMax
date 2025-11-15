# CLAUDE.md - AI Assistant Guide for ViMax

**Last Updated**: 2025-11-13
**Codebase Version**: Main branch
**Total LOC**: ~5,259 lines of production code

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Key Architectural Patterns](#key-architectural-patterns)
4. [Development Workflows](#development-workflows)
5. [Important Conventions](#important-conventions)
6. [Configuration System](#configuration-system)
7. [Common Tasks & How-To Guide](#common-tasks--how-to-guide)
8. [Testing & Debugging](#testing--debugging)
9. [File Navigation Guide](#file-navigation-guide)
10. [Agent Collaboration Reference](#agent-collaboration-reference)

---

## Project Overview

### What is ViMax?

**ViMax** is an **Agentic Video Generation** framework that transforms ideas, scripts, or novels into complete videos using a multi-agent system. It automates the entire video production pipeline from narrative conception to final rendering.

### Core Capabilities

- **Idea2Video**: Transform raw ideas into complete video stories
- **Script2Video**: Convert screenplay scripts into professional videos
- **Novel2Video**: Adapt complete novels into episodic video content (in development)
- **AutoCameo**: Generate videos featuring user-provided photos (coming soon)

### Technical Stack

- **Python**: 3.12+
- **Package Manager**: uv (https://docs.astral.sh/uv/)
- **Core Dependencies**:
  - `langchain` + `langchain-openai` + `langchain-community` (LLM orchestration)
  - `google-genai` (Google AI integration)
  - `openai` (OpenAI API)
  - `faiss-cpu` (vector similarity search)
  - `moviepy` (video editing)
  - `opencv-python` (image/video processing)
  - `scenedetect` (scene detection)
  - `pydantic` (data validation)

### Project Philosophy

ViMax mimics a **professional film production workflow**:
1. **Screenwriter** creates the narrative
2. **Storyboard Artist** designs shot sequences
3. **Character Designer** creates character references
4. **Director of Photography** plans camera movements
5. **Production Team** generates visual assets
6. **Editor** assembles the final video

---

## Codebase Structure

```
ViMax/
├── agents/              # AI agent components (14 files, ~2,800 LOC)
├── pipelines/           # Orchestration workflows (4 files, ~1,200 LOC)
├── interfaces/          # Pydantic data models (10 files, ~800 LOC)
├── tools/               # External API integrations (7 files, ~300 LOC)
├── utils/               # Helper utilities (5 files, ~150 LOC)
├── configs/             # YAML configuration files (2 files)
├── assets/              # Static resources (images, etc.)
├── main_idea2video.py   # Entry point for idea-to-video workflow
├── main_script2video.py # Entry point for script-to-video workflow
├── pyproject.toml       # Project dependencies
├── uv.lock              # Dependency lock file
└── README.md            # User-facing documentation
```

### Directory Responsibilities

#### `/agents` - AI Agent Components
**Purpose**: Core intelligence layer containing specialized AI agents

**Key Files**:
- `screenwriter.py` - Story development and script writing
- `storyboard_artist.py` - Shot sequence planning and visual decomposition
- `character_extractor.py` - Extract character information from scripts
- `character_portraits_generator.py` - Generate character reference portraits
- `camera_image_generator.py` - Camera tree construction and transition videos
- `reference_image_selector.py` - Select optimal reference images for consistency
- `best_image_selector.py` - Choose best image from multiple candidates
- `scene_extractor.py`, `event_extractor.py` - Extract narrative units
- `script_enhancer.py`, `script_planner.py` - Script optimization
- `global_information_planner.py` - Cross-scene planning
- `novel_compressor.py` - Long-form content compression

**Agent Pattern**: All agents follow a consistent structure:
```python
class AgentName:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.system_prompt = "..."

    @retry(stop=stop_after_attempt(3), after=after_func)
    async def primary_method(self, input_data):
        # LLM call with structured output
        # Save results to disk
        # Return Pydantic model
```

#### `/pipelines` - Orchestration Layer
**Purpose**: High-level workflows coordinating multiple agents

**Key Files**:
- `idea2video_pipeline.py` - Complete idea-to-video workflow
- `script2video_pipeline.py` - Script-to-video conversion (most complex, 625 lines)
- `novel2movie_pipeline.py` - Novel adaptation (in development)
- `idea2video_pipeline_deprecated.py` - Legacy implementation

**Pipeline Pattern**: Async orchestration with caching and resumability
```python
class PipelineName:
    def __init__(self, config):
        # Initialize agents and tools from config

    async def run(self, input_data, working_dir):
        # Create working directory structure
        # Execute multi-step workflow
        # Cache intermediate results
        # Return final output
```

#### `/interfaces` - Data Models
**Purpose**: Pydantic models defining all data structures

**Key Files**:
- `character.py` - Character representations (in scene, event, novel)
- `shot_description.py` - Shot metadata and visual decomposition
- `camera.py` - Camera tree structure
- `frame.py` - Frame representation
- `image_output.py`, `video_output.py` - Unified output wrappers
- `scene.py`, `event.py`, `environment.py` - Narrative structures

**Data Model Pattern**: All models extend Pydantic's BaseModel
```python
from pydantic import BaseModel, Field

class ModelName(BaseModel):
    field_name: type = Field(description="...")

    # Optional: custom validators, methods
```

#### `/tools` - External API Integrations
**Purpose**: Wrappers for generative AI services

**Image Generators**:
- `ImageGeneratorNanobananaGoogleAPI` - Google Gemini image generation
- `ImageGeneratorDoubaoSeedreamYunwuAPI` - Doubao/Yunwu API
- `ImageGeneratorNanobananaYunwuAPI` - Nanobanana via Yunwu

**Video Generators**:
- `VideoGeneratorVeoGoogleAPI` - Google Veo 3.1
- `VideoGeneratorDoubaoSeedanceYunwuAPI` - Doubao Seedance
- `VideoGeneratorVeoYunwuAPI` - Veo via Yunwu

**Other Tools**:
- `reranker.py` - BGE-based reranking for RAG

**Tool Pattern**: Consistent interface for swappable implementations
```python
class GeneratorName:
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key

    async def generate_single_image(self, prompt, reference_images):
        # API call
        # Return ImageOutput

    async def generate_single_video(self, first_frame, last_frame, prompt):
        # API call
        # Return VideoOutput
```

#### `/utils` - Helper Utilities
**Purpose**: Common functionality used across the codebase

**Files**:
- `retry.py` - Retry logic with logging for failed operations
- `timer.py` - Timing decorator and context manager
- `image.py` - Image processing utilities (resize, crop, etc.)
- `video.py` - Video processing utilities (concatenation, encoding)

#### `/configs` - Configuration Files
**Purpose**: YAML files defining pipeline configurations

**Files**:
- `idea2video.yaml` - Configuration for idea-to-video pipeline
- `script2video.yaml` - Configuration for script-to-video pipeline

**Configuration Schema**:
```yaml
chat_model:
  init_args:
    model: string
    model_provider: string
    api_key: string
    base_url: string (optional)

image_generator:
  class_path: string (e.g., "tools.ImageGeneratorNanobananaGoogleAPI")
  init_args:
    api_key: string

video_generator:
  class_path: string (e.g., "tools.VideoGeneratorVeoGoogleAPI")
  init_args:
    api_key: string

working_dir: string (path to store intermediate files)
```

---

## Key Architectural Patterns

### 1. Multi-Agent Orchestration

**Pattern**: Specialized agents collaborate through sequential and parallel workflows

**Example**: Script2Video Pipeline
```
Script → Character Extraction → Portrait Generation → Storyboard Design →
Visual Decomposition → Camera Tree Construction → Frame Generation →
Video Generation → Concatenation
```

**Key Insight**: Each agent has a single, well-defined responsibility. Complex tasks are decomposed into agent chains.

### 2. Pydantic-First Data Modeling

**Pattern**: All data structures use Pydantic BaseModel for validation and serialization

**Benefits**:
- Type safety at runtime
- Automatic JSON serialization/deserialization
- Clear documentation via Field descriptions
- Easy integration with LangChain's structured output parsers

**Example**:
```python
class CharacterInScene(BaseModel):
    idx: int = Field(description="Character index in scene")
    identifier_in_scene: str = Field(description="Character name/role")
    is_visible: bool = Field(description="Whether character is visible")
    static_features: str = Field(description="Immutable physical features")
    dynamic_features: str = Field(description="Clothing, accessories, etc.")
```

### 3. Output Abstraction

**Pattern**: Unified output interfaces supporting multiple formats

**Purpose**: Different APIs return data in different formats (base64, URL, PIL Image, NumPy array). The abstraction layer provides a consistent interface.

**Example**:
```python
class ImageOutput:
    fmt: Literal["b64", "url", "pil", "np"]
    data: Union[str, Image.Image, np.ndarray]

    def save(self, path: str):
        # Automatically choose correct save method based on format
        save_func = getattr(self, f"save_{self.fmt}")
        save_func(path)
```

### 4. Retry with Logging

**Pattern**: All agent methods use @retry decorator with custom logging

**Purpose**: LLM/API calls can fail due to rate limits, network issues, or model errors. Automatic retries with logging ensure robustness.

**Implementation**:
```python
from utils.retry import retry, after_func
from tenacity import stop_after_attempt

@retry(stop=stop_after_attempt(3), after=after_func)
async def agent_method(self, input_data):
    # LLM call that may fail
    response = await self.chat_model.ainvoke(messages)
    return response
```

**after_func** logs the exception traceback to help with debugging.

### 5. Caching and Resumability

**Pattern**: All intermediate results are saved to disk; pipeline checks for cached data before regenerating

**Purpose**:
- Resume interrupted pipelines without losing progress
- Faster iterations during development
- Cost savings (avoid redundant LLM/API calls)

**Implementation**:
```python
save_path = os.path.join(working_dir, "characters.json")
if os.path.exists(save_path):
    with open(save_path, "r") as f:
        characters = [CharacterInScene(**c) for c in json.load(f)]
else:
    characters = await character_extractor.extract_characters(script)
    with open(save_path, "w") as f:
        json.dump([c.model_dump() for c in characters], f, indent=2)
```

**Convention**: Use descriptive filenames (e.g., `characters.json`, `storyboard.json`, `camera_tree.json`)

### 6. Async/Await Throughout

**Pattern**: All I/O operations are asynchronous

**Purpose**: Maximize throughput by allowing concurrent operations

**Key Areas**:
- LLM calls: `await chat_model.ainvoke(messages)`
- Image generation: `await image_generator.generate_single_image()`
- Video generation: `await video_generator.generate_single_video()`
- Parallel processing: `await asyncio.gather(*tasks)`

**Example**:
```python
# Generate character portraits in parallel
tasks = [
    character_portraits_generator.generate_portrait(char)
    for char in characters
]
portraits = await asyncio.gather(*tasks)
```

### 7. Camera Tree Architecture

**Pattern**: Hierarchical structure representing camera relationships

**Purpose**: Enable smooth transitions and consistency across shots

**Structure**:
```python
class Camera(BaseModel):
    idx: int
    active_shot_idxs: List[int]  # Shots filmed by this camera
    parent_cam_idx: Optional[int]  # Parent camera (e.g., wide shot)
    parent_shot_idx: Optional[int]  # Specific parent shot
    is_parent_fully_covers_child: Optional[bool]
    missing_info: Optional[str]
```

**Example**:
```
Camera 0 (wide shot of room) - Parent
├── Camera 1 (medium shot of character A) - Child
└── Camera 2 (close-up of character B) - Child
```

**Key Insight**: Wide shots serve as parents for close-ups, ensuring spatial/temporal consistency.

### 8. Structured Prompting Convention

**Pattern**: All agent prompts follow a consistent structure

**Template**:
```
[Role]
You are a <expert type> specializing in <domain>.

[Task]
<Clear, specific task description>

[Input]
<XML-tagged input data>
{input_variable}
</XML-tagged>

[Output]
{format_instructions}  # Pydantic schema

[Guidelines]
- Guideline 1
- Guideline 2
- ...
```

**Benefits**:
- Consistent LLM performance
- Easier to debug and iterate on prompts
- Clear separation of role, task, and constraints

### 9. Frame Variation System

**Pattern**: Three-tier classification for shot complexity

**Categories**:
- **Small**: Minor changes (facial expressions, hand gestures)
- **Medium**: New characters appear, character turns/rotations
- **Large**: Significant composition changes (e.g., wide → close-up transitions)

**Impact**: Determines whether `last_frame` is needed for video generation
- Small/Medium: Only `first_frame` needed
- Large: Both `first_frame` and `last_frame` needed

### 10. Event-Driven Coordination

**Pattern**: AsyncIO events manage dependencies between parallel tasks

**Purpose**: Some frames depend on others (e.g., camera transitions). Events ensure correct execution order.

**Implementation**:
```python
# Create events for each shot
self.frame_events[shot_idx] = {
    "first_frame": asyncio.Event(),
    "last_frame": asyncio.Event()
}

# Wait for dependency
await self.frame_events[parent_shot_idx]["first_frame"].wait()

# Generate frame
frame = await generate_frame(...)

# Signal completion
self.frame_events[shot_idx]["first_frame"].set()
```

---

## Development Workflows

### Idea2Video Workflow

**Entry Point**: `main_idea2video.py`

**Input**:
```python
idea = "If a cat and a dog are best friends, what would happen when they meet a new cat?"
user_requirement = "For children, do not exceed 3 scenes."
style = "Cartoon"
```

**Pipeline Steps**:
1. **Story Development** (`Screenwriter`)
   - Input: idea, user_requirement, style
   - Output: Narrative story with character descriptions
   - File: `story.txt`

2. **Character Extraction** (`CharacterExtractor`)
   - Input: story
   - Output: List of characters with static/dynamic features
   - File: `characters.json`

3. **Portrait Generation** (`CharacterPortraitsGenerator`)
   - Input: characters
   - Output: Front/side/back view portraits for each character
   - Files: `portraits/{character_idx}_front.png`, `_side.png`, `_back.png`

4. **Script Writing** (`Screenwriter`)
   - Input: story, characters
   - Output: Multi-scene screenplay
   - File: `script.txt`

5. **Scene Processing** (For each scene, run Script2Video pipeline)
   - Input: scene script, characters, portraits
   - Output: scene video
   - Files: `scene_{idx}/final_video.mp4`

6. **Video Concatenation**
   - Input: All scene videos
   - Output: Final video
   - File: `final_video.mp4`

### Script2Video Workflow

**Entry Point**: `main_script2video.py`

**Input**:
```python
script = """
EXT. SCHOOL GYM - DAY
A group of students are practicing basketball in the gym...
John: (dribbling the ball) I'm going to score a basket!
Jane: (smiling) Good job, John!
"""
user_requirement = "Fast-paced with no more than 15 shots."
style = "Anime Style"
```

**Pipeline Steps**:
1. **Character Extraction** (`CharacterExtractor`)
   - File: `characters.json`

2. **Portrait Generation** (`CharacterPortraitsGenerator`)
   - Files: `portraits/{character_idx}_{view}.png`

3. **Storyboard Design** (`StoryboardArtist`)
   - Input: script, user_requirement, characters
   - Output: List of shots with descriptions
   - File: `storyboard.json`

4. **Visual Decomposition** (`StoryboardArtist`)
   - For each shot, decompose into:
     - `first_frame_static_description`
     - `last_frame_static_description`
     - `first_frame_to_last_frame_motion_description`
     - `variation_type` (small/medium/large)
   - File: `shot_descriptions.json`

5. **Camera Tree Construction** (`CameraImageGenerator`)
   - Analyze shots and build hierarchical camera relationships
   - File: `camera_tree.json`

6. **Transition Video Generation** (`CameraImageGenerator`)
   - For each parent-child camera pair, generate transition video
   - Files: `camera_transitions/camera_{idx}_to_{child_idx}.mp4`

7. **Frame Generation** (Complex parallel system)
   - For each camera:
     - Generate first frame of first shot (using reference selection)
     - Extract frames from transition videos for subsequent camera changes
     - Generate remaining frames (parallel per camera)
   - Files: `frames/shot_{idx}_first_frame.png`, `_last_frame.png`

8. **Video Generation** (Parallel)
   - For each shot, generate video from frames + motion prompt
   - Files: `videos/shot_{idx}.mp4`

9. **Video Concatenation**
   - Combine all shots in sequence
   - File: `final_video.mp4`

---

## Important Conventions

### File Organization

**Working Directory Structure**:
```
.working_dir/{pipeline_name}/
├── characters.json
├── portraits/
│   ├── {character_idx}_front.png
│   ├── {character_idx}_side.png
│   └── {character_idx}_back.png
├── storyboard.json
├── shot_descriptions.json
├── camera_tree.json
├── camera_transitions/
│   └── camera_{idx}_to_{child_idx}.mp4
├── frames/
│   ├── shot_{idx}_first_frame.png
│   └── shot_{idx}_last_frame.png
├── videos/
│   └── shot_{idx}.mp4
└── final_video.mp4
```

**Naming Conventions**:
- Use snake_case for files and directories
- Use descriptive names (e.g., `character_extractor.py`, not `extractor.py`)
- Index files with zero-padded numbers (e.g., `shot_0001.mp4`)
- Use `.json` for Pydantic model exports
- Use `.txt` for plain text (scripts, stories)

### Code Style

**Imports**:
```python
# Standard library
import os
import json
import asyncio
from typing import List, Optional, Dict

# Third-party
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Local
from interfaces.character import CharacterInScene
from utils.retry import retry, after_func
```

**Async Methods**:
```python
# Always use async for I/O operations
async def method_name(self, param: type) -> return_type:
    result = await self.async_operation()
    return result

# Use asyncio.gather for parallel operations
results = await asyncio.gather(*tasks)
```

**Error Handling**:
```python
# Let @retry handle transient errors
@retry(stop=stop_after_attempt(3), after=after_func)
async def method_with_retry(self):
    # This will retry up to 3 times if it raises an exception
    pass

# Handle specific errors explicitly
try:
    result = await operation()
except SpecificError as e:
    # Handle or log
    raise
```

**Logging**:
```python
# Use print statements for user-facing progress
print(f"[CharacterExtractor] Extracting characters from script...")

# after_func in retry.py logs exceptions automatically
# No need for explicit exception logging in most cases
```

### Data Persistence

**Saving Pydantic Models**:
```python
# Single model
with open(path, "w") as f:
    json.dump(model.model_dump(), f, indent=2)

# List of models
with open(path, "w") as f:
    json.dump([m.model_dump() for m in models], f, indent=2)
```

**Loading Pydantic Models**:
```python
# Single model
with open(path, "r") as f:
    data = json.load(f)
    model = ModelClass(**data)

# List of models
with open(path, "r") as f:
    data = json.load(f)
    models = [ModelClass(**item) for item in data]
```

**Saving Images**:
```python
# Use ImageOutput abstraction
image_output.save(path)  # Automatically handles format

# Or directly with PIL
from PIL import Image
image.save(path)
```

**Saving Videos**:
```python
# Use VideoOutput abstraction
video_output.save(path)

# Or with moviepy
from moviepy.editor import VideoFileClip
clip.write_videofile(path, codec="libx264", audio_codec="aac")
```

### LLM Integration

**Structured Output**:
```python
from langchain_core.output_parsers import PydanticOutputParser

# Create parser
parser = PydanticOutputParser(pydantic_object=ModelClass)

# Format instructions
format_instructions = parser.get_format_instructions()

# Include in prompt
prompt = f"""
[Output]
{format_instructions}
"""

# Parse response
result = parser.parse(llm_response.content)
```

**Chat Model Usage**:
```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt)
]

response = await self.chat_model.ainvoke(messages)
result = parser.parse(response.content)
```

### API Integration

**Image Generation**:
```python
# All image generators follow this interface
image_output = await image_generator.generate_single_image(
    prompt=prompt,
    reference_images=[ref1, ref2, ...]  # Optional
)

# Save result
image_output.save(save_path)
```

**Video Generation**:
```python
# All video generators follow this interface
video_output = await video_generator.generate_single_video(
    first_frame=first_frame_path,
    last_frame=last_frame_path,  # Optional (for large variations)
    prompt=motion_prompt
)

# Save result
video_output.save(save_path)
```

---

## Configuration System

### Configuration Loading

**In main files**:
```python
import yaml

with open("configs/idea2video.yaml", "r") as f:
    config = yaml.safe_load(f)
```

**In pipelines**:
```python
import importlib

# Dynamic class loading
image_generator_cls_path = config["image_generator"]["class_path"]
module_name, class_name = image_generator_cls_path.rsplit(".", 1)
image_generator_cls = getattr(importlib.import_module(module_name), class_name)

# Instantiation
image_generator = image_generator_cls(
    **config["image_generator"]["init_args"]
)
```

### Adding New Providers

**Step 1**: Implement the tool interface

```python
# tools/image_generator_new_provider.py
class ImageGeneratorNewProvider:
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        # Initialize client

    async def generate_single_image(
        self,
        prompt: str,
        reference_images: List[str] = None
    ) -> ImageOutput:
        # API call
        # Return ImageOutput
```

**Step 2**: Update configuration

```yaml
image_generator:
  class_path: tools.ImageGeneratorNewProvider
  init_args:
    api_key: <YOUR_API_KEY>
    # Additional provider-specific args
```

**Step 3**: No code changes needed! The pipeline will automatically use the new provider.

### Switching Between Providers

**Example: Google AI Studio vs OpenRouter**:

```yaml
# Using Google AI Studio directly
chat_model:
  init_args:
    model: gemini-2.0-flash-exp
    model_provider: google
    api_key: <GOOGLE_API_KEY>

# Using OpenRouter
chat_model:
  init_args:
    model: google/gemini-2.5-flash-lite-preview-09-2025
    model_provider: openai
    api_key: <OPENROUTER_API_KEY>
    base_url: https://openrouter.ai/api/v1
```

**Supported Model Providers**:
- `google` - Google AI Studio (native)
- `openai` - OpenAI API
- `openai` with `base_url` - OpenRouter, Yunwu, or other OpenAI-compatible APIs

---

## Common Tasks & How-To Guide

### Task 1: Add a New Agent

**Scenario**: You want to add a new agent (e.g., `AudioDescriptionGenerator`)

**Steps**:

1. **Create agent file**: `agents/audio_description_generator.py`

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from utils.retry import retry, after_func
from tenacity import stop_after_attempt

class AudioDescriptionGenerator:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.system_prompt = """
[Role]
You are an expert audio designer for film and video.

[Task]
Generate detailed audio descriptions for each shot.

[Input]
<SHOT>
{shot_description}
</SHOT>

[Output]
{format_instructions}
"""

    @retry(stop=stop_after_attempt(3), after=after_func)
    async def generate_audio_description(self, shot_description: str):
        parser = PydanticOutputParser(pydantic_object=AudioDescription)

        prompt = self.system_prompt.format(
            shot_description=shot_description,
            format_instructions=parser.get_format_instructions()
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=shot_description)
        ]

        response = await self.chat_model.ainvoke(messages)
        result = parser.parse(response.content)

        return result
```

2. **Create data model**: `interfaces/audio_description.py`

```python
from pydantic import BaseModel, Field

class AudioDescription(BaseModel):
    dialogue: str = Field(description="Character dialogue")
    sound_effects: str = Field(description="Sound effects")
    background_music: str = Field(description="Background music style")
```

3. **Integrate into pipeline**: `pipelines/script2video_pipeline.py`

```python
from agents.audio_description_generator import AudioDescriptionGenerator

class Script2VideoPipeline:
    def __init__(self, config):
        # ... existing initialization
        self.audio_description_generator = AudioDescriptionGenerator(self.chat_model)

    async def run(self, script, style, user_requirement, working_dir):
        # ... existing steps

        # Add new step
        audio_descriptions_path = os.path.join(working_dir, "audio_descriptions.json")
        if os.path.exists(audio_descriptions_path):
            with open(audio_descriptions_path, "r") as f:
                audio_descriptions = [AudioDescription(**a) for a in json.load(f)]
        else:
            tasks = [
                self.audio_description_generator.generate_audio_description(shot.description)
                for shot in shot_descriptions
            ]
            audio_descriptions = await asyncio.gather(*tasks)

            with open(audio_descriptions_path, "w") as f:
                json.dump([a.model_dump() for a in audio_descriptions], f, indent=2)

        # Use audio_descriptions in subsequent steps
```

### Task 2: Modify an Existing Agent's Prompt

**Scenario**: Improve the `CharacterExtractor` prompt to better handle complex scripts

**Steps**:

1. **Locate the agent**: `agents/character_extractor.py`

2. **Find the prompt**: Look for `self.system_prompt` or similar

3. **Modify the prompt**:

```python
# Before
self.system_prompt = """
[Role]
You are a script analysis expert.

[Task]
Extract character information.
"""

# After
self.system_prompt = """
[Role]
You are a top-tier script analysis expert with expertise in character development,
narrative structure, and visual storytelling.

[Task]
Extract comprehensive character information from the provided script, including:
1. Physical appearance (static features that never change)
2. Clothing and accessories (dynamic features that may change)
3. Personality traits (to inform visual characterization)
4. Role in the story (protagonist, antagonist, supporting)

[Guidelines]
- Static features should be immutable (e.g., species, gender, height, facial structure)
- Dynamic features can change across scenes (e.g., outfits, props)
- Use specific, visual language (avoid abstract descriptions)
- Consider cultural context and age appropriateness for the target audience
"""
```

4. **Test the changes**: Run the pipeline with a test script

5. **Iterate**: Review the output, adjust the prompt, and test again

**Prompt Engineering Tips**:
- Be specific about what you want
- Use examples (few-shot prompting) when helpful
- Add constraints to prevent common errors
- Use structured sections ([Role], [Task], [Guidelines])

### Task 3: Add Support for a New Video Generator

**Scenario**: Integrate a new video generation API (e.g., Runway Gen-4)

**Steps**:

1. **Create tool file**: `tools/video_generator_runway.py`

```python
from interfaces.video_output import VideoOutput
import aiohttp

class VideoGeneratorRunway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runwayml.com/v1"

    async def generate_single_video(
        self,
        first_frame: str,
        last_frame: str = None,
        prompt: str = ""
    ) -> VideoOutput:
        # Read first frame
        with open(first_frame, "rb") as f:
            first_frame_data = f.read()

        # Prepare request
        payload = {
            "first_frame": first_frame_data,
            "prompt": prompt
        }

        if last_frame:
            with open(last_frame, "rb") as f:
                payload["last_frame"] = f.read()

        # API call
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/generate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            ) as response:
                result = await response.json()
                video_url = result["video_url"]

        # Download video
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                video_data = await response.read()

        # Return VideoOutput
        return VideoOutput(fmt="bytes", data=video_data)
```

2. **Update configuration**: `configs/script2video.yaml`

```yaml
video_generator:
  class_path: tools.VideoGeneratorRunway
  init_args:
    api_key: <RUNWAY_API_KEY>
```

3. **Test**: Run the pipeline and verify videos are generated correctly

**Note**: No changes to the pipeline code are needed due to the dynamic class loading pattern.

### Task 4: Debug a Failed Pipeline Run

**Scenario**: Pipeline crashes during frame generation

**Debugging Steps**:

1. **Check the working directory**:
   - Look for incomplete files (e.g., missing `frames/shot_0005_first_frame.png`)
   - Identify which step failed

2. **Review logs**:
   - The `@retry` decorator logs exceptions via `after_func`
   - Look for traceback in console output

3. **Inspect cached data**:
   - Load intermediate JSON files to verify data integrity
   ```python
   import json
   with open(".working_dir/script2video/shot_descriptions.json", "r") as f:
       shot_descriptions = json.load(f)

   # Check for issues
   for shot in shot_descriptions:
       if not shot.get("first_frame_static_description"):
           print(f"Missing description for shot {shot['idx']}")
   ```

4. **Resume from checkpoint**:
   - Delete the problematic file (if corrupted)
   - Re-run the pipeline (it will regenerate only missing files)

5. **Add temporary debug logging**:
   ```python
   # In the failing agent/pipeline method
   print(f"[DEBUG] Input data: {input_data}")
   result = await problematic_operation(input_data)
   print(f"[DEBUG] Output data: {result}")
   ```

6. **Isolate the problem**:
   - Extract the failing operation into a standalone script
   - Test with simplified inputs
   - Verify API keys, quotas, and network connectivity

### Task 5: Optimize Pipeline Performance

**Scenario**: Pipeline is too slow for long videos

**Optimization Strategies**:

1. **Increase Parallelism**:
   ```python
   # Before: Sequential processing
   frames = []
   for shot in shots:
       frame = await generate_frame(shot)
       frames.append(frame)

   # After: Parallel processing
   tasks = [generate_frame(shot) for shot in shots]
   frames = await asyncio.gather(*tasks)
   ```

2. **Use Faster Models**:
   ```yaml
   # Before
   chat_model:
     init_args:
       model: google/gemini-2.0-flash-thinking-exp-01-21

   # After (faster, cheaper)
   chat_model:
     init_args:
       model: google/gemini-2.5-flash-lite-preview-09-2025
   ```

3. **Reduce Redundant Calls**:
   - Ensure caching is working correctly
   - Avoid regenerating unchanged data

4. **Optimize Image/Video Processing**:
   ```python
   # Use lower resolution for intermediate frames
   image = image.resize((512, 512))  # Instead of (1024, 1024)

   # Compress videos with lower quality settings
   clip.write_videofile(path, bitrate="500k")  # Instead of "5000k"
   ```

5. **Profile the Pipeline**:
   ```python
   from utils.timer import timer

   @timer
   async def slow_operation():
       # ... operation

   # This will print: "[Timer] slow_operation took 12.34s"
   ```

6. **Batch API Calls**:
   ```python
   # If the API supports batch requests
   results = await api.generate_batch(prompts_list)

   # Instead of
   results = [await api.generate(prompt) for prompt in prompts_list]
   ```

---

## Testing & Debugging

### Manual Testing

**Test Individual Agents**:
```python
# test_character_extractor.py
import asyncio
from langchain_openai import ChatOpenAI
from agents.character_extractor import CharacterExtractor

async def test():
    chat_model = ChatOpenAI(model="gpt-4o", api_key="...")
    extractor = CharacterExtractor(chat_model)

    script = """
    EXT. PARK - DAY
    A cat and a dog are playing together.
    """

    characters = await extractor.extract_characters(script)
    print(characters)

asyncio.run(test())
```

**Test Pipelines with Minimal Input**:
```python
# Test with a very short script (1 shot)
script = """
EXT. PARK - DAY
A cat sits on a bench.
"""
user_requirement = "Only 1 shot."
style = "Cartoon"

# Run pipeline
# Should complete quickly and cheaply
```

### Common Errors

**Error**: `KeyError: 'api_key'`
- **Cause**: Missing API key in config
- **Fix**: Add `api_key` to config YAML

**Error**: `asyncio.TimeoutError`
- **Cause**: API call taking too long
- **Fix**: Increase timeout or check network connectivity

**Error**: `FileNotFoundError: 'frames/shot_0005_first_frame.png'`
- **Cause**: Frame generation failed for a specific shot
- **Fix**: Check logs for the specific error, regenerate that frame

**Error**: `JSONDecodeError`
- **Cause**: LLM returned invalid JSON
- **Fix**:
  - Check prompt format instructions
  - Add examples to the prompt
  - Use a more capable model

**Error**: `pydantic.ValidationError`
- **Cause**: LLM output doesn't match Pydantic schema
- **Fix**:
  - Simplify the schema
  - Add more explicit instructions in the prompt
  - Add default values to optional fields

### Logging Best Practices

**User-Facing Progress**:
```python
print(f"[{self.__class__.__name__}] Starting operation...")
print(f"[{self.__class__.__name__}] Processing {len(items)} items...")
print(f"[{self.__class__.__name__}] Completed in {elapsed:.2f}s")
```

**Debug Information** (temporary):
```python
import json
print(f"[DEBUG] Intermediate data: {json.dumps(data, indent=2)}")
```

**Exception Logging** (handled by `after_func`):
- No need to manually log exceptions in methods decorated with `@retry`
- `after_func` automatically logs the full traceback

---

## File Navigation Guide

### Finding Specific Functionality

**"Where is character extraction implemented?"**
- **Agent**: `/home/user/ViMax/agents/character_extractor.py`
- **Data Model**: `/home/user/ViMax/interfaces/character.py`
- **Usage**: Search for `CharacterExtractor` in pipelines

**"Where are camera trees built?"**
- **Agent**: `/home/user/ViMax/agents/camera_image_generator.py`
- **Data Model**: `/home/user/ViMax/interfaces/camera.py`
- **Method**: `construct_camera_tree()`

**"Where is the storyboard designed?"**
- **Agent**: `/home/user/ViMax/agents/storyboard_artist.py`
- **Methods**:
  - `design_storyboard()` - Create shot list
  - `decompose_storyboard_with_first_last_frame()` - Visual decomposition

**"Where are reference images selected?"**
- **Agent**: `/home/user/ViMax/agents/reference_image_selector.py`
- **Method**: `select_reference_images()`

**"Where is the final video concatenated?"**
- **Pipeline**: `/home/user/ViMax/pipelines/script2video_pipeline.py`
- **Section**: Near the end of `run()` method
- **Tool**: Uses `moviepy.editor.concatenate_videoclips()`

### Code Organization Principles

**Agents**: Single-responsibility, focused on one task
**Pipelines**: Orchestration, coordinate multiple agents
**Interfaces**: Data models, no business logic
**Tools**: External API wrappers, no business logic
**Utils**: Pure functions, no state

**Dependency Direction**:
```
Pipelines → Agents → Interfaces
         → Tools  → Interfaces
         → Utils  → (nothing)
```

**Never**:
- Agents should not import Pipelines
- Interfaces should not import Agents or Tools
- Utils should not import anything from the project (only standard library)

---

## Agent Collaboration Reference

### Idea2Video Pipeline Agent Flow

```
1. Screenwriter.develop_story()
   Input: idea, user_requirement, style
   Output: Narrative story

2. CharacterExtractor.extract_characters()
   Input: story
   Output: List[CharacterInStory]

3. CharacterPortraitsGenerator.generate_portraits()
   Input: characters
   Output: Character portrait images (front/side/back)

4. Screenwriter.write_script()
   Input: story, characters
   Output: Multi-scene script

5. [For each scene] Script2VideoPipeline.run()
   Input: scene script, characters, portraits
   Output: Scene video

6. Concatenate all scene videos
   Output: Final video
```

### Script2Video Pipeline Agent Flow

```
1. CharacterExtractor.extract_characters()
   Input: script
   Output: List[CharacterInScene]

2. CharacterPortraitsGenerator.generate_portraits()
   Input: characters
   Output: Portrait images

3. StoryboardArtist.design_storyboard()
   Input: script, user_requirement, characters
   Output: List[ShotBriefDescription]

4. StoryboardArtist.decompose_storyboard_with_first_last_frame()
   Input: storyboard
   Output: List[ShotDescription] with first/last frame details

5. CameraImageGenerator.construct_camera_tree()
   Input: shot_descriptions
   Output: List[Camera]

6. CameraImageGenerator.generate_transition_videos()
   Input: camera_tree, shot_descriptions
   Output: Transition videos between cameras

7. ReferenceImageSelector.select_reference_images() [For each frame]
   Input: shot, available_images
   Output: Selected reference images + enhanced prompt

8. ImageGenerator.generate_single_image() [For each frame]
   Input: prompt, reference_images
   Output: Frame image

9. VideoGenerator.generate_single_video() [For each shot]
   Input: first_frame, last_frame (optional), motion_prompt
   Output: Shot video

10. Concatenate all shot videos
    Output: Final video
```

### Key Collaboration Patterns

**Sequential Dependencies**:
- Character extraction must complete before portrait generation
- Storyboard design must complete before visual decomposition
- Camera tree must be built before transition video generation

**Parallel Operations**:
- Character portraits can be generated in parallel
- Frames within a camera can be generated in parallel
- Shot videos can be generated in parallel

**Event-Driven Coordination**:
- Frame generation waits for dependent frames (via AsyncIO events)
- Camera transitions depend on parent camera frames

---

## Working with Long-Form Content

### Novel2Video Considerations

**Challenges**:
- Novels can be hundreds of thousands of words
- Need to compress into manageable video length
- Maintain character consistency across many scenes
- Track complex plot threads

**Approach** (in development):
1. **NovelCompressor** - Segment novel into episodes
2. **SceneExtractor** - Extract key scenes from each episode
3. **EventExtractor** - Extract key events within scenes
4. **GlobalInformationPlanner** - Track characters/locations across episodes
5. Standard pipeline for each episode

**Status**: Novel2Video pipeline is partially implemented in `pipelines/novel2movie_pipeline.py`

---

## Future Enhancements

### Coming Soon (per README)

- Google AI Studio API config (completed ✅)
- Dev mode branch (in progress)
- AutoCameo integration (planned)
- More demos (ongoing)
- Shot planning improvements (planned)
- New features (TBD)

### Potential Areas for AI Assistant Contributions

1. **Improved Prompts**: Iterate on agent prompts for better output quality
2. **New Agents**: Audio generation, subtitle creation, scene detection
3. **API Integrations**: Support for more LLM/image/video providers
4. **Performance**: Caching strategies, batch processing, parallel optimizations
5. **Quality Control**: Automated validation of generated content
6. **Documentation**: Code comments, docstrings, examples
7. **Testing**: Unit tests, integration tests, end-to-end tests
8. **Error Handling**: More robust retry logic, graceful degradation

---

## Summary for AI Assistants

### Key Takeaways

1. **Architecture**: Multi-agent pipeline with Pydantic data models and async/await
2. **Modularity**: Agents, pipelines, interfaces, tools, utils are clearly separated
3. **Extensibility**: New agents/tools can be added without modifying core code
4. **Robustness**: Caching, retries, and error logging ensure reliability
5. **Performance**: Parallel processing and async I/O maximize throughput

### Development Principles

- **Single Responsibility**: Each agent/tool does one thing well
- **Type Safety**: Use Pydantic for all data structures
- **Async First**: All I/O should be asynchronous
- **Cache Everything**: Save intermediate results to enable resumability
- **Fail Gracefully**: Use retries and logging to handle errors

### When Working on ViMax

1. **Understand the Pipeline**: Know which pipeline you're modifying
2. **Follow Patterns**: Use existing agents/tools as templates
3. **Test Incrementally**: Test each component before integration
4. **Cache Results**: Always save intermediate data to disk
5. **Log Progress**: Print user-facing progress messages
6. **Handle Errors**: Use `@retry` decorator for robustness

### Quick Reference Commands

```bash
# Install dependencies
uv sync

# Run idea-to-video
python main_idea2video.py

# Run script-to-video
python main_script2video.py

# Check working directory
ls -la .working_dir/script2video/

# View cached data
cat .working_dir/script2video/characters.json
```

---

**End of CLAUDE.md**

For questions or issues, refer to:
- Project README: `/home/user/ViMax/readme.md`
- GitHub Issues: https://github.com/HKUDS/ViMax/issues
- Communication channels: `/home/user/ViMax/Communication.md`
