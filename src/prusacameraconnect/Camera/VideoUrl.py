import cv2
import structlog
from PIL import Image

from Types import Camera

from . import BaseCameraHandler

log = structlog.get_logger()


class VideoCaptureHandler(BaseCameraHandler):
    def __init__(self, camera: Camera, options: dict):
        """Opens a video stream from a url"""
        super().__init__(camera)
        self.url = options["url"]
        self.source = cv2.VideoCapture(self.url)

    async def fetch(self) -> Image:
        """Fetches an image from the video stream"""
        ret, frame = self.source.read()

        if not ret:
            raise Exception(f"Failed to fetch image")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return Image.fromarray(frame)
