from PIL import Image
import io
import aiohttp
import structlog

from Types import Camera

from . import BaseCameraHandler

log = structlog.get_logger()


class ImageUrlHandler(BaseCameraHandler):
    """This handler is used to fetch an image from a URL, which some IP cameras provide."""

    def __init__(self, camera: Camera, options: dict):
        super().__init__(camera)
        self.url = options["url"]

    @property
    def _session(self):
        """Returns an aiohttp ClientSession."""
        return aiohttp.ClientSession()

    async def fetch(self) -> Image:
        """Fetches an image from self.url. Returns a PIL Image."""
        async with self._session as session:
            async with session.get(self.url) as resp:
                if resp.status != 200:
                    raise Exception(
                        f"Failed to fetch image: {resp.status} {resp.reason}"
                    )
                await log.adebug(f"Fetched image", url=self.url, status=resp.status)
                return Image.open(io.BytesIO(await resp.read()))
