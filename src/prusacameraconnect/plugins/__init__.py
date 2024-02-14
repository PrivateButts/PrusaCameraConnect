from PIL import Image

class BasePluginHandler:
    def image_processing_hook(self, image: Image) -> Image:
        """Hook for additional image processing, should return the processed image."""
        return image