from dataclasses import dataclass
import importlib
from pathlib import Path
from strictyaml import load, Map, Str, Float, Seq, Enum, Url, YAMLError, as_document

from Camera import BaseCameraHandler

SCHEMA = Map(
    {
        "global_config": Map(
            {
                "connect_endpoint": Url(),
            }
        ),
        "cameras": Seq(
            Map(
                {
                    "name": Str(),
                    "fingerprint": Str(),
                    "token": Str(),
                    "interval": Float(),
                    "handler": Enum(["ImageUrl.ImageUrlHandler"]),
                    "handler_config": Map(
                        {
                            "url": Url(),
                        }
                    ),
                }
            )
        ),
    }
)


@dataclass
class GlobalConfig:
    connect_endpoint: str


@dataclass
class Camera:
    name: str
    fingerprint: str
    token: str
    interval: float
    handler: str
    handler_config: dict

    def __post_init__(self):
        module_name, class_name = self.handler.split(".")
        module = importlib.import_module(f"Camera.{module_name}")
        handler_class = getattr(module, class_name)
        self.handle = handler_class(**self.handler_config)


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
