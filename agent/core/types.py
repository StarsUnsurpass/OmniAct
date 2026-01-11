from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

@dataclass
class InteractiveElement:
    id: int
    tag_name: str
    bbox: BoundingBox
    attributes: dict
    text_content: str = ""
