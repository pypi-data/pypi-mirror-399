from .tabular_dataset import TabularDataset
from .titanic import Titanic
from .uci_dataset import (
    Adult,
    AirQuality,
    BankMarketing,
    HeartDisease,
    Iris,
    OnlineRetail,
    REV,
    UCIDataset,
    WDBC,
    WineQuality,
)
from .utils import download_from_uci

__all__ = [
    "download_from_uci",
    "Adult",
    "AirQuality",
    "BankMarketing",
    "HeartDisease",
    "Iris",
    "OnlineRetail",
    "REV",
    "TabularDataset",
    "Titanic",
    "UCIDataset",
    "WDBC",
    "WineQuality",
]
