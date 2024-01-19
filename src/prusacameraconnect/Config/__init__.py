from pathlib import Path
from strictyaml import load

from Types import Camera, GlobalConfig, SCHEMA


class Config:
    config = {}

    def __init__(self, config_location: Path | None = None):
        self._load_config(config_location)

    def _load_config(self, config_location: Path | None = None):
        """Loads the config from the config_location, or from the default location if not specified."""
        if config_location is None:
            config_location = Path("config.yaml")

        if not config_location.exists():
            raise FileNotFoundError(f"Config file not found at {config_location}")

        with config_location.open() as f:
            self.config = load(f.read(), SCHEMA).data

    @property
    def settings(self):
        """Returns the global config."""
        return GlobalConfig(**self.config["global_config"])

    @property
    def cameras(self):
        """Returns a list of cameras from the config."""
        return [Camera(**camera) for camera in self.config["cameras"]]
