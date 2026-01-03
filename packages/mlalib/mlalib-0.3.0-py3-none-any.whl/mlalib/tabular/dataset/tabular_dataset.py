import csv
import math
from pathlib import Path
from itertools import islice
from typing import Callable, Union

import pandas as pd

PandasObj = Union[pd.DataFrame, pd.Series]


class TabularDataset:
    """
    A convenience class for loading tabular datasets from disk or URL,
    applying optional transforms, splitting into train/test sets, and converting
    the results into tensors/TensorDataset.

    Args:
            path (str or path): Path tabular dataset.
            train (bool or None): Instance uses train split if True, test split if False and full dataset if None.
            Only works in 'eager' mode. Defaults to None.
            transform (Callable or None): Optional transformation to apply to the dataset. Defaults to None.
            train_size (float): Fraction of data to include in the train split. Defaults to 1.0.
            split_seed (int): Random seed for train/test split. Defaults to 42.
            mode (str): Whether to load data in 'eager' or 'lazy' mode. Defaults to 'eager'.
            chunk_size (int): Number of rows to load in 'lazy' mode at a time. Defaults to 1024.
            file_ext (str or None): Optional file extension override (e.g., ".csv"). Defaults to None.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        train: bool | None = None,
        transform: Callable[[PandasObj], PandasObj] | None = None,
        train_size: float = 0.8,
        split_seed: int = 42,
        mode: str = "eager",
        chunk_size=1024,
        file_ext: str | None = None,
    ):
        self._path = Path(path)
        self._transform = transform
        self._mode = mode
        self.data = None
        ext = file_ext or self._path.suffix.lower()

        if not self._path.exists():
            raise FileNotFoundError(f"dataset not found: '{self._path}'")

        if mode not in {"eager", "lazy"}:
            raise ValueError(
                f"invalid mode: '{mode}'. Expected one of 'eager' or 'lazy'"
            )
        if not 0 <= train_size <= 1:
            raise ValueError(f"train size must be between 0 and 1, got {train_size}")

        if mode == "eager":
            readers = {
                ".csv": pd.read_csv,
                ".xlsx": pd.read_excel,
                ".xls": pd.read_excel,
                ".json": pd.read_json,
                ".parquet": pd.read_parquet,
            }
            if ext not in readers:
                raise ValueError(
                    f"unsupported file format: '{ext}', expected one of {list(readers.keys())}"
                )

            df = readers[ext](self._path)

            if train is not None:
                train_df = df.sample(frac=train_size, random_state=split_seed)

                if train:
                    df = train_df.reset_index(drop=True)
                else:
                    df = df.drop(train_df.index).reset_index(drop=True)

            self._num_samples = len(df)
            self.data = self._transform(df) if self._transform else df

        else:
            if ext != ".csv":
                raise ValueError("lazy mode is only supported for csv files")

            self._chunk_size = chunk_size

            with open(self._path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                self._columns = next(reader)
                self._num_rows = sum(1 for _ in reader)

            self._num_chunks = math.ceil(self._num_rows / self._chunk_size)

    def __len__(self):
        if self._mode == "eager":
            return self._num_samples
        else:
            return self._num_chunks

    def __getitem__(self, idx: int):
        if self._mode == "eager":
            if isinstance(self.data, (tuple, list)):
                return tuple(
                    d.iloc[idx] if hasattr(d, "iloc") else d[idx] for d in self.data
                )
            return self.data.iloc[idx] if hasattr(self.data, "iloc") else self.data[idx]

        else:
            if idx < 0:
                idx = self._num_chunks + idx

            if not (0 <= idx < self._num_chunks):
                raise IndexError(
                    f"chunk index {idx} out of range (0-{self._num_chunks-1})"
                )

            start = idx * self._chunk_size
            end = min(start + self._chunk_size, self._num_rows)

            with open(self._path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # skip header
                rows = list(islice(reader, start, end))

            data = pd.DataFrame(rows, columns=self._columns)

            if self._transform:
                data = self._transform(data)

            return data
