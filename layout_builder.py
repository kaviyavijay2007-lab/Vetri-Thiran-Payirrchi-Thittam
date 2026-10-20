from typing import List
from app.schemas import ComicLayout, PanelStory

def build_comic_layout(stories: List[PanelStory], image_urls: List[str]) -> List[ComicLayout]:
    if len(stories) != len(image_urls):
        raise ValueError("Number of stories and images must match.")
    return [
        ComicLayout(
            panel_number=story.panel_number,
            title=story.title,
            image_url=image_url,
            scene_description=story.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=story.image_prompt,
        )
        for story, image_url in zip(stories, image_urls)
    ]
