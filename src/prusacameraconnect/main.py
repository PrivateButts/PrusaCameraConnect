import asyncio
import structlog
from PrusaConnectAPI import PrusaConnectAPI
from Config import Config, Camera

log = structlog.get_logger()
config = Config()
api = PrusaConnectAPI()


async def camera_loop(camera: Camera):
    while True:
        await log.ainfo(f"Updating {camera.name}")
        try:
            image = await camera.handle.get_snapshot()
            await api.upload_snapshot(camera.token, camera.fingerprint, image)
        except KeyboardInterrupt:
            return
        except Exception as e:
            await log.aexception(f"Failed to upload snapshot for {camera.name}")
        await asyncio.sleep(camera.interval)


async def main():
    await log.ainfo("Starting Prusa Camera Connect")
    tasks = []
    for camera in config.cameras:
        tasks.append(asyncio.create_task(camera_loop(camera)))

    await asyncio.gather(*tasks)
    await log.ainfo("Stopping Prusa Camera Connect")


if __name__ == "__main__":
    asyncio.run(main())
