import sys
from pathlib import Path

import pandas as pd
import polars as pl
from loguru import logger


from .config import RunData


def get_fnames(read_from: str, search_pattern: str) -> list[Path]:
    """測定データの一覧を取得

    測定データのファイル名の一覧を取得します。
    ファイル名はPathオブジェクトに変換しています。
    リストはファイル名で昇順ソートします。

    :Args:
        - `read_from (str)`: 測定データがあるパス
        - `search_pattern (str)`: ファイル名の検索パターン

    :Returns:
        - `fnames (list[Path])`: 測定データの一覧

    :Example:

    ```python
    fnames = get_fnames(
        read_from="../data/raw_data/20240601_run80",
        search_pattern="osechi_data_*.csv")
    ```
    """
    fnames = sorted(Path(read_from).glob(search_pattern))
    return fnames


def read_data_with_pandas(fnames: list[Path]) -> pd.DataFrame:
    """pd.DataFrameに変換

    複数の測定ファイルを読み込んでpd.DataFrameに変換します。
    測定ファイルの拡張子は``.dat``と``.csv``に限定しています。

    :Args:
        - `fnames (list[Path])`: 測定データのファイル名のリスト

    :Exception:
        - ``.dat`` / ``.csv``以外の拡張子の場合は中断（break）

    :Returns:
        - `merged (pd.DataFrame)`: 結合したデータフレーム
    """
    names = ["datetime", "top", "mid", "btm", "adc", "tmp", "atm", "hmd"]
    data = []
    for fname in fnames:
        _suffix = fname.suffix
        if _suffix in [".dat"]:
            datum = pd.read_csv(fname, names=names, sep=" ", comment="t")
        elif _suffix in [".csv"]:
            datum = pd.read_csv(fname, names=names)
        else:
            msg = f"Unknown suffix: {_suffix}"
            logger.warning(msg)
            break
        data.append(datum)
    merged = pd.concat(data, ignore_index=True).dropna(how="all")

    if len(merged) == 0:
        msg = "No entries in DataFrame. Exit."
        logger.error(msg)
        sys.exit()

    return merged


def read_data_with_polars(fnames: list[Path]) -> pd.DataFrame:
    """pl.DataFrameに変換

    複数のファイルを読み込んでpl.DataFrameに変換します。
    polarsで読み込んだ方が、少し処理が速くなります。

    ただし、そのままpl.DataFrameを返すと、あとの処理がうまくいかないので、
    最後にpl.DataFrameからpd.DataFrameに変換しています。

    :Args:
        - `fnames (list[Path])`: 測定データのファイル名のリスト

    :Returns:
        - `merged (pd.DataFrame)`: 結合したデータフレーム
    """
    names = ["datetime", "top", "mid", "btm", "adc", "tmp", "atm", "hmd"]
    data = []
    for fname in fnames:
        _suffix = fname.suffix
        _stem = fname.stem
        if _suffix in [".dat"]:
            datum = pl.read_csv(
                fname,
                has_header=False,
                new_columns=names,
                separator=" ",
                comment_char="t",
            )
        elif _suffix in [".csv"]:
            if _stem.startswith("osechi_data"):
                datum = pl.read_csv(fname, has_header=False, new_columns=names)
            elif _stem.startswith("scan_data"):
                datum = pl.read_csv(fname, has_header=False, new_columns=names, skip_rows=1)
        else:
            msg = f"Unknown suffix: {_suffix}"
            logger.warning(msg)
            break
        data.append(datum)
    merged = pl.concat(data).to_pandas().dropna(how="all")

    if len(merged) == 0:
        msg = "No entries in DataFrame. Exit."
        logger.error(msg)
        sys.exit()

    return merged


def read_data(fnames: list[Path]) -> pd.DataFrame:
    """測定データをデータフレームに変換

    ``read_data_with_polars``を使ってデータフレームに変換します。

    :Example:

    ```python
    fnames = get_fnames(
        read_from=...,
        search_pattern=".csv"
        )
    data = read_data(fnames)
    ```
    """
    # data = read_data_with_pandas(fnames)
    data = read_data_with_polars(fnames)
    return data


def add_time(data: pd.DataFrame, offset: int, timezone: str) -> pd.DataFrame:
    """`time`カラムを追加

    測定データのデータフレームに``time``カラムを追加します。
    ``time``カラムは``datetime``カラムをタイムゾーン付き日時オブジェクトに変換したものです。
    また、``offset``（秒）の分、測定時刻を正しい時刻に修正します。

    :Args:
        - `data (pd.DataFrame)`: 測定データ
        - `offset (int)`: 測定時刻のオフセット（秒）
    :Returns:
        - `data (pd.DataFrame)`: ``time``カラムを追加した測定データ

    :Example:

    ```python
    data = read_data(fnames)
    data = add_time(data)
    ```

    ```{caution}
    Raspberry Pi 4はRTCを内蔵していません。電源を切ると時計がストップします。
    測定を開始する前に、ネットワークに接続してNTPから時刻を自動取得するか、
    ``date``コマンドなどで時刻を手動設定する必要があります。
    その作業を忘れてしまった場合のために、``offset``オプションがあります。
    ```

    """
    data["datetime"] = pd.to_datetime(data["datetime"], format="ISO8601")
    if data["datetime"].dt.tz is None:
        data["datetime"] = data["datetime"].dt.tz_localize(timezone)
    data["datetime_offset"] = pd.to_timedelta(offset, "s")
    data["time"] = data["datetime"] + data["datetime_offset"]
    return data


def add_hit(data: pd.DataFrame) -> pd.DataFrame:
    """`hit`カラムを追加

    各シンチのレイヤーにヒットがあったかどうかを確認し、``hit_レイヤー名``カラムを追加します。
    ヒットがある場合は``1``、ヒットがない場合は``0``です。

    :Args:
        - `data (pd.DataFrame)`: 測定データ

    :Returns:
        - `data (pd.DataFrame)`: `hit`カラムを追加したデータフレーム

    :Example:

    ```python
    data = read_data(fnames)
    data = add_time(data)
    data = add_hit(data)
    ```
    """
    copied = data.copy()
    headers = ["top", "mid", "btm"]
    for header in headers:
        name = f"hit_{header}"
        copied[name] = 0
        isT = data[header] > 0
        copied.loc[isT, name] = 1
    return copied


def add_hit_type(data: pd.DataFrame) -> pd.DataFrame:
    """`hit_type`カラムを追加

    レイヤーごとのヒット情報から、ヒットの種類を計算します。
    ヒット情報が計算できてない場合は、警告を表示し、元のデータを返します。

    :Args:
        - `data (pd.DataFrame)`: ``add_hit``したあとの測定データ

    :Returns:
        - `data (pd.DataFrame)`: ``hit_type``を追加したデータフレーム

    :Example:

    ```python
    data = read_data(fnames)
    data = add_time(data)
    data = add_hit(data)
    data = add_hit_type(data)
    ```
    """
    _header = "hit_top"
    if _header not in data.columns:
        msg = f"Header '{_header}' does not exist in current dataframe."
        logger.warning(msg)
        return data
    data["hit_type"] = 4 * data["hit_top"] + 2 * data["hit_mid"] + data["hit_btm"]
    return data


def resample_data(data: pd.DataFrame, interval: int):
    """測定データをリサンプル

    ``data``に指定した測定データを``pandas.DataFrame.resample``でリサンプルします。
    データは前処理済みのデータを指定してください。
    再集計したデータをさらに、再集計することもできます。

    :Note:
        - 入力データに必要なカラム: ``["time", "hit_type", "hit_top", "hit_mid", "hit_btm", "adc", "tmp", "atm", "hmd"]``
        - 出力データに追加されるカラム: ``["interval", "event_rate", "event_rate_top", "event_rate_mid", "event_rate_btm"]``


    :Args:
        - `data (pd.DataFrame)`: 前処理済みのデータフレーム
        - `interval (int)`: リサンプル間隔（秒）

    :Returns:
        - `merged (pd.DataFrame)`: 再集計後のデータフレーム
    """

    # 再集計する時間間隔
    rule = f"{interval}s"

    # 元データのコピーを作成
    copied = data.copy()
    # インデックスを datetime オブジェクトに変更
    copied.index = copied["time"]

    # count
    headers = {"hit_type": "events"}
    keys = list(headers.keys())
    _count = copied.resample(rule)[keys].count().reset_index().rename(columns=headers)

    # sum: 合計値
    headers = {
        "hit_top": "hit_top_sum",
        "hit_mid": "hit_mid_sum",
        "hit_btm": "hit_btm_sum",
    }
    keys = list(headers.keys())
    _sum = copied.resample(rule)[keys].sum().reset_index()

    # mean: 平均値
    headers = {
        "adc": "adc_mean",
        "tmp": "tmp_mean",
        "atm": "atm_mean",
        "hmd": "hmd_mean",
    }
    keys = list(headers.keys())
    _mean = copied.resample(rule)[keys].mean().reset_index()

    # std : 標準偏差
    headers = {
        "adc": "adc_std",
        "tmp": "tmp_std",
        "atm": "atm_std",
        "hmd": "hmd_std",
    }
    keys = list(headers.keys())
    _std = copied.resample(rule)[keys].std().reset_index().rename(columns=headers)

    # 測定日時（time）で結合
    m1 = pd.merge(_count, _sum, on="time")
    m2 = pd.merge(m1, _mean, on="time")
    merged = pd.merge(m2, _std, on="time")

    # レートを計算
    merged["interval"] = interval
    merged["event_rate"] = merged["events"] / merged["interval"]
    merged["event_rate_top"] = merged["hit_top"] / merged["interval"]
    merged["event_rate_mid"] = merged["hit_mid"] / merged["interval"]
    merged["event_rate_btm"] = merged["hit_btm"] / merged["interval"]

    # 測定時間を計算
    epoch = merged["time"].min()
    merged["days"] = merged["time"] - epoch
    merged["seconds"] = merged["days"].dt.total_seconds()

    return merged


def resample_data_with_hit_type(data: pd.DataFrame, interval: int) -> pd.DataFrame:
    """測定データをリサンプル

    ヒット種類（``hit_type``）ごとにリサンプルします。

    :Args:
        - `data (pd.DataFrame)`: ``hit_type``を持つデータフレーム
        - `interval (int)`:  リサンプルの間隔（秒）

    :Returns:
        - `resampled (pd.DataFrame)`: ``hit_type``ごとにリサンプルしたデータフレーム
    """
    hit_types = sorted(data["hit_type"].unique())
    rdata = []
    for ht in hit_types:
        q = f"hit_type == {ht}"
        qdata = data.query(q).copy()
        _resampled = resample_data(qdata, interval)
        _resampled["hit_type"] = ht
        rdata.append(_resampled)

    resampled = pd.concat(rdata, ignore_index=True)
    resampled = resampled.sort_values(["time", "hit_type"])
    return resampled


def preprocess_data(
    data: pd.DataFrame, interval: int, datetime_offset: int, timezone: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """測定データを前処理する

    :Args:
        - `data (pd.DataFrame)`: 測定データ
        - `interval (int)`: リサンプル間隔（秒）
        - `datetime_offset (int)`: 時刻のオフセット（秒）
        - `timezone (str)`: タイムゾーン情報

    :Returns:
        - `data (pd.DataFrame)`: 前処理したあとのデータ
        - `resampled (pd.DataFrame)`: リサンプルしたデータ
    """
    data = add_time(data, offset=datetime_offset, timezone=timezone)
    data = add_hit(data)
    data = add_hit_type(data)
    resampled = resample_data_with_hit_type(data, interval)
    return data, resampled


def raw2csv(
    fnames: list[Path], interval: int, datetime_offset: int, timezone: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """測定データを指定してデータフレームに変換する

    :Args:
        - `fnames (list[Path])`: 前処理するファイル名のリスト
        - `interval (int)`: リサンプル間隔（秒）
        - `datetime_offset (int)`: 時刻のオフセット（秒）
        - `timezone (str)`: タイムゾーン情報

    :Returns:
        - `data (pd.DataFrame)`: 前処理したあとのデータ
        - `resampled (pd.DataFrame)`: リサンプルしたデータ

    """
    if len(fnames) == 0:
        msg = "No files found."
        logger.error(msg)
        sys.exit()

    data = read_data(fnames)
    data, resampled = preprocess_data(data, interval, datetime_offset, timezone)
    return data, resampled


def run2csv(run: RunData) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ランを指定してデータフレームに変換する

    :Args:
        - `run (RunData)`: RunDataオブジェクト

    :Returns:
        - `data (pd.DataFrame)`: 前処理したあとのデータ
        - `resampled (pd.DataFrame)`: リサンプルしたデータ

    :Example:

    ```python
    run = RunData(...)
    data, resampled = run2csv(run)
    print(f"gzip={len(data)}")
    print(f"csv ={len(resampled)}")
    ```

    """
    fnames = get_fnames(read_from=run.read_from, search_pattern=run.srcf)
    interval = run.interval
    datetime_offset = run.datetime_offset
    timezone = "UTC+09:00"

    data, resampled = raw2csv(fnames, interval, datetime_offset, timezone)
    data["runid"] = run.run_id
    data["name"] = run.name
    data["description"] = run.description

    resampled["runid"] = run.run_id
    resampled["name"] = run.name
    resampled["description"] = run.description

    return data, resampled


if __name__ == "__main__":
    fname = "../data/raw_data/20230806_run17/osechi_data_000000.csv"
    fnames = [Path(fname)]
    gzip, csv = raw2csv(fnames, interval=600, datetime_offset=0, timezone="UTC+09:00")
    logger.debug(f"raw2gz  = {len(gzip)}")
    logger.debug(f"raw2csv = {len(csv)}")
