import importlib
import structlog
from dataclasses import dataclass
from strictyaml import Map, Str, Float, Seq, Enum as YamlEnum, Url, Optional, Any
from enum import Enum

log = structlog.get_logger()


class PrinterState(Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    PRINTING = "PRINTING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    ATTENTION = "ATTENTION"
    READY = "READY"


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
                    "handler": Str(),
                    "handler_config": Any(),
                    Optional("printer_link"): Map(
                        {
                            "url": Url(),
                            "username": Str(),
                            "password": Str(),
                            "snapshot_states": Seq(YamlEnum([x.value for x in PrinterState])),
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
class PrinterLink:
    url: str
    username: str
    password: str
    snapshot_states: list[PrinterState]

    def __post_init__(self):
        self.snapshot_states = [PrinterState(x) for x in self.snapshot_states]


@dataclass
class Camera:
    name: str
    fingerprint: str
    token: str
    interval: float
    handler: str
    handler_config: dict
    printer_link: PrinterLink | None = None

    def __post_init__(self):
        self.printer_link = PrinterLink(**self.printer_link) if self.printer_link else None

        module_name = ".".join(self.handler.split(".")[0:-1])
        class_name = self.handler.split(".")[-1]
        log.debug(f"Importing {class_name} from {module_name}")
        module = importlib.import_module(module_name)
        handler_class = getattr(module, class_name)
        self.handle: "Camera.BaseCameraHandler" = handler_class(self, self.handler_config)
