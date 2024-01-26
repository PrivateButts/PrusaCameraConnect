from pathlib import Path
from strictyaml import load
import os

from Types import Camera, GlobalConfig, SCHEMA


class Config:
    config = {}

    def __init__(self, config_location: Path | None = None):
        self._load_config(config_location)

    def _load_config_file(self, config_location: Path | None = None):
        if config_location is None:
            config_location = Path("config.yaml")

        if not config_location.exists():
            raise FileNotFoundError(f"Config file not found at {config_location.absolute()}")

        with config_location.open() as f:
            return f.read()

    def _load_config(self, config_location: Path | None = None):
        """Loads the config from the config_location, or from the default location if not specified."""
        config_data = (
            os.getenv("APP_CONFIG")
            if os.getenv("APP_CONFIG")
            else self._load_config_file(config_location)
        )

        self.config = load(config_data, SCHEMA).data

    @property
    def settings(self):
        """Returns the global config."""
        return GlobalConfig(**self.config["global_config"])

    @property
    def cameras(self):
        """Returns a list of cameras from the config."""
        return [Camera(**camera) for camera in self.config["cameras"]]
