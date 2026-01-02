from dataclasses import dataclass
from icecream import ic
from loguru import logger
from pathlib import Path
from typing import Optional, Any
import pandas as pd
import sys
import tomli  # Python3.9対応のためtomliを使う
from deprecated import deprecated

# import tomllib  # TODO: いずれtomllibに置き換える
from pydantic import BaseModel

ic.configureOutput(prefix=f"{__name__}: ")


@dataclass
class RunData:
    """
    ランごとの設定

    それぞれのランの情報／設定を整理するためのクラスです。
    ランを走らせた時の設定は、Googleスプレッドシートで管理しています
    （更新・共有の手軽さを考慮してスプレッドシートを採用しました）。

    :TODO:
        - スプレッドシートをCSV形式でダウンロードして、RunDataオブジェクトに変換するツールを作りたい
    """

    run_id: int
    """ラン番号"""

    description: str = ""
    """ランの簡単な説明。詳しい説明はGoogleスプレッドシートで説明"""

    read_from: str = ""
    """測定データが保存されているディレクトリ名"""

    srcf: str = "*.csv"
    """測定データの拡張子。デフォルトはCSV形式"""

    interval: int = 600
    """サンプリング間隔（秒）。デフォルトは600秒（10分）"""

    datetime_offset: int = 0
    """測定器の時刻と実時刻の時間差（秒）。デフォルトは0秒"""

    skip: bool = False
    """データ処理スキップのフラグ。デフォルトはFalse"""

    nfiles: int = 0
    """測定データのファイル数。デフォルトは0"""

    raw2gz: str = ""
    """出力ファイル名。リサンプルなし。指定がない場合は保存しない"""

    raw2csv: str = ""
    """出力ファイル名。リサンプルあり。指定がない場合は保存しない"""

    query: str = ""
    """データの抽出条件。有効なデータを指定する"""

    def __post_init__(self) -> None:
        """RunDataクラスの初期化"""
        self.name = f"Run{self.run_id}"
        try:
            self.fnames = self.get_fnames()
        except FileNotFoundError as e:
            logger.warning(e)
            msg = "self.fnames set to []"
            logger.info(msg)
            self.fnames = []
        self.nfiles = len(self.fnames)

    def get_fnames(self) -> list[Path]:
        """該当するランのファイル名の一覧を取得

        `read_from`と`srcf`の値から、該当するファイルの一覧を、
        `pathlib.Path`オブジェクトのリストとして取得します。

        :Exception:
            - `read_from`ディレクトリが存在しない場合は終了

        :Returns:
            - `fnames (list[Path])`: ファイル名のリスト
        """

        read_from = Path(self.read_from).expanduser()
        srcf = self.srcf

        if not read_from.exists():
            msg = f"No directory found : {read_from}"
            raise FileNotFoundError(msg)

        fnames = sorted(read_from.glob(srcf))
        return fnames

    def _load_gzip(self) -> Optional[pd.DataFrame]:
        """gzipで保存したデータを読み込む

        ``raw2gz``で指定したファイル名を`pd.DataFrame`に変換します。

        :Exception:
            - `raw2gz`ファイルが存在しない場合は終了

        :Returns:
            - `data (pd.DataFrame | None)`: データフレーム
        """
        p = Path(self.raw2gz)
        if p.exists():
            data = pd.read_csv(self.raw2gz, parse_dates=["time"])
            return data
        else:
            msg = f"File not found. {p}"
            raise FileNotFoundError(msg)

    def _load_csv(self) -> Optional[pd.DataFrame]:
        """csvで保存したデータを読み込む

        ``raw2csv``で指定したファイルを``pd.DataFrame`に変換します。

        :Exception:
            - ``raw2csv``ファイルが存在しない場合は終了

        :Returns:
            - `data (pd.DataFrame | None)` : データフレーム
        """
        p = Path(self.raw2csv)
        if p.exists():
            data = pd.read_csv(self.raw2csv, parse_dates=["time"])
            return data
        else:
            msg = f"File not found. {p}"
            raise FileNotFoundError(msg)

    def load_data(self, kind: str) -> Optional[pd.DataFrame]:
        """形式を指定してデータを読み込む

        `kind`で測定データの読み取り形式を指定します。
        指定できる形式は`csv`もしくは`gzip`です。

        :Args:
            - `kind (str)`: 保存したデータの形式。["csv", "gzip"]

        :Returns:
            - `data (pd.DataFrame)`: データフレーム
        """
        if kind == "csv":
            return self._load_csv()
        elif kind == "gzip":
            return self._load_gzip()
        else:
            fmt = ["csv", "gzip"]
            msg = f"Wrong file type : {kind}. Choose from {fmt}."
            raise ValueError(msg)


@dataclass
class Config:
    """（削除予定）ラン設定ファイル用のクラス

    :TODO:
        - RunManagerクラスを別途作成した
        - 重複する箇所は置き換える

    """

    fname: str = "config.toml"
    """設定ファイル。デフォルトは`config.toml`"""

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def __post_init__(self) -> None:
        """（削除予定）
        - ``self.config``
        - ``self.rules``
        - ``self.runs``
        """
        self.config = self.load_config()
        self.rules = self.get_rules()
        self.runs = self.get_runs()
        self.labels = self.get_labels()

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def load_config(self) -> dict:
        """（削除予定）設定ファイルを読み込む

        :Returns:
        - config(dict) : 設定

        :Notes:
        - デフォルトの設定ファイル名は `config.toml`
        - 設定ファイルの名前は変更することができる
        - 設定ファイルが見つからない場合は、エラーを表示してスキップ（早期リターン）する
        - 設定ファイルは辞書型で読み込む
        """
        p = Path(self.fname)

        if not p.exists():
            msg = f"No file found : {p}"
            raise FileNotFoundError(msg)

        with p.open("rb") as f:
            config = tomli.load(f)
        return config

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def get_rules(self) -> dict:
        """（削除予定）イベント条件に関する設定を取得する

        :Returns:
        - rules(dict): {イベント名 : イベント条件}

        :Notes:
        - 設定ファイルの ``[rules]`` セクションの内容を取得する
        - ``条件名 = 条件式`` の辞書型（map型）で定義されている

        """
        rules = self.config.get("rules")
        return rules  # type: ignore

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def get_labels(self) -> Optional[dict]:
        """（削除予定）カラム名を取得する

        ``[labels]`` のセクションに、カラム名に対応した日本語を記述する

        """
        labels = self.config.get("labels")
        return labels

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def get_run(self, run_id: int) -> RunData:
        """（削除予定）ラン番号を指定してラン情報を取得する"""
        for run in self.runs:
            if run.run_id == run_id:
                return run
        msg = f"Run #{run_id} is out of range. Add to config."
        logger.error(msg)
        sys.exit()

    @deprecated(version="v0.17.2", reason="Replace with RunManager.")
    def get_runs(self) -> list[RunData]:
        """（削除予定）ランに関係する設定を取得する

        :Returns:
        - runs(list[RunData]): ランごとに設定をまとめたリスト

        :Notes:
        - 設定ファイルの ``[[rawdata]]`` セクションの内容を ``RunData`` クラスにまとめる
        - 除外するランがある場合は ``skip = true`` を設定する
        """
        runs = []
        rundata = self.config["rundata"]
        for data in rundata:
            if data.get("skip") is None:
                run = data.get("run")
                error = f"Run{run} : No configuration found for 'skip'"
                logger.error(error)
                sys.exit()

            if not data.get("skip"):
                _data = RunData(
                    run_id=data["run"],
                    read_from=data["read_from"],
                    srcf=data["srcf"],
                    interval=data["interval"],
                    datetime_offset=data.get("datetime_offset", 0),
                    description=data["desc"],
                    skip=data["skip"],
                    raw2gz=data.get("raw2gz"),
                    raw2csv=data.get("raw2csv"),
                    query=data.get("query"),
                )
                runs.append(_data)
        return runs


@dataclass
class Daq:
    """DAQ設定クラス

    :Example:

    ```python
    daq = Daq()
    daq.load_toml(fname="TOML形式のファイル")

    # 現在日時をベースにした保存先に変更
    now = pendulum.now().format("YYYYMMDD")
    daq.saved =  str(Path(daq.saved) / now)
    ```

    """

    saved: str = "."
    """測定データを保存するディレクトリ。デフォルトは`.`（カレントディレクトリ）"""

    prefix: str = "data"
    """測定データのファイル名につける接頭辞。デフォルトは`data`"""

    suffix: str = ".csv"
    """測定データの拡張子。デフォルトは`.csv`"""

    skip: int = 10

    max_rows: int = 10000
    """1ファイルあたりのデータ数。デフォルトは`10000`"""

    max_files: int = 100
    """1ランあたりのファイル数。デフォルトは`100`"""

    quiet: bool = False
    """quietモード用フラグ。デフォルトはFalse"""

    append: bool = False
    """追記モード用フラグ。デフォルトはFalse"""

    device: str = "/dev/ttyUSB0"
    """シリアル通信のポート名。デフォルトは`/dev/ttyUSB0`（Linux用）"""

    baudrate: int = 115200
    """シリアル通信レート（ボーレート）。デフォルトは`115200` [bps]"""

    timeout: int = 1000
    """シリアル通信のタイムアウト設定（秒）。デフォルトは`1000`秒"""

    fname_logs: str = "threshold_logs.csv"
    """ファイル名。スレッショルド設定のログ"""

    fname_scan: str = "threshold_scan.csv"
    """ファイル名。スレッショルド測定の結果"""

    def load_toml(self, fname: str) -> None:
        "Load DAQ configuration from TOML"
        p = Path(fname)
        with p.open("rb") as f:
            _config = tomli.load(f)

        # logger.debug(_config)
        self.saved = _config.get("saved", ".")
        self.prefix = _config.get("prefix", "data")
        self.suffix = _config.get("suffix", ".csv")
        self.skip = _config.get("skip", 10)
        self.max_rows = _config.get("max_rows", 10000)
        self.max_files = _config.get("max_files", 100)
        self.quiet = _config.get("quiet", False)
        self.append = _config.get("append", False)
        self.device = _config.get("device", "/dev/ttyUSB0")
        self.baudrate = _config.get("baudrate", 115200)
        self.timeout = _config.get("timeout", 1000)
        self.fname_logs = _config.get("fname_logs", "threshold_logs.csv")
        self.fname_scan = _config.get("fname_scan", "threshold_scan.csv")


class UserSettings(BaseModel):
    """ユーザー設定用のクラス

    ``read_from`` に指定したファイルからユーザー設定を読み込みます。
    設定ファイルはTOML形式で作成してください。
    その他の形式に対応する予定はいまのところありません。
    また、読み込み時のファイル形式のチェックもしていません。

    :TODO:
        - ``daq.toml``、``scan.toml``から``hnw.toml``に移行する
        - クラス名を`DaqManager`に変更する

    :versionadded:
        `0.12.0`

    :Example:

    ```python
    us = UserSettings(load_from="../sandbox/hnw.toml")
    us.settings
    {
        'default': {'saved': '', 'suffix': '.csv', 'skip': 10, 'max_rows': 1000},
        'device': {'port': '/dev/ttyUSB0', 'baudrate': 115200, 'timeout': 100},
        'daq': {'prefix': 'osechi_data', 'max_files': 1000},
        'scan': {'prefix': 'scan_data', 'max_files': 10, 'timeout': 10},
        'threshold': {'logs': {'fname': 'threshold_logs.csv',
        'names': ['time', 'ch', 'vth', 'success']},
        'scan': {'fname': 'threshold_scan.csv',
        'names': ['time', 'duration', 'ch', 'vth', 'events']
    }

    us.sections
    dict_keys(
        ['default', 'device', 'daq', 'scan', 'threshold', 'loguru']
    )
    ```

    """

    load_from: str
    """設定ファイルを指定する"""

    settings: dict = {}
    """読み込んだ設定値の一覧"""

    sections: list = []
    """読み込んだ設定セクションの一覧"""

    def model_post_init(self, __context: Any) -> None:
        """UserSettingsクラスの初期化"""
        settings = self.load_toml(self.load_from)
        self.settings = settings
        self.sections = list(settings.keys())
        return super().model_post_init(__context)

    def load_toml(self, load_from: str) -> dict:
        """TOML形式の設定を読み込む

        UserSettingsクラスのオブジェクトを生成するときに ``__post_init__``の中で実行している。
        プロダクション環境では、このメソッドをわざわざ実行する必要はありません。

        新しい設定ファイルを作成した場合の内容確認のために使えると思います。

        :Args:
            - `load_from (str)`: ファイル名

        :Returns:
            - `settings (dict)`: ユーザー設定

        """
        p = Path(load_from)
        with p.open("rb") as f:
            settings = tomli.load(f)
        return settings

    def _get_settings(self, keys: list) -> dict:
        """キーを指定してユーザー設定を取得

        キーはTOMLファイルのセクションに対応しています。
        キーは複数指定できます。
        同じ設定項目がある場合、あとに設定した値が優先されます。

        指定したキーが設定ファイルに存在しない場合はスキップします。

        :Args:
            `keys (list)`: 設定キーをリストで指定する

        :Returns:
            `settings (dict)`: 設定値の一覧

        :Example:

        ```python
        us = UserSettings(load_from="../sandbox/hnw.toml")
        keys = ["default", "device", "scan", "threshold"]
        settings = s._get_settings(keys)
        ```

        """
        settings = {}
        for key in keys:
            d = self.settings.get(key)
            if d is None:
                pass
            else:
                settings.update(d)
        return settings

    def get_daq_settings(self) -> dict:
        """DAQの設定を取得する

        :Note:

            ``keys = ["default", "device", "daq"]``に相当

        :Returns:
            - `settings (dict)`: DAQの設定に必要な項目

        :Example:

        ```python
        us = UserSettings(load_from="../sandbox/hnw.toml")
        settings = us.get_daq_settings()
        settings
        {
            'saved': '',
            'suffix': '.csv',
            'skip': 10,
            'max_rows': 1000,
            'port': '/dev/ttyUSB0',
            'baudrate': 115200,
            'timeout': 100,
            'prefix': 'osechi_data',
            'max_files': 1000
        }
        ```

        """
        keys = ["default", "device", "daq"]
        settings = self._get_settings(keys)
        return settings

    def get_scan_settings(self) -> dict:
        """スレッショルド測定の設定を取得

        :Note:

            ``keys = ["default", "device", "scan", "threshold"]``に相当

        :Returns:
            - `settings (dict)`: スレッショルド測定に必要な項目

        :Example:

        ```python
        us = UserSettings(load_from="../sandbox/hnw.toml")
        settings = us.get_scan_settings()
        settings
        {
            'saved': '',
            'suffix': '.csv',
            'skip': 10,
            'max_rows': 1000,
            'port': '/dev/ttyUSB0',
            'baudrate': 115200,
            'timeout': 10,
            'prefix': 'scan_data',
            'max_files': 10,
            'logs': {'fname': 'threshold_logs.csv', 'names': ['time', 'ch', 'vth', 'success']},
            'scan': {'fname': 'threshold_scan.csv', 'names': ['time', 'duration', 'ch', 'vth', 'events']},
            'fit': {'fname': 'threshold_fit.csv', 'names': ['time', 'ch', '0sigma', '1sigma', '3sigma', '5sigma']}
        }
        ```

        """

        keys = ["default", "device", "scan", "threshold"]
        settings = self._get_settings(keys)
        return settings

    def get_loguru(self, level: str = "DEBUG") -> logger:
        """ロガーを初期化する

        loguruパッケージを使ったロガーを初期化します。
        ``level`` オプションで指定したログレベルで、標準エラー出力（``sys.stderr``）のハンドラーを作成します。

        以下のような ``[loguru]`` セクションを作成することで、ファイル出力のハンドラーを追加できます。
        このハンドラーのログレベルは``DEBUG``、出力形式はJSON形式にハードコードしています。

        ```toml
        [loguru]
        sink = "required"
        format = "required"
        retention = "optional"
        rotation = "optional"
        ```

        :Args:
            - `level (str)`: 標準エラー出力のログレベル。デフォルトは"DEBUG"。

        :Returns:
            - `logger (loguru.logger)`: ロガー

        :Example:

        ```python
        us = UserSettings(load_from="../sandbox/hnw.toml")
        logger = us.get_loguru()
        logger.info("ロガーを初期化した")
        ```
        """
        # ロガーの既定値をリセット
        logger.debug("ロガーをリセットする")
        logger.remove()

        # 標準エラー（sys.stderr）出力のハンドラーを追加
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DDTHH:mm:ss} | <level>{level:8}</level> | <level>{message}</level>",
            level=level,
        )
        logger.debug(f"標準エラー出力のハンドラーを追加した（{level=}）")

        # ファイル出力のハンドラーを追加
        section = self.settings.get("loguru")

        if section is None:
            return logger

        # ファイルから読み込んだ値を設定
        logger.add(
            sink=section.get("sink"),
            format=section.get("format"),
            level="DEBUG",
            retention=section.get("retention"),
            rotation=section.get("rotation"),
            serialize=True,
        )
        logger.info("ファイル出力のハンドラーを追加した")
        return logger


@dataclass
class RunManager:
    """ランの設定をスプレッドシートから読み込む"""

    load_from: str
    "ファイル名。データを記録したスプレッドシートを指定する"

    query: str = "run_id > 0"
    "クエリ。データを読み込む条件を指定する"

    drive: str = "data"
    "ディレクトリ名。上記ファイルまでの相対パスを指定する"

    is_valid: bool = True
    "データ用フラグ。スレッショルド測定の解析時はFalseにする"

    is_test: bool = False
    "テスト用フラグ。ユニットテストで実行するときはTrueにする"

    def __post_init__(self):
        self.data = self._load_data()
        self.runs = self._get_runs(self.is_valid)

    def _load_data(self) -> pd.DataFrame:
        """ファイルから設定を読み込む"""
        data = pd.read_csv(self.load_from, skiprows=2)
        # NaNを処理する
        data = data.fillna("")
        return data

    def get_records(self, query: str, is_valid: bool) -> pd.DataFrame:
        """条件にマッチしたレコードを取得

        `query`にマッチしたレコードを取得します。

        :Args:
            - `query (str)`: クエリ条件
            - `is_valid (bool)` : 有効データのフラグ。 Defaults to True

        :Returns:
            - `matched (pd.DataFrame)`: クエリにマッチしたデータフレーム

        :Example:

        ```python
        rm = RunManager("./_data/run.csv")
        rm.get_records("run_id==1")
        rm.get_records("run_type=='古墳'")
        rm.get_records("50 <= run_id <= 84")
        rm.get_records("50 <= run_id <= 84", is_valid=False)
        rm.get_records("50 <= run_id <= 84 and run_type='テスト'")
        ```
        """
        if is_valid:
            matched = self.data.query(query).query("is_valid==True").copy()
        else:
            matched = self.data.query(query).copy()
        return matched

    def _to_rundata(self, row: pd.DataFrame) -> RunData:
        if self.is_test:
            run_data = RunData(run_id=0)
        else:
            run_data = RunData(
                run_id=row.run_id,
                read_from=Path(self.drive) / "raw_data" / row.path_raw_data,
                srcf=row.search_pattern,
                interval=row.resample_interval,
                datetime_offset=row.datetime_offset,
                description=row.overview,
                skip=~row.is_valid,
                raw2gz=Path(self.drive) / "parsed" / row.path_preprocessed_data,
                raw2csv=Path(self.drive) / "parsed" / row.path_resampled_data,
                query=row.query,
            )
        return run_data

    def _get_runs(self, is_valid: bool) -> list[RunData]:
        query = self.query
        matched = self.get_records(query, is_valid)
        runs = []
        for row in matched.itertuples():
            run_data = self._to_rundata(row)
            runs.append(run_data)
        return runs

    def get_run(self, run_id: int) -> RunData:
        """Get RunData.

        ラン番号（`run_id`）を指定して、RunData情報を取得する。

        :raises KeyError:
            - ラン番号が見つからない場合

        """
        for run in self.runs:
            if run.run_id == run_id:
                return run

        msg1 = f"Run #{run_id} is out of range. Quit."
        logger.error(msg1)
        fname = Path(self.drive) / self.load_from
        msg2 = f"Check or Fix configuration file: {fname}."
        logger.warning(msg2)
        raise KeyError(f"{msg1} {msg2}")


if __name__ == "__main__":
    """configモジュールの動作確認用

    $ python3 config.py

    - 設定ファイルの内容がきちんと読み込まれているか確認する
    - Configクラスのインスタンス変数を修正した場合に動作確認する
    - RunDataクラスのインスタンス変数を修正した場合に動作確認する
    """

    c = Config("../sandbox/config.toml")
    ic(c.fname)
    ic(type(c.rules))
    # ic(c.runs)
    # for run in c.runs:
    #     ic(run.name)
    #     ic(run.runid)
    #     ic(run.fnames)
