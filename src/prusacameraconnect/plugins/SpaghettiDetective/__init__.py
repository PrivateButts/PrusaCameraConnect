import asyncio
from PIL import Image, ImageDraw
from plugins import BasePluginHandler
import aiohttp
import structlog
from aiogram import Bot
import aiosmtplib
from email.message import EmailMessage

log = structlog.get_logger()


class DetectivePlugin(BasePluginHandler):
    def __init__(self, config: dict):
        self.snapshot_url = config.get("snapshot_url")
        self.ml_api_endpoint = config.get("ml_api_endpoint")
        self.api_key = config.get("api_key")
        self.draw_detections = config.get("draw_detections", True)
        self.action_threshold = int(config.get("action_threshold", 0))
        self.threshold_actions = config.get("threshold_actions", [])

        if self.snapshot_url is None:
            raise ValueError("Snapshot URL not set")
        if self.ml_api_endpoint is None:
            raise ValueError("ML API endpoint not set")

    @property
    def _session(self):
        """Returns an aiohttp ClientSession."""
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        return aiohttp.ClientSession(headers=headers)

    @property
    def _detective_url(self):
        return f"{self.ml_api_endpoint}?img={self.snapshot_url}"

    async def image_processing_hook(self, image: bytes) -> Image:
        await log.adebug("Sending image to Spaghetti Detective")
        async with self._session as session:
            async with session.get(self._detective_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to process image: {resp.status} {resp.reason}")
                data = await resp.json()
                await log.ainfo(
                    "Image processed by Spaghetti Detective",
                    detection_count=len(data["detections"]),
                )

        if self.draw_detections:
            # Draw the detections on the image
            overlay = ImageDraw.Draw(image)
            for detection in data["detections"]:
                x, y, w, h = detection[2]
                overlay.rectangle((x, y, x + w, y + h), outline="purple", width=4)
                overlay.rectangle((x, y, x + w, y + h), outline="red", width=2)
                overlay.text(
                    (x, y),
                    f"{detection[0]}\n{detection[1]}",
                    fill="white",
                    stroke_fill="black",
                    stroke_width=2,
                )

        if len(data["detections"]) > self.action_threshold:
            await log.awarn(
                "Detected spaghetti is greater than configured threshold",
                detection_count=len(data["detections"]),
            )
            asyncio.gather(
                *[self._dispatch(action) for action in self.threshold_actions if action is not None]
            )

        # Return the modified image as a PIL Image
        return image

    async def _dispatch(self, action: dict):
        """Dispatches an action based on the action type."""
        await log.adebug(f"Dispatching action: {action.get('type')}")
        match action.get("type"):
            case "webhook":
                await self._dispatch_webhook(action)
            case "email":
                await self._dispatch_email(action)
            case "telegram":
                await self._dispatch_telegram(action)

    async def _dispatch_webhook(self, action: dict):
        """Dispatches a webhook with the provided payload."""
        async with aiohttp.ClientSession() as session:
            await session.post(action["url"], json=action["payload"])
            log.ainfo("Webhook dispatched", url=action["url"])

    async def _dispatch_email(self, action: dict):
        """Dispatches an email alert."""
        message = EmailMessage()
        message["From"] = action["from"]
        message["To"] = action["to"]
        message["Subject"] = action["subject"]
        message.set_content(action["body"])
        _result, msg = await aiosmtplib.send(
            message,
            hostname=action["hostname"],
            port=action["port"],
            username=action["username"],
            password=action["password"],
            use_tls=bool(action["use_tls"]),
        )

        await log.ainfo("Email dispatched", msg=msg)

    async def _dispatch_telegram(self, action: dict):
        """Dispatches a Telegram alert."""
        bot = Bot(token=action["token"])
        await bot.send_message(action["chat_id"], action["message"])
