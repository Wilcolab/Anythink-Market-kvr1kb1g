from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageFilter, ImageEnhance
import io
import os
import base64
from pathlib import Path
import uuid
import uvicorn
import random
from PIL.ImageFilter import BuiltinFilter

# Get the base directory using the current file's location
BASE_DIR = Path(__file__).resolve().parent

# In-memory image storage using a dictionary
# Keys are unique IDs, values are base64 encoded image data
IMAGE_STORE = {}

app = FastAPI(title="Image Filter App")

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

class VintageFilmFilter(BuiltinFilter):
    """
    A custom filter that simulates the look of vintage film photography.
    Combines multiple effects to create an authentic film look:
    - Color temperature adjustment for warm/cool tones
    - Film grain simulation
    - Vignette effect for darkened corners
    - Contrast adjustment with soft focus
    
    Parameters:
        warmth (float): Color temperature adjustment (0.6-1.4)
            - Values > 1.0 create warmer tones (more red/yellow)
            - Values < 1.0 create cooler tones (more blue)
        grain (float): Film grain intensity (0.0-3.0)
            - Higher values create more pronounced grain
            - 0.0 removes grain completely
        vignette (float): Vignette strength (0.0-3.0)
            - Higher values create stronger corner darkening
            - 0.0 removes vignette completely
        contrast (float): Contrast adjustment (0.6-1.4)
            - Values > 1.0 increase contrast
            - Values < 1.0 decrease contrast
            - Also affects soft focus intensity
    """
    name = "Vintage Film"
    filterargs = (3, 3)  # Kernel size for filter

    def __init__(self, warmth=1.0, grain=1.0, vignette=1.0, contrast=1.0):
        # Clamp parameters to safe ranges to prevent extreme effects
        self.warmth = max(0.6, min(1.4, float(warmth)))    # Color temperature (0.6-1.4)
        self.grain = max(0.0, min(3.0, float(grain)))      # Film grain intensity (0.0-3.0)
        self.vignette = max(0.0, min(3.0, float(vignette))) # Vignette strength (0.0-3.0)
        self.contrast = max(0.6, min(1.4, float(contrast))) # Contrast adjustment (0.6-1.4)

    def filter(self, image):
        """
        Applies the vintage film effect to the input image.
        
        Processing steps:
        1. Color temperature adjustment
        2. Film grain addition
        3. Vignette effect
        4. Contrast and soft focus
        
        Args:
            image (PIL.Image): Input image to process
            
        Returns:
            PIL.Image: Processed image with vintage film effect
        """
        # Convert to RGB if not already
        rgb_img = image.convert('RGB')
        width, height = rgb_img.size
        
        # Create a new image for the result
        result_img = Image.new('RGB', (width, height))
        result_pixels = result_img.load()
        source_pixels = rgb_img.load()
        
        # Step 1: Apply warm color temperature with enhanced effect
        # This creates the characteristic warm tones of vintage film
        for y in range(height):
            for x in range(width):
                r, g, b = source_pixels[x, y]
                # Enhanced warmth effect
                r = min(255, int(r * (1.2 * self.warmth)))  # Stronger red boost
                g = min(255, int(g * (1.1 * self.warmth)))  # Moderate green boost
                b = min(255, int(b * (0.8 / self.warmth)))  # Stronger blue reduction
                result_pixels[x, y] = (r, g, b)
        
        # Step 2: Add film grain with enhanced intensity
        # This simulates the random noise present in film photography
        for y in range(height):
            for x in range(width):
                r, g, b = result_pixels[x, y]
                # Enhanced grain effect
                noise = random.randint(-30, 30) * self.grain  # Increased noise range
                r = max(0, min(255, r + noise))
                g = max(0, min(255, g + noise))
                b = max(0, min(255, b + noise))
                result_pixels[x, y] = (r, g, b)
        
        # Step 3: Apply vignette effect with enhanced strength
        # This creates the characteristic darkening of corners in film photos
        center_x, center_y = width / 2, height / 2
        max_distance = (center_x ** 2 + center_y ** 2) ** 0.5
        
        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                # Normalize distance
                distance = distance / max_distance
                
                # Enhanced vignette effect
                vignette = 1 - (distance * 0.7 * self.vignette)  # Increased vignette strength
                r, g, b = result_pixels[x, y]
                r = int(r * vignette)
                g = int(g * vignette)
                b = int(b * vignette)
                result_pixels[x, y] = (r, g, b)
        
        # Step 4: Adjust contrast with enhanced effect
        # This creates the characteristic contrast of film photos
        enhancer = ImageEnhance.Contrast(result_img)
        result_img = enhancer.enhance(0.8 * self.contrast)  # Increased contrast effect
        
        # Step 5: Add subtle soft focus effect
        # This simulates the slight softness often present in film photos
        blur_radius = 0.5 * (2 - self.contrast)  # More blur when contrast is lower
        result_img = result_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return result_img

# Available filters
FILTERS = {
    "grayscale": "Convert to grayscale",
    "blur": "Blur effect",
    "contour": "Contour effect",
    "detail": "Enhance details",
    "edge_enhance": "Edge enhancement",
    "emboss": "Emboss effect",
    "sharpen": "Sharpen image",
    "smooth": "Smooth image",
    "brightness": "Increase brightness",
    "contrast": "Increase contrast",
    "invert": "Invert colors",
    "sepia": "Sepia tone effect",
    "vintage_film": "Add film grain effect"
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "filters": FILTERS}
    )

@app.post("/upload")
async def upload_image(request: Request, image: UploadFile = File(...)):
    # Read the image into memory
    contents = await image.read()
    
    # Generate a unique ID for the image
    image_id = str(uuid.uuid4())
    
    # Convert to PIL Image for potential resizing/optimization
    img = Image.open(io.BytesIO(contents))
    
    # Convert to RGB if not already
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Optional: resize large images to reduce memory usage
    max_size = 1200
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size))
    
    # Save to memory buffer and convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Store in memory dictionary
    IMAGE_STORE[image_id] = img_base64
    
    return templates.TemplateResponse(
        "filter.html", 
        {
            "request": request, 
            "filters": FILTERS, 
            "image_id": image_id,
            "image_data": f"data:image/jpeg;base64,{img_base64}"
        }
    )

@app.get("/apply-filter")
async def get_filter_page(request: Request, image_id: str):
    # Get the image data from storage
    img_base64 = IMAGE_STORE.get(image_id)
    
    if not img_base64:
        return JSONResponse({"error": "Image not found"}, status_code=404)
    
    return templates.TemplateResponse(
        "filter.html", 
        {
            "request": request, 
            "filters": FILTERS, 
            "image_id": image_id,
            "image_data": f"data:image/jpeg;base64,{img_base64}"
        }
    )

@app.post("/api/apply-filter")
async def api_apply_filter(
    image_id: str = Form(...), 
    selected_filter: str = Form(...),
    warmth: float = Form(1.0),
    grain: float = Form(1.0),
    vignette: float = Form(1.0),
    contrast: float = Form(1.0)
):
    """
    Applies the selected filter to the specified image.
    
    This endpoint handles all filter operations, including:
    - Basic filters (grayscale, blur, etc.)
    - Advanced filters (vintage film with multiple parameters)
    - Parameter validation and clamping
    - Error handling
    
    Parameters:
        image_id (str): Unique identifier of the uploaded image
        selected_filter (str): Name of the filter to apply
        warmth (float): Color temperature for vintage film filter (0.6-1.4)
        grain (float): Film grain intensity for vintage film filter (0.0-3.0)
        vignette (float): Vignette strength for vintage film filter (0.0-3.0)
        contrast (float): Contrast adjustment for vintage film filter (0.6-1.4)
    
    Returns:
        JSONResponse: Contains base64-encoded filtered image or error message
        
    Raises:
        404: If the specified image_id is not found
    """
    print(f"Received filter request: {selected_filter}")
    print(f"Parameters: warmth={warmth}, grain={grain}, vignette={vignette}, contrast={contrast}")
    
    # Get the image data from storage
    img_base64 = IMAGE_STORE.get(image_id)
    
    if not img_base64:
        return JSONResponse({"error": "Image not found"}, status_code=404)
    
    # Convert base64 to PIL Image
    img_data = base64.b64decode(img_base64)
    img = Image.open(io.BytesIO(img_data))
    
    # Apply the selected filter
    if selected_filter == "vintage_film":
        # Clamp parameters to expanded safe ranges
        warmth = max(0.6, min(1.4, float(warmth)))
        grain = max(0.0, min(3.0, float(grain)))
        vignette = max(0.0, min(3.0, float(vignette)))
        contrast = max(0.6, min(1.4, float(contrast)))
        
        print(f"Applying vintage filter with clamped values: warmth={warmth}, grain={grain}, vignette={vignette}, contrast={contrast}")
        
        filtered_img = img.filter(VintageFilmFilter(
            warmth=warmth,
            grain=grain,
            vignette=vignette,
            contrast=contrast
        ))
    elif selected_filter == "grayscale":
        # Convert to grayscale and back to RGB for consistent output
        filtered_img = img.convert("L").convert("RGB")
    elif selected_filter == "blur":
        filtered_img = img.filter(ImageFilter.BLUR)
    elif selected_filter == "contour":
        filtered_img = img.filter(ImageFilter.CONTOUR)
    elif selected_filter == "detail":
        filtered_img = img.filter(ImageFilter.DETAIL)
    elif selected_filter == "edge_enhance":
        filtered_img = img.filter(ImageFilter.EDGE_ENHANCE)
    elif selected_filter == "emboss":
        filtered_img = img.filter(ImageFilter.EMBOSS)
    elif selected_filter == "sharpen":
        filtered_img = img.filter(ImageFilter.SHARPEN)
    elif selected_filter == "smooth":
        filtered_img = img.filter(ImageFilter.SMOOTH)
    elif selected_filter == "brightness":
        # Increase brightness by 50%
        enhancer = ImageEnhance.Brightness(img)
        filtered_img = enhancer.enhance(1.5)
    elif selected_filter == "contrast":
        # Increase contrast by 50%
        enhancer = ImageEnhance.Contrast(img)
        filtered_img = enhancer.enhance(1.5)
    elif selected_filter == "invert":
        # Invert colors
        rgb_img = img.convert('RGB')
        width, height = rgb_img.size
        pixels = rgb_img.load()
        
        for y in range(height):
            for x in range(width):
                r, g, b = rgb_img.getpixel((x, y))
                # Invert each color channel
                pixels[x, y] = (255 - r, 255 - g, 255 - b)
        
        filtered_img = rgb_img
    elif selected_filter == "sepia":
        # Convert to sepia tone using standard coefficients
        rgb_img = img.convert('RGB')
        width, height = rgb_img.size
        pixels = rgb_img.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = rgb_img.getpixel((px, py))
                # Standard sepia tone coefficients
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                # Ensure values don't exceed 255
                tr = min(255, tr)
                tg = min(255, tg)
                tb = min(255, tb)
                    
                pixels[px, py] = (tr, tg, tb)
        
        filtered_img = rgb_img
    else:
        # No filter or unknown filter - return original image
        filtered_img = img
    
    # Save to memory buffer instead of file
    buffered = io.BytesIO()
    filtered_img.save(buffered, format="JPEG", quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return JSONResponse({"image_data": f"data:image/jpeg;base64,{img_str}"})

@app.post("/download")
async def download_image(
    image_data: str = Form(...),
    filter_name: str = Form(...)
):
    # Remove prefix if present
    if "data:image/jpeg;base64," in image_data:
        image_data = image_data.replace("data:image/jpeg;base64,", "")
    
    # Decode base64 string
    try:
        image_bytes = base64.b64decode(image_data)
    except:
        return JSONResponse({"error": "Invalid image data"}, status_code=400)
    
    # Create filename
    filename = f"filtered_image_{filter_name}.jpg"
    
    # Return image data directly as a response
    return Response(
        content=image_bytes,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=31337, reload=True) 