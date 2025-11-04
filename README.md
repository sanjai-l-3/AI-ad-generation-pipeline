## AI Ad Production Pipeline

End-to-end system to generate ad scripts, characters, locations, outfits, scene images, and stitched videos — available as both a Python pipeline and an interactive Streamlit app.

### Features
- **Stage-wise pipeline**: Script → Characters → Locations → Outfits → Character-Outfit mapping → Scene descriptions → Scene images → Videos
- **Idempotent**: Skips completed stages automatically; supports selective regeneration
- **Project-oriented storage** under `projects_data/<project_id>/...`

### Project Structure (key paths)
- `pipeline.py`: Programmatic pipeline runner (CLI/Script)
- `app.py`: Streamlit multi-stage UI
- `services/*`: Stage-specific generators (scripts, images, videos, etc.)
- `streamlit_components/*`: Streamlit stage UIs and utilities
- `projects_data/<project_id>/`
  - `character_images/`, `location_images/`, `outfit_images/`, `character_outfit_images/`
  - `scene_images/`, `generated_videos/`, `final_videos/` (if used)
  - `scripts/` (JSON stage artifacts, reports), `prompts/` (prompts, descriptions)

---
## API Key Setup

To enable AI-powered generation, you’ll need API keys for external providers:

- **Gemini (Google) API:**  
  Set the `GEMINI_API_KEY` environment variable.

- **OpenAI API:**  
  Set the `OPENAI_API_KEY` environment variable.

### How to Add API Keys

1. **Local development:**  
   Create a `.env` file at the project root (or use your shell environment):

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Alternatively, export them in your shell before running:**

   ```bash
   export GEMINI_API_KEY=your_gemini_api_key_here
   export OPENAI_API_KEY=your_openai_api_key_here
   ```


### Dependencies
Install via a virtual environment. If you have a `requirements.txt`, use it. If not, start with the core libs and add missing ones as errors indicate.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate or  conda env

# If requirements.txt exists
pip install -r requirements.txt

```



---

## Running the Full Pipeline (Python)
`pipeline.py` exposes a class `CompleteAdProductionPipeline` that orchestrates every stage and automatically skips stages that are already completed for the same `project_id`.

### Minimal example
Edit `pipeline.py` or create a small script to call the pipeline with your own `ad_concept`, `brand_info`, and optional `product_image_path`.

```python
from pipeline import CompleteAdProductionPipeline

ad_concept = {
    "title": "Your Ad Title",
    "one_line_summary": "One-liner",
    "story": "High-level story",
    "visual_flow": {"Opening": "..."},
    "voice_over": "...",
    "tagline": "...",
    "key_message": "...",
    "key_features": ["..."]
}

brand_info = {
    "brand_name": "Your Brand",
    "product_name": "Your Product",
    "product_description": "...",
    "key_features": ["..."]
}

pipeline = CompleteAdProductionPipeline(project_id="my_project_001")
results = pipeline.run_complete_pipeline(
    ad_concept=ad_concept,
    brand_info=brand_info,
    product_image_path="/absolute/path/to/product_image.png",  # optional
    target_duration="45 seconds",
    aspect_ratio="16:9",
    generate_character_images=True,
    generate_location_images=True,
    generate_outfit_images=True,
    character_outfit_images=True,
    generate_scene_images=True,
    generate_videos=True,
    force_regenerate=False
)
```

### Run directly
`pipeline.py` includes a runnable example in `if __name__ == "__main__":`. Adjust the example `project_id` and `product_image_path` in-place, then run:

```bash
python pipeline.py
```

### Useful methods
- `get_pipeline_status()` — prints completed vs pending stages for the `project_id`
- `reset_stage(stage_name)` — delete outputs for a specific stage (e.g., `"scene_descriptions"`, `"characters"`, `"video_generation_report"`)
- `reset_all_stages()` — delete outputs for all stages of the project

### Outputs
Artifacts are written to `projects_data/<project_id>/`:
- `scripts/` — JSONs for characters, locations, outfits, mapping, generation reports, etc.
- `prompts/` — scene and video description prompts
- `scene_images/` — generated scene images
- `generated_videos/` — generated per-shot videos and report

---

## Running the Streamlit App
The Streamlit app provides a guided, stage-wise UI with the same pipeline under the hood.

### Start the app
From the project root (`ads_poc/`):

```bash
streamlit run app.py
```

### Workflow in the UI
1. **Select/Create Project** — Choose a `project_id` and project path
2. **Brand Info & Ad Concept** — Enter brand details; generate and select an ad concept
3. **Script Generation** — Produce the shot script
4. **Characters & Locations** — Generate characters and locations with images
5. **Outfits** — Generate outfit images and character–outfit mapping
6. **Scene Generation** — Generate scene descriptions and images
7. **Video Generation** — Generate per-shot videos and a video report

The sidebar displays stage status, and the app will block navigation if prerequisites are missing (e.g., cannot proceed to Outfits before Characters & Locations).

### Where the app writes files
The app reads/writes under `projects_data/<project_id>/` using the same file conventions as the Python pipeline (e.g., `scripts/<project_id>_characters.json`, `prompts/<project_id>_scene_descriptions.json`, etc.).

---

## Tips & Troubleshooting
- **Absolute paths**: When providing `product_image_path`, use absolute paths to avoid resolution issues.
- **Regeneration**: Use `force_regenerate=True` in the Python pipeline or delete specific artifacts via `reset_stage` to re-run a stage.
- **Missing packages**: If you see `ModuleNotFoundError`, install the package into your active venv (e.g., `pip install streamlit`).
- **Permissions**: Ensure you have write access to `projects_data/`.
- **Long runs**: Image/video generation can take time; prefer smaller test projects first.

---

## Quick Commands
```bash
# Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present

# Run CLI pipeline (edit pipeline.py example or import as shown above)
python pipeline.py

# Launch Streamlit UI
streamlit run app.py
```

---

