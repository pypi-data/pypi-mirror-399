"""解析用データ読み込みのモジュール


:TODO:
作りはじめてみましたが、config.RunManagerに統合できそうな気がしてきました。
できることを比べながら、こちらを削除する予定にします。

"""

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pendulum
from loguru import logger
from pydantic import BaseModel
from deprecated import deprecated


class PathSettings(BaseModel):
    """データセットのパス設定

    :TODO:
    - データセットの配置を変更したら、パスのデフォルト値を変更する

    """

    drive: str = "."
    """測定データがあるルートディレクトリ。デフォルトは`.`（カレントディレクトリ）"""

    def _get_path(self, path: str) -> Path:
        """（プライベート関数）データのパスを取得

        `drive`と`path`を使って読み込みたいデータのパスを取得します。

        :Args:
            - `path (str)`: パス名

        :Exception:
            - 指定したパスが存在しない場合は`drive`に設定

        :Returns:
            - ` p (Path)`: データのパス
        """
        p = Path(self.drive) / path
        if not p.exists():
            msg = f"Path does not exist. {p}"
            logger.error(msg)
            p = Path(self.drive)
            msg = f"Fallback to root path. {p}"
            logger.warning(msg)
        return p

    def raw_data_path(self, path: str = "raw_data") -> Path:
        """測定データのパス

        :Args:
            - `path (str, optional)`: パス名. Defaults to "raw_data".

        :Returns:
            - `p (Path)`: 測定データのパス
        """
        p = self._get_path(path)
        return p

    def preprocessed_data_path(self, path: str = "parsed") -> Path:
        """前処理したデータのパス

        :Args:
            - `path (str, optional)`: パス名. Defaults to "parsed".

        :Returns:
            - `p (Path)`: 前処理したデータのパス
        """

        p = self._get_path(path)
        return p

    def resampled_data_path(self, path: str = "parsed") -> Path:
        """リサンプルしたデータのパス"""
        p = self._get_path(path)
        return p


class Run(PathSettings):
    """ラン設定

    :Examples:

    ```python
    run = Run(run_id=65, date="20240521")
    data1 = run.preprocessed_data()
    data2 = run.resample_data()
    data3 = run.ondotori_data()
    ```

    実行する場所からデータセットまでのパスを``drive``で変更できます。

    ```python
    run = Run(run_id=65, date="20240521", drive="../data")
    data = run.resample_data()
    ```

    """

    run_id: int
    """ラン番号"""

    date: str
    """測定日"""

    name: str | None = None
    """ファイル名"""

    def model_post_init(self, __context: Any) -> None:
        if self.name is None:
            self.name = self._stem()
        return super().model_post_init(__context)

    def _stem(self) -> str:
        """（プライベート関数）ファイル名のstemを取得する"""
        stem = f"{self.date}_run{self.run_id}"
        return stem

    def _osechi_raw_data(self, search_pattern="osechi_data_*.csv") -> list[Path]:
        """（プライベート関数）前処理したファイル名のリストを取得する"""
        p = self.raw_data_path() / self.name
        fnames = sorted(p.glob(search_pattern))
        return fnames

    def _osechi_preprocessed_data(self) -> list[Path]:
        """（プライベート関数）前処理したファイル名のリストを取得する"""
        p = self.preprocessed_data_path()
        if not p.exists():
            msg = f"Path does not exist. {p}"
            logger.error(msg)
        fnames = sorted(p.glob(f"{self._stem()}.csv.gz"))
        return fnames

    def _osechi_resampled_data(self) -> list[Path]:
        """（プライベート関数）リサンプルしたファイル名のリストを取得する"""
        p = self.resampled_data_path()
        fnames = sorted(p.glob(f"{self._stem()}.csv"))
        return fnames

    def _ondotori_raw_data(self) -> list[Path]:
        """（プライベート関数）おんどとりのデータを取得する"""
        p = self.raw_data_path() / self._stem()
        fnames = sorted(p.glob("TR41_*.csv"))
        return fnames

    def _threshlod_logs_data(self) -> list[Path]:
        """（プライベート関数）スレッショルド設定のログを取得する"""
        p = self.raw_data_path() / self._stem()
        fnames = sorted(p.glob("threshold_logs.csv"))
        return fnames

    def _threshold_scan_data(self, search_pattern) -> list[Path]:
        """（プライベート関数）スレッショルド測定のデータを取得する"""
        p = self.raw_data_path() / self._stem()
        fnames = sorted(p.glob(search_pattern))
        return fnames

    def _to_dataframe(self, fnames, **kwargs) -> pd.DataFrame:
        """（プライベート関数）すべてのファイルをデータフレームに変換する

        :Args:
        - `fnames (list[Path])`: ファイル名のリスト
        - `**kwargs`: pd.DataFrameのオプション

        :Returns:
        - `data (pd.DataFrame)`: データフレーム
        """
        dfs = []
        for fname in fnames:
            df = pd.read_csv(fname, **kwargs)
            if not df.empty:
                dfs.append(df)
        if len(dfs) > 0:
            data = pd.concat(dfs, ignore_index=True)
        else:
            data = pd.DataFrame()
        return data

    def preprocessed_data(self) -> pd.DataFrame:
        """前処理したデータフレーム"""
        fnames = self._osechi_preprocessed_data()
        data = self._to_dataframe(fnames, parse_dates=["time"])
        return data

    def resampled_data(self) -> pd.DataFrame:
        """リサンプルしたデータフレーム"""
        fnames = self._osechi_resampled_data()
        data = self._to_dataframe(fnames, parse_dates=["time"])
        return data

    def ondotori_data(self) -> pd.DataFrame:
        """おんどとりのデータフレーム"""
        fnames = self._ondotori_raw_data()
        data = self._to_dataframe(
            fnames, skiprows=4, names=["datetime", "tmpC"], parse_dates=["datetime"]
        )
        return data

    def threshold_logs(self) -> pd.DataFrame:
        """スレッショルド設定のデータフレーム"""
        fnames = self._threshlod_logs_data()
        data = self._to_dataframe(
            fnames, names=["time", "ch", "vth", "success"], parse_dates=["time"]
        )
        return data

    def threshold_scan(self, search_pattern, **kwargs) -> pd.DataFrame:
        """スレッショルド測定のデータフレーム"""
        fnames = self._threshold_scan_data(search_pattern=search_pattern)
        data = self._to_dataframe(fnames, **kwargs)
        return data

    def __str__(self):
        return self.name


def reformat_datetime(datetime: str) -> str:
    """
    日時を変換する

    :Examples:

    ```python
    >>> reformat_datetime("2022-05-18T20:48:14")
    2022-05-18T20:48:14

    >>> reformat_datetime("2022-06-02T18:52:36.442190+09:00")
    2022-06-02T18:52:36
    ```

    """
    dt = pendulum.parse(datetime)
    fmt = dt.format("YYYY-MM-DDTHH:mm:ss")
    return fmt


@deprecated(
    version="0.15.0",
    reason="削除する予定の関数です。Runオブジェクトを使ってみてください。",
)
def load_raw_data(fname: Path, **kwargs) -> pd.DataFrame:
    """
    （削除予定）DAQで取得したデータ形式を ``pd.DataFrame`` に変換して読み込む

    :Args:
    - ``fname (Path)``: 測定データのファイル名
    - ``**kwargs``: ``pd.read_csv``のオプション


    :Returns:
    - ``data (pd.DataFrame)``: データフレーム

    :Notes:
    - ファイルの保存形式（＝拡張子）で ``pd.read_csv`` の引数をちょっと変える必要がある。拡張子は ``.dat`` / ``.csv`` だけOKにしてあり、それ以外の場合は ``sys.exit`` する。
    - ``.csv`` はそのままカンマ区切り、``.dat`` はスペース区切り（ ``sep=" "`` ）として、 ``pd.read_csv`` する。
    - ファイル内のカラム名は適当だったり、なかったりする。適切なカラム名を付与する。カラム名はこの関数内にハードコードしている。
    - イベント時刻（ ``time`` ）は ``pd.datetime`` オブジェクトに変換する。使ったDAQのバージョンによって記録された日時の形式が異なるので、それを内部で変換している。
    - 各レイヤーのヒットの有無（ ``True`` / ``False`` ）を確認して、ヒット用のカラム（ ``hit_top`` / ``hit_mid`` / ``hit_btm`` ）に保存する。現在、各レイヤーの値自体には意味がない。そのうち光量など意味を持たせる可能性はあるかも？
    - ヒットのあったレイヤーのパターンを計算して 8ビット で表現する。``hit_type = hit_top * 4 + hit_mid * 2 + hit_btm * 1``
    """

    _names = ["time", "top", "mid", "btm", "adc", "tmp", "atm", "hmd"]
    suffix = fname.suffix
    if suffix == ".dat":
        data = pd.read_csv(fname, names=_names, sep=" ", comment="t", **kwargs)
    elif suffix == ".csv":
        data = pd.read_csv(fname, names=_names, **kwargs)
    else:
        error = f"Unknown suffix : {suffix}"
        logger.error(error)
        sys.exit()

    data["time"] = data["time"].apply(reformat_datetime)
    data["time"] = pd.to_datetime(data["time"], format="ISO8601")
    # 各レイヤーのヒットの有無を確認する
    data["hit_top"] = data["top"] > 0
    data["hit_mid"] = data["mid"] > 0
    data["hit_btm"] = data["btm"] > 0
    # ヒットのあったレイヤーのパターンを8ビットで表現する
    data["hit_type"] = data["hit_top"] * 4 + data["hit_mid"] * 2 + data["hit_btm"] * 1
    return data


@deprecated(
    version="0.15.0",
    reason="削除する予定の関数です。Runオブジェクトを使ってみてください。",
)
def load_files(fnames: list[Path]) -> pd.DataFrame:
    """（削除予定）複数のファイルを読み込み、単一のデータフレームに変換する

    :Args:
    - ``fnames (list[Path])``: 測定データのファイルの一覧

    :Returns:
    - ``data (pd.DataFrame)``: すべてのファイルを結合したデータフレーム

    :Notes:
    - ``fnames`` で列挙されたファイルごとに、データフレームに変換する
    - ファイル名の一覧が空の場合は終了する
    - 個々のデータフレームを結合して単一のデータフレームを作成する
    - 結合したデータフレームは、時刻（``time``）でソートしておく
    """
    if len(fnames) == 0:
        error = "No files listed"
        logger.error(error)
        sys.exit()

    _loaded = []
    for fname in fnames:
        _data = load_raw_data(fname)
        _loaded.append(_data)
    loaded = pd.concat(_loaded, ignore_index=True)
    loaded = loaded.sort_values(["time"])
    debug = f"Entries : {len(loaded)}"
    logger.debug(debug)
    return loaded
