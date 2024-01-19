import hashlib
import aiohttp
import structlog

from Types import PrinterState

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


class PrusaLinkAPI:
    def __init__(self, endpoint: str, username: str, password: str):
        self.endpoint = endpoint
        self.username = username
        self.password = password

    @property
    def _session(self):
        """Returns an aiohttp ClientSession."""
        return aiohttp.ClientSession(self.endpoint)

    # Digest auth implementation borrowed from homeassistant's pyprusalink project
    def _extract_digest_params(self, headers: dict[str]) -> None:
        """Extract realm, nonce key from Digest Auth header"""
        header_value = headers.get("WWW-Authenticate", "")
        if not header_value.startswith("Digest"):
            return

        header_value = header_value[len("Digest ") :]

        params = {}
        parts = header_value.split(",")
        for part in parts:
            key, value = part.strip().split("=", 1)
            params[key.strip()] = value.strip(' "')

        self._realm = params["realm"]
        self._nonce = params["nonce"]
        self._qop = params.get("qop", "auth")

    async def get_status(self, tigger_digest=False) -> dict:
        headers = {}
        if tigger_digest:
            ha1 = hashlib.md5(
                f"{self.username}:{self._realm}:{self.password}".encode()
            ).hexdigest()
            ha2 = hashlib.md5(f"GET:/api/v1/status".encode()).hexdigest()
            response_value = hashlib.md5(
                f"{ha1}:{self._nonce}:{ha2}".encode()
            ).hexdigest()
            headers = {
                "Authorization": f'Digest username="{self.username}", realm="{self._realm}", '
                f'nonce="{self._nonce}", uri="/api/v1/status", response="{response_value}"'
            }
        async with self._session as session:
            async with session.get("/api/v1/status", headers=headers) as resp:
                if resp.status == 401 and not tigger_digest:
                    self._extract_digest_params(resp.headers)
                    await log.adebug("Trying again with digest auth")
                    return await self.get_status(True)

                if resp.status != 200:
                    raise Exception(
                        f"Failed to get status: {resp.status} {resp.reason}"
                    )
                return await resp.json()

    async def get_printer_state(self) -> PrinterState:
        status = await self.get_status()
        return PrinterState(status["printer"]["state"])
