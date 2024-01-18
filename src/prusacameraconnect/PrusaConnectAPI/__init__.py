import aiohttp
import structlog

log = structlog.get_logger()


class PrusaConnectAPI:
    def __init__(self, endpoint: str = "https://connect.prusa3d.com"):
        self.endpoint = endpoint

    @property
    def _session(self):
        """Returns an aiohttp ClientSession."""
        return aiohttp.ClientSession(self.endpoint)

    async def upload_snapshot(
        self, token: str, fingerprint: str, snapshot: str
    ) -> None:
        """Uploads a snapshot to Prusa Connect, uses token and fingerprint to authenticate, snapshot should be a binary string of a JPEG image."""
        async with self._session as session:
            async with session.put(
                "/c/snapshot",
                headers={"Token": token, "Fingerprint": fingerprint},
                data=snapshot,
            ) as resp:
                if resp.status != 204:
                    raise Exception(
                        f"Failed to upload snapshot: {resp.status} {resp.reason}"
                    )
                await log.adebug(f"Uploaded snapshot", fingerprint=fingerprint)
