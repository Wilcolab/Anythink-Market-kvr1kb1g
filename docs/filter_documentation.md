# Image Filter Documentation

## API Documentation

### Filter Application Endpoint

**Endpoint:** `/api/apply-filter`  
**Method:** POST  
**Content-Type:** multipart/form-data

#### Parameters

| Parameter | Type | Description | Default | Range |
|-----------|------|-------------|---------|--------|
| image_id | string | Unique identifier of the uploaded image | Required | - |
| selected_filter | string | Name of the filter to apply | Required | See available filters below |
| warmth | float | Color temperature adjustment (vintage film filter only) | 1.0 | 0.6 - 1.4 |
| grain | float | Film grain intensity (vintage film filter only) | 1.0 | 0.0 - 3.0 |
| vignette | float | Vignette strength (vintage film filter only) | 1.0 | 0.0 - 3.0 |
| contrast | float | Contrast adjustment (vintage film filter only) | 1.0 | 0.6 - 1.4 |

#### Available Filters

| Filter Name | Description | Parameters |
|-------------|-------------|------------|
| none | No filter applied | None |
| grayscale | Converts image to black and white | None |
| blur | Applies Gaussian blur effect | None |
| contour | Detects and enhances edges | None |
| detail | Enhances image details | None |
| edge_enhance | Sharpens edges | None |
| emboss | Creates embossed effect | None |
| sharpen | Increases image sharpness | None |
| smooth | Reduces noise and smooths the image | None |
| brightness | Increases image brightness by 50% | None |
| contrast | Increases image contrast by 50% | None |
| invert | Inverts the colors of the image | None |
| sepia | Applies a warm sepia tone effect | None |
| vintage_film | Applies a classic film camera look | warmth, grain, vignette, contrast |

#### Response

**Success Response (200 OK)**
```json
{
    "image_data": "base64_encoded_image_string"
}
```

**Error Response (404 Not Found)**
```json
{
    "error": "Image not found"
}
```

#### Error Handling

- Returns 404 if the specified image_id is not found in the system
- Parameters for vintage_film filter are automatically clamped to their valid ranges
- Invalid filter names will result in no filter being applied
- All image processing errors are caught and returned as error responses

## User Guide

### Applying Filters

1. **Upload an Image**
   - Click the upload button or drag and drop an image file
   - Supported formats: JPEG, PNG, GIF
   - Maximum image size: 1200x1200 pixels (larger images will be automatically resized)

2. **Select a Filter**
   - Choose from the available filters displayed in the filter grid
   - Each filter has a name and description
   - Click on a filter to apply it
   - The filtered image will appear in the preview panel

3. **Vintage Film Filter Controls**
   When the Vintage Film filter is selected, additional controls appear:
   
   - **Color Warmth (0.6 - 1.4)**
     - Adjusts the color temperature
     - Values > 1.0 make the image warmer (more red/yellow)
     - Values < 1.0 make the image cooler (more blue)
   
   - **Film Grain (0.0 - 3.0)**
     - Controls the intensity of the film grain effect
     - Higher values create more pronounced grain
     - 0.0 removes grain completely
   
   - **Vignette Strength (0.0 - 3.0)**
     - Controls the darkness of the corners
     - Higher values create stronger vignette effect
     - 0.0 removes vignette completely
   
   - **Contrast (0.6 - 1.4)**
     - Adjusts the image contrast
     - Values > 1.0 increase contrast
     - Values < 1.0 decrease contrast

4. **Download**
   - Click the "Download" button to save the filtered image
   - The image will be saved in JPEG format with 85% quality

### Tips for Best Results

- For portrait photos, try the Vintage Film filter with:
  - Warmth: 1.1 - 1.2
  - Grain: 0.8 - 1.2
  - Vignette: 1.0 - 1.5
  - Contrast: 1.0 - 1.1

- For landscape photos, try the Vintage Film filter with:
  - Warmth: 1.0 - 1.1
  - Grain: 0.5 - 1.0
  - Vignette: 1.5 - 2.0
  - Contrast: 0.9 - 1.0

- Use the Sharpen filter for slightly blurry images
- Use the Smooth filter to reduce noise in high ISO photos
- Combine filters by applying them in sequence

## Code Documentation

### VintageFilmFilter Class

The `VintageFilmFilter` class implements a custom filter that simulates the look of vintage film photography. It combines multiple effects to create an authentic film look.

```python
class VintageFilmFilter(BuiltinFilter):
    """
    A custom filter that simulates the look of vintage film photography.
    Combines color temperature adjustment, film grain, vignette, and contrast effects.
    
    Parameters:
        warmth (float): Color temperature adjustment (0.6-1.4)
        grain (float): Film grain intensity (0.0-3.0)
        vignette (float): Vignette strength (0.0-3.0)
        contrast (float): Contrast adjustment (0.6-1.4)
    """
```

#### Filter Processing Steps

1. **Color Temperature Adjustment**
   ```python
   # Step 1: Apply warm color temperature
   # - Increases red channel (1.2x warmth)
   # - Slightly increases green channel (1.1x warmth)
   # - Decreases blue channel (0.8x / warmth)
   ```

2. **Film Grain Addition**
   ```python
   # Step 2: Add film grain
   # - Generates random noise (-30 to +30)
   # - Scales noise by grain parameter
   # - Applies to all color channels
   ```

3. **Vignette Effect**
   ```python
   # Step 3: Apply vignette
   # - Calculates distance from image center
   # - Creates radial darkening effect
   # - Strength controlled by vignette parameter
   ```

4. **Contrast and Focus**
   ```python
   # Step 4: Adjust contrast
   # - Applies contrast enhancement
   # - Adds subtle blur based on contrast value
   # - Creates soft focus effect
   ```

### API Implementation

The filter application endpoint (`/api/apply-filter`) handles all filter operations:

```python
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
    
    Parameters are validated and clamped to safe ranges:
    - warmth: 0.6 to 1.4
    - grain: 0.0 to 3.0
    - vignette: 0.0 to 3.0
    - contrast: 0.6 to 1.4
    
    Returns:
        JSON response with base64-encoded filtered image
    """
```

### Frontend Implementation

The filter UI is implemented in `filter.html` with the following key components:

1. **Filter Selection Grid**
   - Displays available filters in a responsive grid
   - Each filter has a name and description
   - Active filter is highlighted

2. **Vintage Film Controls**
   - Sliders for each parameter
   - Real-time preview updates
   - Reset buttons for each parameter
   - Debounced updates to prevent excessive API calls

3. **Image Preview**
   - Side-by-side comparison of original and filtered images
   - Responsive layout
   - Download button for filtered image

4. **Error Handling**
   - Loading indicators during processing
   - Error messages for failed operations
   - Graceful fallback for unsupported filters 