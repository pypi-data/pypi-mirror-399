import os
from typing import Literal

VitalEnvironmentT = Literal["sandbox", "production"]
VitalRegionT = Literal["us", "eu"]


def api_base_url(environment: VitalEnvironmentT, region: VitalRegionT) -> str:
    if base_url := os.getenv("VITALX_BASE_URL"):
        return base_url

    match region:
        case "us":
            match environment:
                case "production":
                    return "https://api.tryvital.io/"
                case "sandbox":
                    return "https://api.sandbox.tryvital.io/"
        case "eu":
            match environment:
                case "production":
                    return "https://api.eu.tryvital.io/"
                case "sandbox":
                    return "https://api.sandbox.eu.tryvital.io/"
