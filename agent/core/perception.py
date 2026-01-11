import base64
import io
from typing import List, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import Page, Locator
from .types import InteractiveElement, BoundingBox

async def capture_interactive_elements(page: Page) -> List[InteractiveElement]:
    """
    Scans the page for interactive elements and visible text.
    """
    # 1. Capture Interactive Elements (Existing Logic)
    selector = 'button, a, input, select, textarea, [role="button"], [role="link"]'
    locators = page.locator(selector)
    count = await locators.count()
    
    elements = []
    
    for i in range(count):
        loc = locators.nth(i)
        if not await loc.is_visible(): continue
        bbox = await loc.bounding_box()
        if not bbox: continue
        if bbox['width'] < 5 or bbox['height'] < 5: continue

        tag_name = await loc.evaluate("el => el.tagName.toLowerCase()")
        text_content = await loc.text_content() or ""
        
        # Get extra attributes like placeholder, title, aria-label
        attributes = await loc.evaluate("""el => {
            return {
                placeholder: el.placeholder || '',
                title: el.title || '',
                aria_label: el.getAttribute('aria-label') || '',
                id: el.id || '',
                name: el.name || ''
            }
        }""")
        
        elements.append(InteractiveElement(
            id=len(elements) + 1,
            tag_name=tag_name,
            bbox=BoundingBox(int(bbox['x']), int(bbox['y']), int(bbox['width']), int(bbox['height'])),
            attributes={k: v for k, v in attributes.items() if v},
            text_content=text_content.strip()[:100]
        ))
    
    # 2. OCR-like Text Extraction (Alternative Perception)
    # This helps the VLM 'read' the page precisely even if the screenshot is grainy.
    # We can inject this into the prompt.
    
    return elements

async def get_page_text_map(page: Page) -> str:
    """
    Extracts all meaningful visible text on the page with approximate positions.
    """
    text_map = await page.evaluate("""() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let nodes = [];
        let node;
        while(node = walker.nextNode()) {
            const parent = node.parentElement;
            if (parent && parent.offsetWidth > 0 && parent.offsetHeight > 0) {
                const rect = parent.getBoundingClientRect();
                const text = node.textContent.trim();
                if (text.length > 2) {
                    nodes.append(`${text} [at ${Math.round(rect.x)},${Math.round(rect.y)}]`);
                }
            }
        }
        return nodes.slice(0, 50).join('\\n'); // Limit to first 50 chunks
    }""")
    return text_map

async def annotate_screenshot(page: Page, elements: List[InteractiveElement]) -> bytes:
    """
    Takes a screenshot and overlays the Set-of-Mark (SoM) bounding boxes and IDs.
    Returns the annotated image as bytes (PNG).
    """
    screenshot_bytes = await page.screenshot()
    
    image = Image.open(io.BytesIO(screenshot_bytes))
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fallback to default if not available
    try:
        # Linux path often has DejaVuSans or similar. 
        # For robustness, we might want to ship a font or use default.
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    for el in elements:
        box = el.bbox
        
        # Draw box
        # Color: Red for contrast, or maybe different colors for different types
        color = "red"
        draw.rectangle(
            [(box.x, box.y), (box.x + box.width, box.y + box.height)],
            outline=color,
            width=2
        )
        
        # Draw Label (ID)
        # Position label at top-left corner of the box, with a background
        label_text = str(el.id)
        
        # Get text size to draw background
        # verify textbbox availability (Pillow >= 9.2.0)
        if hasattr(draw, "textbbox"):
            left, top, right, bottom = draw.textbbox((0, 0), label_text, font=font)
            text_w = right - left
            text_h = bottom - top
        else:
            # Fallback for older Pillow
            text_w, text_h = draw.textsize(label_text, font=font)
            
        label_x = box.x
        label_y = box.y - text_h - 4 # slightly above
        
        # Ensure label is within bounds
        if label_y < 0:
            label_y = box.y + box.height + 2
            
        # Draw label background
        draw.rectangle(
            [(label_x, label_y), (label_x + text_w + 4, label_y + text_h + 4)],
            fill=color,
            outline=color
        )
        
        # Draw label text
        draw.text((label_x + 2, label_y + 2), label_text, fill="white", font=font)
        
    # Save back to bytes
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
