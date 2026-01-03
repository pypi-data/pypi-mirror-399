from pathlib import Path
from typing import Any, Callable

from .utils import download_from_uci
from .tabular_dataset import TabularDataset


class UCIDataset(TabularDataset):
    """
    Class for loading datasets from UCI machine learning repository.

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        id: int,
        filename: str,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        root = root or Path.cwd()
        path = Path(root) / filename

        if download:
            path = download_from_uci(id, root=root, filename=filename)

        super().__init__(
            path=path,
            train=train,
            transform=transform,
            train_size=train_size,
            split_seed=42,
            **kwargs,
        )


class Adult(UCIDataset):
    """
    UCI Adult dataset.

    Source:
    Becker, B and Kohavi, R. (1996).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/2/adult

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=2,
            filename="adult.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class AirQuality(UCIDataset):
    """
    UCI Air quality dataset.

    Source:
    Vito, S. (2008).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/360/air+quality

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=360,
            filename="air_quality.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class BankMarketing(UCIDataset):
    """
    UCI Bank Marketing dataset.

    Source:
    Moro et al. (2014).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/222/bank+marketing

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=222,
            filename="heart_disease.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class HeartDisease(UCIDataset):
    """
    UCI Heart Disease dataset.

    Source:
    Janosi et al. (1989).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/45/heart+disease

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=45,
            filename="heart_disease.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class Iris(UCIDataset):
    """
    UCI Iris dataset.

    Source:
        Fisher, R. A. (1936).
        UCI Machine Learning Repository.
        https://archive.ics.uci.edu/dataset/53/iris

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=53,
            filename="iris.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class OnlineRetail(UCIDataset):
    """
    UCI Online Retail dataset.

    Source:
    Chen, D. (2015).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/352/online+retail

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=352,
            filename="online_retail.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class REV(UCIDataset):
    """
    UCI Real Estate Valuation dataset.

    Source:
    Yeh, I. (2018).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/477/real+estate+valuation+data+set

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=477,
            filename="rev.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class WDBC(UCIDataset):
    """
    UCI Breast Cancer Wisconsin Diagnostic dataset.

    Source:
    Wolberg et al. (1993).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=17,
            filename="wdbc.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )


class WineQuality(UCIDataset):
    """
    UCI Wine Quality dataset.

    Source:
    Cortez et al. (2009).
    UCI Machine Learning Repository.
    https://archive.ics.uci.edu/dataset/186/wine+quality

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(
            id=186,
            filename="wine_quality.csv",
            root=root,
            train=train,
            transform=transform,
            download=download,
            train_size=train_size,
            **kwargs,
        )
