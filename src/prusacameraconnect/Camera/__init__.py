import io
import structlog
from PIL import Image

from Types import Camera

log = structlog.get_logger()


class BaseCameraHandler:
    camera: Camera

    def __init__(self, camera: Camera):
        self.camera = camera

    async def fetch(self) -> Image:
        """Base method for fetching an image from the camera. Returns a PIL Image."""
        raise NotImplementedError()

    async def get_snapshot(self) -> bytes:
        """Base method for getting a snapshot from the camera. Returns a binary string of a JPEG image."""
        image = await self.fetch()
        stringBuffer = io.BytesIO()
        image.save(stringBuffer, format="JPEG")
        await log.adebug(f"Converted to snapshot")
        return stringBuffer.getvalue()
