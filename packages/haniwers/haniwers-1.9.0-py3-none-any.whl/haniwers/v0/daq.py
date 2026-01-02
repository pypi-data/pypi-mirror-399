import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pendulum
import serial
from deprecated import deprecated
from loguru import logger
from pydantic import BaseModel
from tqdm import tqdm
from typing import TextIO, Generator
import time

from .config import Daq
from .preprocess import add_hit, add_hit_type


class RealEvent(BaseModel):
    """実イベント

    OSECHIに接続したUSBポートから、シリアル通信で受け取った値を格納するためのデータクラス。
    ファイルに書き出したり、`pandas.DataFrame`に変換できるように自作メソッドを追加。

    """

    timestamp: datetime = pendulum.now()
    """測定時刻。宇宙線イベントが通過した日時。タイムゾーン付きの日付オブジェクト"""
    top: int = 0
    """topレイヤーのヒット。0 - 10の値"""
    mid: int = 0
    """midレイヤーのヒット。0 - 10の値"""
    btm: int = 0
    """btmレイヤーのヒット。0 - 10の値"""
    adc: int = 0
    """topレイヤーにヒットがあったときのADC値。0 - 1023の値"""
    tmp: float = 0.0
    """BME280で測定した気温。[degC]"""
    atm: float = 0.0
    """BME280で測定した気圧。[Pa]"""
    hmd: float = 0.0
    """BME280で測定した湿度。[%]"""

    def to_list_string(self) -> list[str]:
        """メンバー変数を文字列にしたリストに変換

        :Returns:
            list (str): データ文字列のリスト

        ```python
        >>> real_data = RealEvent()
        >>> read_data.to_list_string()
        ['2024-05-21 08:44:20.389786+09:00', '0', '0', '0', '0', '0', '0', '0']
        ```

        """
        data = self.model_dump()
        values = [str(v) for v in data.values()]
        return values

    def to_csv_string(self) -> str:
        """Comma Separated Values

        メンバー変数をCSV形式（カンマ区切り）の文字列に変換します。
        OSECHIから受け取ったデータを、ファイルに保存する際に使うことを想定したメソッドです。

        :Returns:
            str: CSV形式の文字列

        ```python
        >>> real_data = RealEvent()
        >>> real_data.to_csv_string()
        '2024-05-21 08:44:20.389786+09:00,0,0,0,0,0,0,0'
        ```

        """
        data = self.model_dump().values()
        values = [str(v) for v in data]
        csv_string = (",").join(values)
        return csv_string

    def to_tsv_string(self) -> str:
        """Tab Separated Values

        メンバー変数をTSV形式（タブ区切り）の文字列に変換します。

        :Returns:
            str: TSV形式の文字列

        ```python
        >>> real_data = RealEvent()
        >>> real_data.to_tsv_string()
        '2024-05-21 08:44:20.389786+09:00\t0\t0\t0\t0\t0\t0\t0'
        ```

        """
        data = self.model_dump().values()
        values = [str(v) for v in data]
        tsv_string = ("\t").join(values)
        return tsv_string

    def to_ltsv_string(self) -> str:
        """Labeled Tab-Separated Values

        メンバー変数をLTSV形式（ラベルありのタブ区切り）の文字列に変換します。

        :Returns:
            str: LTSV形式の文字列

        ```python
        >>> real_data = RealEvent()
        >>> real_data.to_ltsv_string()
        'timestamp:2024-05-21 08:44:20.389786+09:00\ttop:0\tmid:0\tbtm:0\tadc:0\ttmp:0\tatm:0\thmd:0'
        ```
        """
        data = self.model_dump().items()
        values = [f"{k}:{v}" for k, v in data]
        ltsv_string = ("\t").join(values)
        return ltsv_string


@deprecated(version="0.15.0", reason="Use mkdir_saved")
def init_saved(daq: Daq) -> None:
    """（削除予定）"""
    logger.warning("Deprecated since 0.15.0: Use mkdir_saved")
    return mkdir_saved(daq)


def mkdir_saved(daq: Daq) -> None:
    """データを保存するディレクトリを作成

    データを保存するディレクトリを初期化します。
    ディレクトリが存在しない場合は、新しく作成します。
    ディレクトリが存在する場合は、そのままにします。

    :Args:
        - daq(Daq): DAQ設定オブジェクト

    :Returns:
        - None
    """

    p = Path(daq.saved)
    p.mkdir(exist_ok=True)
    msg = f"Save files in : {p}"
    logger.info(msg)

    return


def get_savef(args: Daq, fid: int | str) -> Path:
    """（削除予定）データを保存するファイル名を生成する

    保存するファイル名を生成します。
    DAQ設定の接頭辞（``prefix``）と拡張子（``suffix``）の値を使って
    ``{prefix}_{連番:06}.{suffix}``の形式で生成します。

    :Args:
    - args(Daq): DAQ設定オブジェクト
        - prefix: ファイルの接頭辞
        - suffix: ファイルの拡張子
    - n(int): ファイル番号

    :Example:
    ```console
    osechi_data_000000.csv
    osechi_data_000001.csv
    osechi_data_000002.csv
    ```

    """
    stem = f"{args.prefix}_{fid:07}"
    fname = Path(stem).with_suffix(args.suffix)
    savef = Path(args.saved, fname)

    msg = "deprecation warning: use get_savef_with_timestamp instaed."
    logger.warning(msg)

    return savef


def get_savef_with_timestamp(args: Daq, fid: int | str) -> Path:
    """データを保存するファイル名を生成する（時刻付き）

    作成日を含んだファイル名を生成する。
    ファイル名は、DAQ設定の接頭辞（``prefix``）、ファイルを開いた時刻（``pendulum.now``）と
    拡張子（``suffix``）の値を使って生成する。

    時刻のフォーマットは、ファイル名が分かりやすいように独自フォーマットにした。

    :Args:
        - `args (Daq)`: Daqオブジェクト
        - `fid (int|str)`: ファイル識別子

    :Returns:
        - `savef (Path)`: ファイル名（Pathオブジェクト）

    :Examples:

    ファイル数の上限を指定して、Pathオブジェクトを生成

    ```console
    max_files = 100
    for nfile in range(max_files):
        savef = get_savef_with_timestamp(daq, nfile)
        # savefを使ったファイル処理
    ```

    :Examples:

    DAQを走らせると生成されるファイル名のサンプル

    ```console
    20240520/osechi_data_2024-05-20T12h34m56s_000000.csv
    20240520/osechi_data_2024-05-20T13h53m24s_000001.csv
    20240520/osechi_data_2024-05-20T14h46m23s_000000.csv  // DAQを走らせ直すとリセット
    20240520/osechi_data_2024-05-20T14h36m32s_000001.csv
    ```

    """
    ts = pendulum.now().format("YYYY-MM-DDTHH[h]mm[m]ss[s]")
    # fidはintもしくはstrなので 07 とした
    # 07d だとstrのときにエラーがでる
    stem = f"{args.prefix}_{ts}_{fid:07}"
    fname = Path(stem).with_suffix(args.suffix)
    savef = Path(args.saved, fname)
    return savef


def open_serial_connection(daq: Daq) -> serial.Serial:
    """シリアル通信を開始する

    シリアル通信（UART）に使うポートを準備します。
    ``with``構文で使う想定です。

    通信に使うUSBポート名（``device``）、
    ボーレート（``baudrate``）、
    通信開始／書き込みのタイムアウト秒（``timeout``）は
    DAQ用の設定ファイルで変更できるようにしてあります。

    :Args:
        - `daq (Daq)`: DAQ設定オブジェクト
            - `device`: USBポート名
            - `baudrate`: ボーレート（通信速度）[bps]
            - `timeout`: タイムアウト秒 [sec]

    :Returns:
        - `port (serial.Serial)`: 通信を開始したSerialオブジェクト

    :Example:

    ```python
    with open_serial_connection(daq) as port:
        # データ測定の処理
        success = write_vth(port, ch, vth)
    ```

    """
    port = serial.Serial(
        daq.device,
        baudrate=daq.baudrate,
        timeout=daq.timeout,
        write_timeout=daq.timeout,
    )
    port.rts = False
    port.dtr = False

    # logger.debug(f"Port opened: {port}")

    return port


def write_vth(port: serial.Serial, ch: int, vth: int) -> bool:
    """Write threshold to individual channel.

    シリアル通信（UART）を使って、チャンネルに閾値を書き込みます。
    ESP32のバッファサイズの制限から、閾値は2回に分割して転送しています。

    - ``val1`` は vth を右に6ビットシフト（=64で割る）して、head を足した値
    - ``val2`` は vth を左に2ビットシフト（=4をかける）して、下位8ビットを取り出した値

    詳細はこの関数のソースコードを確認してください。

    閾値を書き込んだあとに、値が読み出せるかを確認します。
    レスポンスは以下の2つの形式に対応しています：

    - JSON形式: ``{"type":"response","status":"ok"/"error","channel":ch,...}``
    - レガシー形式: ``dame`` （失敗） または チャンネル番号 ``1`` / ``2`` / ``3`` （成功）

    :Args:
        - `port (serial.Serial)`: 接続ポート（Serialオブジェクト）
        - `ch (int)`: 閾値を設定するチャンネル番号
        - `vth (int)`: 閾値

    :Returns:
        - `success (bool)`: 閾値を書き込んだ結果

    :Examples:

    チャンネルごとに閾値を設定

    ```python
    success = write_vth(port, 1, 270)
    success = write_vth(port, 2, 281)
    success = write_vth(port, 3, 297)
    ```

    :TODO:
        ユーザーが直接あつかわない関数でよいので、
        内部変数（の命名規則）に変更する（write_vth -> _write_vth）

    """
    val = vth
    head = 0b10000
    val1 = head + (val >> 6)
    val2 = (val << 2) & 0xFF

    logger.debug(f"Write: ch = {ch}")
    logger.debug(f"Write: val1 = {val1:b}")
    logger.debug(f"Write: val2 = {val2:b}")

    port.write(ch.to_bytes(1, "big"))
    port.write(val1.to_bytes(1, "big"))
    port.write(val2.to_bytes(1, "big"))
    port.write(b"\n")

    read0 = port.readline().decode("utf-8", "ignore").strip()
    read1 = port.readline().decode("utf-8", "ignore").strip()
    read2 = port.readline().decode("utf-8", "ignore").strip()

    # スレッショルド設定の読み出しに必要な休憩時間
    # 0.01秒、0.05秒は効果がなく、0.1秒がちょうどよい
    time.sleep(0.1)

    logger.debug(f"Read: ch = {read0}")
    logger.debug(f"Read: val1 = {read1}")
    logger.debug(f"Read: val2 = {read2}")

    success = False

    # Try to parse as JSON (new format)
    if read0.startswith("{"):
        try:
            response_json = json.loads(read0)
            if response_json.get("type") == "response":
                status = response_json.get("status")
                response_ch = response_json.get("channel")

                if status == "ok" and response_ch == ch:
                    success = True
                    msg = f"Ch{ch}: Set threshold to {vth}."
                    logger.success(msg)
                elif status == "error":
                    success = False
                    msg = f"Ch{ch}: Set threshold failed. Try again."
                    logger.warning(msg)
                else:
                    success = False
                    msg = f"Ch{ch}: Unexpected JSON response: {read0}"
                    logger.warning(msg)
                return success
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse JSON response: {read0}")
            # Fall through to legacy format handling

    # Check legacy format
    if read0 == "dame":
        success = False
        msg = f"Ch{ch}: Set threshold failed. Try again."
        logger.warning(msg)
    elif read0 == str(ch):
        success = True
        msg = f"Ch{ch}: Set threshold to {vth}."
        logger.success(msg)
    else:
        success = True
        msg = f"Ch{ch}: Set threshold to {vth}. Maybe."
        logger.success(msg)
    return success


def set_vth(daq: Daq, ch: int, vth: int) -> bool:
    """Set threshold to individual channel.

    シリアル通信を開始し、チャンネル番号を指定して閾値を設定します。
    チャンネル番号は1 - 3 の範囲で指定してください。
    閾値は1 - 1023 の範囲で指定してください。

    書き込みに成功すると ``success=True`` を返します。
    書き込みに失敗した場合は、警告メッセージを表示します。
    このとき、設定済みの閾値はそのままになります。

    :Args:
        - `daq (Daq)`: DAQ設定オブジェクト
        - `ch (int)`: チャンネル番号。`1 - 3`の範囲で指定してください
        - `vth (int)`: 閾値の値。`1 - 1023` の範囲で指定してください

    :Returns:
        - `success (bool)`: 閾値を書き込んだ結果

    :Exceptions:
        - チャンネル番号が範囲外の場合は終了
        - 閾値が範囲外の場合は終了
        - `serial.SerialException`: シリアル通信ができなかった場合は終了
        - `Exception`: その他の予期せぬエラーの場合も終了

    :Examples:

    ```python
    success = set_vth(daq, 1, 280)
    success = set_vth(daq, 2, 280)
    success = set_vth(daq, 4, 280)  # チャンネル番号が範囲外
    success = set_vth(daq, 1, 2000) # 閾値が範囲外
    ```

    """

    # check values
    if ch not in range(1, 4):
        msg = f"value of ch is out of range: {ch}"
        logger.error(msg)
        sys.exit()

    if vth not in range(1, 1024):
        msg = f"value of vth is out of range: {vth}"
        logger.error(msg)
        sys.exit()

    mkdir_saved(daq)

    try:
        with open_serial_connection(daq) as port:
            success = write_vth(port, ch, vth)
            fname = Path(daq.saved) / daq.fname_logs

            with fname.open("a", newline="") as f:
                now = pendulum.now().to_iso8601_string()
                row = [str(now), str(ch), str(vth), str(success)]
                writer = csv.writer(f)
                writer.writerow(row)
            msg = f"Saved data to {fname}."
            logger.info(msg)
        return success
    except serial.SerialException as e:
        logger.error(e)
        msg = """Could not open the port. Device name might be wrong.
        Run 'arduino-cli board list' and check the device name.
        Edit 'daq.toml' if you needed.
        """
        logger.warning(msg)
        sys.exit()
    except Exception as e:  # noqa
        logger.error(e)
        msg = """
        Unaware error occurred.
        Please think if you need to handle this error.
        """
        sys.exit()


def set_vth_retry(daq: Daq, ch: int, vth: int, max_retry: int) -> bool:
    """Set threshold with retries

    閾値の書き込みに失敗した場合、成功するまで ``max_retry``回繰り返します。

    :Args:
        - `daq (Daq)`: Daqオブジェクト
        - `ch (int)`: チャンネル番号
        - `vth (int)`: スレッショルド値
        - `max_retry (int)`: リトライする最大回数

    :Returns:
        - `success (bool)`: 閾値を書き込んだ結果

    :Examples:

    ```python
    # 5回繰り返す
    success = set_vth_retry(daq, 1, 280, 5)
    # 10回繰り返す
    success = set_vth_retry(daq, 2, 290, 10)
    ```

    """

    for i in range(max_retry):
        success = set_vth(daq, ch, vth)
        if success:
            return True
        msg = f"Retry: {i} / {max_retry} times."
        logger.warning(msg)

    return False


def _read_event(port: serial.Serial) -> RealEvent:
    """Read single event from the opened port.

    シリアル接続しているポートから1イベント分のデータを読み出します。
    引数に指定するポートは、接続済みのポートを渡してください。
    読み出したデータは適切な型に変換して、`RealEvent`オブジェクトに代入します。

    :Note:
        - ``run_daq``や``time_daq``でデータを取得するために使います。

    :Args:
        - `port (serial.Serial)`: 接続済みのSerialオブジェクト

    :Returns:
        - `event (RealEvent)`: 1イベント分のデータ。読み出した時刻も自動で追加される。

    :Examples:

    ```python
    with open_serial_connection() as port:
        event = _read_event(port)
    print(event)
    # [pendulum.now(), top, mid, btm, adc, tmp, atm, hmd]
    ```

    """
    # logger.debug("[_read_event]")
    data = port.readline().decode("UTF-8").strip().split()
    if len(data) == 0:
        msg = f"No data to readout. Timed-out: {port.timeout}"
        logger.warning(msg)
    event = RealEvent()
    event.timestamp = pendulum.now()
    event.top = int(data[0])
    event.mid = int(data[1])
    event.btm = int(data[2])
    event.adc = int(data[3])
    event.tmp = float(data[4])
    event.atm = float(data[5])
    event.hmd = float(data[6])
    return event


def _loop_events_for_rows(port: serial.Serial, max_rows: int) -> Generator[RealEvent, None, None]:
    """イベント取得ループ（回数指定）

    測定回数を指定してデータを読み出します。
    ジェネレーター関数になっています。

    :Args:
        - `port (serial.Serial)`: 接続済みのSerialオブジェクト
        - `max_rows (int)`: 測定回数

    :Yields:
    - `event (RealEvent)`: 1イベント分の測定データ（RealEventオブジェクト）

    :Example:

    ```python
    # 100回測定する
    for event in _loop_events_for_rows(port, 100):
        print(event.to_ltsv_string())
    ```

    """
    rows = range(max_rows)
    for _ in tqdm(rows, leave=False, desc="loops"):
        event = _read_event(port)
        yield event


def _loop_events_for_duration(
    port: serial.Serial, max_duration: int
) -> Generator[RealEvent, None, None]:
    """イベント取得ループ（時間指定）

    測定時間を指定してデータを読み出します。
    ジェネレーター関数になっています。

    :Args:
        - `port (serial.Serial)`: 接続済みのSerialオブジェクト
        - `max_duration (int)`: 測定時間（秒）

    :Yields:
        - `event (RealEvent)`: 1イベント分の測定データ（RealEventオブジェクト）

    :Example:

    ```python
    # 10秒間測定する
    for event in _loop_events_for_rows(port, 10):
        print(event.to_ltsv_string())
    ```

    """
    # 終了時刻を計算する
    started = pendulum.now()
    stop = started.add(seconds=max_duration)

    logger.debug(f"- DAQ started at: {started}")
    logger.debug(f"- DAQ stops at  : {stop}")

    while pendulum.now() < stop:
        event = _read_event(port)
        yield event

    stopped = pendulum.now()
    diff = stopped - started
    elapsed_time = diff.in_seconds()
    logger.debug(f"- DAQ stopped at: {stopped} / Elapsed: {elapsed_time} sec.")


def loop_and_save(fname: Path, generator: Generator) -> list[RealEvent]:
    """イベント保存ループ

    指定したファイルに、1イベントずつファイルに書き足して保存します。

    保存形式はファイル名の拡張子で判定します。
    有効な拡張子は``[".csv", ".dat", ".tsv", ".json", ".jsonl"]``です。

    イベントの取得方法は``generator``で指定します。
    有効なジェネレーターは``_loop_events_for_rows``と``_loop_events_for_duration``です。

    :Args:
        - `fname (Path)`: データを追記するファイル名
        - `generator (Generator)`: データの取得方法。[``_loop_events_for_rows``, ``_loop_events_for_duration``]から選択。

    :Returns:
        - `events (list[RealEvent])`: 測定したデータのリスト

    """
    # ファイル名から拡張子を取得する
    suffix = fname.suffix

    events = []
    with fname.open("x") as f:
        for event in generator:
            events.append(event)
            if suffix in [".csv"]:
                row = event.to_csv_string()
                f.write(row + "\n")
            if suffix in [".dat", ".tsv"]:
                row = event.to_tsv_string()
                f.write(row + "\n")
            if suffix in [".json", ".jsonl"]:
                row = event.model_dump_json()
                f.write(row + "\n")
            f.flush()
    return events


def events_to_dataframe(events: list[RealEvent]) -> pd.DataFrame:
    """測定データをデータフレームに変換する

    測定データは、データを取得するたびにファイルに書き出してますが、
    同時にRealEventオブジェクトのリストとしてもストアしています。
    このままだと使いにくいので、データフレームに変換できるようにしました。
    そのときに、``preprocess.add_hit``と``preprocess.add_hit_type``の処理もしています。
    測定時刻の調整やリサンプル処理はしていません。

    :Args:
    - `events (list[RealEvent])`: 測定データ（RealEventオブジェクト）のリスト

    :Returns:
    - `data (pd.DataFrame)`: 測定データのデータフレーム

    :Notes:
    """
    rows = []
    for event in events:
        row = event.model_dump()
        rows.append(row)
    data = pd.DataFrame(rows)
    # hit_top / hit_mid / hit_btm を追加
    data = add_hit(data)
    # hit_type を追加
    data = add_hit_type(data)
    return data


def run_daq(port: serial.Serial, daq: Daq) -> None:
    """Run DAQ（回数指定）

    OSECHIを接続したUSBポートとシリアル通信をして、データ取得する。
    指定したファイル数と行数をでループ処理する。

    :Args:
        - `port (serial.Serial)`: 接続するポート（Serialオブジェクト）
        - `daq (Daq)`: 設定（Daqオブジェクト）

    :Returns:
        - `None`: 測定時間が長くなると、メモリリークするかもしれないため、
        1イベントのデータをファイルに書き出したあとは潔く破棄している

    :Example:

    ```python
    run_daq(port, daq)
    ```

    """
    mkdir_saved(daq)
    max_files = daq.max_files
    for nfile in tqdm(range(max_files), desc="files"):
        savef = get_savef_with_timestamp(daq, nfile)
        msg = f"Saving data to: {savef}."
        logger.info(msg)
        logger.info("Press Ctrl-c to stop.")
        loop_and_save(
            fname=savef,
            generator=_loop_events_for_rows(port=port, max_rows=daq.max_rows),
        )
        msg = f"Saved data to: {savef}."
        logger.success(msg)


def scan_daq(args: Daq, fname: str, duration: int) -> pd.DataFrame:
    """Run DAQ（時間指定）

    1回のランあたりの測定時間を指定してデータを取得する。
    スレッショルド測定するために作ったDAQ関数です。

    :Args:
        - `args (Daq)`: Daqオブジェクト
        - `duration (int)`: 測定時間を秒で指定

    :Returns:
        - `data (pd.DataFrame)`: 測定結果のデータフレーム。
        データフレームを次の処理に渡したいため。

    :Example:

    ```python
    data = scan_daq(daq, fname, duration)
    ```
    """

    with open_serial_connection(args) as port:
        logger.debug(f"Port opened : {port.name}")
        events = loop_and_save(
            fname=Path(fname),
            generator=_loop_events_for_duration(port=port, max_duration=duration),
        )
        msg = f"Saved data to: {fname}."
        logger.success(msg)

    logger.debug(f"Port closed : {port.name}")
    return events


def run(port: serial.Serial, args: Daq):
    """メインのDAQ

    run_daqのラッパー。例外処理などで囲んだもの。

    :versionadded: `0.6.0`.
    """

    try:
        run_daq(port, args)
    except serial.SerialException as e:
        logger.error(e)
        msg = """Could not open the port. Device name might be wrong.
        Run 'arduino-cli board list' and check the device name.
        Edit 'daq.toml' if you needed.
        """
        logger.warning(msg)
        sys.exit()
    except KeyboardInterrupt as e:
        logger.warning(e)
        msg = """Quit."""
        logger.info(msg)
        sys.exit()
    except Exception as e:  # noqa
        logger.error(e)
        msg = """Exit.
        Unaware error occurred.
        Please think if you need to handle this error.
        """
        logger.error(msg)
        sys.exit()


"""削除予定の関数"""


@deprecated(version="0.15.3", reason="Will be deprecated. Use scan_daq instead.")
def time_daq(args: Daq, duration: int) -> pd.DataFrame:
    """（削除予定）測定時間を指定してDAQを走らせます。

    :Args:
    - args (Daq): Daqオブジェクト
    - duration (int): 測定時間を秒で指定

    :Returns:
    - data (pd.DataFrame): 測定結果のデータフレーム
    """

    rows = []
    with open_serial_connection(args) as port:
        mkdir_saved(args)

        logger.debug("Port opened.")
        daq_start = pendulum.now()
        daq_stop = daq_start.add(seconds=duration)

        logger.debug(f"- DAQ Started: {daq_start}")
        logger.debug(f"- DAQ Stop   : {daq_stop}")

        while pendulum.now() < daq_stop:
            row = read_serial_data(port)
            event = RealEvent()
            event.timestamp = pendulum.now()
            event.top = int(row[1])
            event.mid = int(row[2])
            event.btm = int(row[3])
            event.adc = int(row[4])
            event.tmp = float(row[5])
            event.atm = float(row[6])
            event.hmd = float(row[7])
            rows.append(event.model_dump())
    daq_end = pendulum.now()
    diff = daq_end - daq_start
    elapsed_time = diff.in_seconds()
    logger.debug(f"- DAQ Closed : {daq_end} / Elapsed: {elapsed_time} sec.")
    data = pd.DataFrame(rows)
    return data


@deprecated(
    version="0.14.0",
    reason="Will be deprecated. Use threshold.scan_threshold_by_channel instead.",
)
def scan_ch_vth(daq: Daq, duration: int, ch: int, vth: int) -> list:
    """（削除予定）Run threshold scan.

    :Args:
    - daq (Daq): Daqオブジェクト
    - duration (int): 測定時間（秒）
    - ch (int): 測定するチャンネル番号
    - vth (int): スレッショルド値

    :Returns:
    - data (list): [測定時刻、チャンネル番号、スレッショルド値、イベント数]のリストを返します。
    """

    logger.warning("Will be deprecated. Please use threshold.scan_by_channel instead.")

    # Try to set the threshold
    if not set_vth_retry(daq, ch, vth, 3):
        msg = f"Failed to set threshold: ch{ch} - {vth}"
        logger.error(msg)
        return []

    # Collect data
    try:
        rows = time_daq(daq, duration)
        counts = len(rows)
        tmp = rows["tmp"].mean()
        atm = rows["atm"].mean()
        hmd = rows["hmd"].mean()
        fname = get_savef_with_timestamp(daq, ch)
        rows.to_csv(fname, index=False)
        msg = f"Saved data to: {fname}"
        logger.info(msg)
    except Exception as e:
        msg = f"Failed to collect data due to: {str(e)}"
        logger.error(msg)
        counts = 0
        tmp = 0
        atm = 0
        hmd = 0

    # Save Summary
    now = pendulum.now().to_iso8601_string()
    data = [now, duration, ch, vth, counts, tmp, atm, hmd]
    fname = Path(daq.saved) / daq.fname_scan
    with fname.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)
    msg = f"Added data to: {fname}"
    logger.info(msg)

    return data


@deprecated(
    version="0.14.0",
    reason="Will be deprecated. Use threshold.scan_thresholds instead.",
)
def scan_ch_thresholds(daq: Daq, duration: int, ch: int, thresholds: list[int]) -> list[list]:
    """（削除予定）Run threshold scan.

    :Args:
    - daq (Daq): Daqオブジェクト
    - duration (int): 測定時間（秒）
    - ch (int): チャンネル番号
    - thresholds (list[int]): スレッショルド値のリスト

    :Returns:
    - rows (list[list]): [測定時刻、チャンネル番号、スレッショルド値、イベント数]のリスト
    """

    logger.warning("Will be deprecated. Please use threshold.scan_thresholds instead.")
    # Estimated time for scan
    msg = f"Number of points: {len(thresholds)}"
    logger.info(msg)
    estimated_time = len(thresholds) * duration
    msg = f"Estimated time: {estimated_time} sec."
    logger.info(msg)

    # すべてのチャンネルの閾値を高くする
    set_vth_retry(daq, 1, 500, 5)
    set_vth_retry(daq, 2, 500, 5)
    set_vth_retry(daq, 3, 500, 5)

    rows = []
    n = len(thresholds)
    for i, vth in enumerate(thresholds):
        msg = "-" * 40 + f"[{i + 1:2d}/{n:2d}: {vth}]"
        logger.info(msg)
        row = scan_ch_vth(daq, duration, ch, vth)
        if row:
            rows.append(row)

    return rows


@deprecated(
    version="0.15.0",
    reason="Will be deprecated. Use _read_event (RealEvent).",
)
def _read_serial_data_as_list(port: serial.Serial) -> list:
    """（削除予定）Read serial data from port.

    OSECHIが接続されているポートからデータを読み出します。
    引数に指定するポートは、あらかじめ開いたものを渡してください。
    ``run_daq``や``time_daq``でデータを取得するために使います。

    :Args:
    - port (serial.Serial): Serialオブジェクト

    :Returns:
    - row (list): 読み出した時刻を追加したデータのリスト

    :Examples:
    ```python
    >>> with open_serial_connection() as port:
    >>>     row = read_serial_data(port)
    >>>     row
    [日付, top, mid, btm, adc, tmp, atm, hmd]
    ```

    """
    msg = "Will be deprecated. Use _read_event."
    logger.warning(msg)
    now = pendulum.now().to_iso8601_string()
    data = port.readline().decode("UTF-8").strip()
    if len(data) == 0:
        msg = f"No data to readout. Timed-out: {port.timeout}"
        logger.warning(msg)
    row = f"{now} {data}".split()
    return row


@deprecated(
    version="0.15.0",
    reason="Will be deprecated. Use _read_event (RealEvent).",
)
def read_serial_data(port: serial.Serial) -> list:
    """（削除予定）"""
    msg = "Will be deprecated. Use _read_event."
    logger.warning(msg)
    data = _read_serial_data_as_list(port)
    return data


@deprecated(version="0.15.3", reason="Will be deprecated. Use loop_and_save instead.")
def _loop_and_save_events(
    fname: Path, port: serial.Serial, max_rows: int, suffix: str = ".csv"
) -> list:
    """（削除予定）イベント保存ループ

    :Args:
    - `f (typing.TextIO)`: 開いたファイルオブジェクト
    - `port (serial.Serial)` : 接続済みのSerialオブジェクト
    - `max_rows (int)`: 1ファイルあたりの行数の最大値
    - `suffix (str)`: ファイルの拡張子

    :Return:
    - `events (list)`: 複数イベントの測定データ

    """
    logger.warning("Will be deprecated. Use loop_and_save instead.")
    events = []
    with fname.open("x") as f:
        for event in _loop_events_for_rows(port, max_rows):
            events.append(event)
            if suffix in [".csv"]:
                row = event.to_csv_string()
                f.write(row + "\n")
            if suffix in [".dat", ".txv"]:
                row = event.to_tsv_string()
                f.write(row + "\n")
            if suffix in [".json", ".jsonl"]:
                row = event.model_dump_json()
                f.write(row + "\n")
            f.flush()
    return events


@deprecated(version="0.15.3", reason="Will be deprecated. Use _loop_and_save_events instead.")
def loop_and_save_events(f: TextIO, daq: Daq, port: serial.Serial) -> list[str]:
    """（削除予定）イベント保存ループ

    :Args:
    - f (TextIO): データを書き込むファイルオブジェクト
    - daq (Daq): Daqオブジェクト
    - port (serial.Serial): 接続済みのSerialオブジェクト

    """
    logger.warning("Will be deprecated. Use _loop_and_save_events instead.")
    rows = daq.max_rows
    events = []
    for event in _loop_events_for_rows(port, max_rows=rows):
        events.append(event.model_dump_json())
        if daq.suffix in [".csv"]:
            row = event.to_csv_string()
            f.write(row + "\n")
        elif daq.suffix in [".dat", ".tsv"]:
            row = event.to_tsv_string()
            f.write(row + "\n")
        elif daq.suffix in [".json", ".jsonl"]:
            row = event.model_dump_json()
            f.write(row + "\n")
        f.flush()
    return events


@deprecated(version="0.15.0", reason="Will be deprecated. Use _loop_and_save_events instead.")
def save_serial_data(f, daq: Daq, port: serial.Serial) -> list:
    """（削除予定）

    :Args:
    - f: ファイルポインタ
    - daq (Daq): Daqオブジェクト
    - port (serial.Serial): Serialオブジェクト

    :Return:
    - rows (list[list]): 取得したデータのリスト

    :TODO:
    - Daqオブジェクトに依存しない関数にしたい（ジェネレーターにするのがいいのかな？）
    - pd.DataFrameを返した方がいいかもしれない？
    """
    logger.warning("Will be deprecated. Use _loop_and_save_events instead.")
    max_rows = daq.max_rows
    rows = []
    for _ in tqdm(range(max_rows), leave=False, desc="rows"):
        row = read_serial_data(port)
        rows.append(row)
        if daq.suffix == ".csv":
            writer = csv.writer(f)
            writer.writerow(row)
        else:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow(row)
        f.flush()
    return rows
