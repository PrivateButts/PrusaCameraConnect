import threading
import time
import cv2
import structlog
from PIL import Image

from Types import Camera

from . import BaseCameraHandler, SourceOfflineException

log = structlog.get_logger()


class VideoCaptureHandler(BaseCameraHandler):
    def __init__(self, camera: Camera, options: dict):
        """Opens a video stream from a url"""
        super().__init__(camera)
        self.url = options["url"]
        self.source = cv2.VideoCapture(self.url)
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        """Reads frames from the video stream,"""
        while True:
            with self.lock:
                ret = self.source.grab()
            if not ret:
                # Unable to connect, so we'll just wait a bit and try again
                log.error("Unable to connect to video stream, retrying in 5 seconds")
                time.sleep(5)
                self.source = cv2.VideoCapture(self.url)
                if self.source.isOpened():
                    log.info("Reconnected to video stream")

    def read(self):
        """Decodes the latest frame from the video stream"""
        with self.lock:
            _, frame = self.source.retrieve()
        return frame

    async def get_snapshot(self) -> Image:
        """Fetches an image from the video stream"""
        if not self.source.isOpened():
            log.warn("Source offline, unable to fetch image")
            raise SourceOfflineException()
        frame = self.read()

        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error:
            log.error(
                "Unable to convert image to RGB, sometimes this happens when a source is about to go offline"
            )
            raise SourceOfflineException()

        return Image.fromarray(frame)
