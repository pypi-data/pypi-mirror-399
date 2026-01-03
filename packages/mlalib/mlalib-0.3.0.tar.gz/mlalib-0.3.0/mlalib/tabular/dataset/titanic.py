from pathlib import Path
from typing import Any, Callable

from .tabular_dataset import TabularDataset
from ...utils import download_from_url


class Titanic(TabularDataset):
    """
    Titanic dataset.

    Source:
        Stanford University, CS109: Probability for Computer Scientists.
        Original data compiled by:
        British Board of Trade (1912).

        https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv

    Args:
        root (str, Path or None): Optional directory where the dataset file is stored or to be downloaded.
        Uses current working directory if None. Defaults to None.
        train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
        Defaults to None.
        transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
        download (bool): Whether to download the dataset from the internet. Defaults to False.
        train_size (float): Fraction of data to include in the train split. Defaults to 0.8.
    """

    URL = "https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv"
    FILE_NAME = "titanic.csv"

    def __init__(
        self,
        root: str | Path | None = None,
        train: bool | None = None,
        transform: Callable | None = None,
        download: bool = False,
        train_size: float = 0.8,
        **kwargs: Any,
    ):
        root = root or Path.cwd()
        path = Path(root) / self.FILE_NAME

        if download:
            path = download_from_url(self.URL, root=root, filename=self.FILE_NAME)

        super().__init__(
            path=path,
            train=train,
            transform=transform,
            train_size=train_size,
            split_seed=42,
            **kwargs,
        )
