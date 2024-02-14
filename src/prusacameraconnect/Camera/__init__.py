import structlog
from PIL import Image

from Types import Camera

log = structlog.get_logger()


class SourceOfflineException(Exception):
    pass


class BaseCameraHandler:
    camera: Camera

    def __init__(self, camera: Camera):
        self.camera = camera

    async def get_snapshot(self) -> Image:
        """Base method for fetching an image from the camera. Returns a PIL Image."""
        raise NotImplementedError()
