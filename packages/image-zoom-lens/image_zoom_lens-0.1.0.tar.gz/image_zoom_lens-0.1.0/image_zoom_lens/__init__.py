"""
Image Zoom Lens Component for Streamlit

A custom Streamlit component that displays an image with an interactive zoom lens.
Features:
- Configurable zoom level (mouse wheel or slider)
- Configurable lens size
- Mouse tracking for lens movement
- Right-click to download image with zoomed lens overlay
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import streamlit.components.v1 as components

if TYPE_CHECKING:
    import numpy as np
    from PIL import Image

# Get the directory of this file (use absolute path)
_COMPONENT_DIR = Path(__file__).resolve().parent


def _convert_image_to_data_url(image) -> str:
    """
    Convert PIL Image or numpy array to base64 data URL.

    Parameters
    ----------
    image : PIL.Image.Image or np.ndarray
        The image to convert

    Returns
    -------
    str
        Base64 encoded data URL
    """
    try:
        # Try importing PIL
        from PIL import Image

        # If it's already a PIL Image
        if isinstance(image, Image.Image):
            buffered = BytesIO()
            # Convert RGBA to RGB if necessary
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
    except ImportError:
        pass

    # Try numpy array
    try:
        import numpy as np
        from PIL import Image

        if isinstance(image, np.ndarray):
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image.astype("uint8"))
            buffered = BytesIO()
            if pil_image.mode == "RGBA":
                pil_image = pil_image.convert("RGB")
            pil_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
    except (ImportError, AttributeError):
        pass

    raise TypeError("Image must be a PIL Image, numpy array, or string URL")


def image_zoom_lens(
    image: Union[str, "Image.Image", "np.ndarray"],
    lens_size: int = 150,
    zoom_level: float = 2.0,
    download_format: str = "jpg",
    lens_shape: str = "circle",
    key: Optional[str] = None,
) -> None:
    """
    Display an image with an interactive zoom lens.

    Parameters
    ----------
    image : str, PIL.Image.Image, or np.ndarray
        Image to display. Can be:
        - String: URL, file path, or data URL
        - PIL Image: PIL.Image.Image object
        - Numpy array: uint8 array with shape (H, W, 3) or (H, W, 4)
    lens_size : int, optional
        Size of the zoom lens in pixels (default: 150).
        Range: 50-500 pixels.
    zoom_level : float, optional
        Initial zoom magnification level (default: 2.0).
        Range: 1.0-20.0x.
    download_format : str, optional
        Format for downloaded images: 'jpg' or 'png' (default: 'jpg').
        JPG provides smaller file sizes, PNG preserves transparency.
    lens_shape : str, optional
        Shape of the zoom lens: 'circle' or 'square' (default: 'circle').
    key : str, optional
        An optional string to use as the unique key for the component.
        If this is None, and the component's arguments are changed, the
        component will be re-mounted in the Streamlit app.

    Usage
    -----
    - Move your mouse over the image to see the zoom lens
    - Use the mouse wheel to adjust zoom level dynamically
    - Use the sliders to adjust lens size and zoom level
    - Right-click on the image to download it with the zoomed lens overlay

    Example
    -------
    >>> import streamlit as st
    >>> from image_zoom_lens import image_zoom_lens
    >>> from PIL import Image
    >>> import numpy as np
    >>>
    >>> # Example 1: Using URL
    >>> image_zoom_lens(
    ...     image="https://example.com/image.jpg",
    ...     lens_size=200,
    ...     zoom_level=3.0
    ... )
    >>>
    >>> # Example 2: Using PIL Image
    >>> pil_image = Image.open("local_image.jpg")
    >>> image_zoom_lens(image=pil_image, lens_size=150)
    >>>
    >>> # Example 3: Using numpy array
    >>> np_image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
    >>> image_zoom_lens(image=np_image, zoom_level=2.5)
    """

    # Convert image to URL if needed
    if isinstance(image, str):
        image_url = image
    else:
        # Convert PIL or numpy to data URL
        image_url = _convert_image_to_data_url(image)

    # Validate parameters
    lens_size = max(50, min(500, lens_size))
    zoom_level = max(1.0, min(20.0, zoom_level))
    download_format = download_format.lower()
    if download_format not in ["jpg", "jpeg", "png"]:
        download_format = "jpg"
    # Normalize jpeg to jpg
    if download_format == "jpeg":
        download_format = "jpg"

    lens_shape = lens_shape.lower()
    if lens_shape not in ["circle", "square"]:
        lens_shape = "circle"

    # Load the HTML file
    html_path = _COMPONENT_DIR / "frontend" / "index.html"
    with open(html_path) as f:
        html_template = f.read()

    # Inject parameters by replacing the script initialization
    html_content = (
        html_template.replace("let imageUrl = '';", f"let imageUrl = '{image_url}';")
        .replace("let currentZoomLevel = 2;", f"let currentZoomLevel = {zoom_level};")
        .replace("let lensSize = 150;", f"let lensSize = {lens_size};")
        .replace("let downloadFormat = 'jpg';", f"let downloadFormat = '{download_format}';")
        .replace("let lensShape = 'circle';", f"let lensShape = '{lens_shape}';")
        .replace("mainImage.src = imageUrl;", f'mainImage.src = "{image_url}";')
        .replace("zoomLensImage.src = imageUrl;", f'zoomLensImage.src = "{image_url}";')
    )

    # Render using components.html
    components.html(html_content, height=700, scrolling=True)

    return None


# Make the component available at package level
__all__ = ["image_zoom_lens"]
