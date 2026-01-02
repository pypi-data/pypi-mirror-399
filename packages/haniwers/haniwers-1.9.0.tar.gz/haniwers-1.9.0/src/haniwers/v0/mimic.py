"""
擬似イベントを生成するモジュール

```python
from haniwers import mimic

# ジェネレーターとして使う例
for fe in mimic.fake_events_generator(n=100, seed=None, interval="random"):
    # FakeEventオブジェクトを処理する
    print(fe.timestamp)


# 擬似イベントのデータフレームを取得する例
fake_data = mimic.fake_events(100)
```
"""

import random
import time

import pandas as pd
import pendulum

from .daq import RealEvent


class FakeEvent(RealEvent):
    """擬似イベント用のクラス"""

    seed: int | None = None
    """乱数シード。デフォルト値は`None`"""
    is_fake: bool = True
    """データ種類のフラグ。FakeEventオブジェクトは常に``True``に設定"""

    def model_post_init(self, __context) -> None:
        """メンバー変数を初期化する"""
        random.seed(self.seed)
        self.timestamp = pendulum.now()
        self.top = random.randint(0, 10)
        self.mid = random.randint(0, 10)
        self.btm = random.randint(0, 10)
        self.tmp = random.gauss(mu=25.0, sigma=3) + random.gauss()
        self.atm = random.gauss(mu=101000, sigma=1000) + random.gauss()
        self.hmd = random.gauss(mu=50, sigma=15) + random.gauss()

        if self.top > 0:
            self.adc = random.randint(1, 1024)

    def to_mock_string(self) -> str:
        """モックしたデータ列

        時刻が入ってないスペース区切りの文字列

        :Example:

        ```
        top mid btm adc tmp atm hmd
        ```
        """
        values_ = self.to_list_string()[1:]
        mock_string = (" ").join(values_)
        return mock_string


def fake_events_generator(n: int, seed: int | None = None, interval: str | int = "random"):
    """FakeEventを生成

    `FakeEvent`を`n`回生成します。
    `interval`でイベントごとの生成間隔を変更できます。
    実際のデータ取得を模擬するため、`interval="random"`を指定できます。

    :Args:
        - `n (int)`: イベント数
        - `seed (int | None)` : 乱数シード。デフォルトは `None`
        - `interval (int | str)` : 生成する間隔。デフォルトは "random"

    :Yield:
        - `FakeEvent`: 擬似イベント

    :Example:

    ```python
    for fe in fake_events_generator(n=100, seed=None, interval="random"):
        e = fe.model_dump()
        print(e)
    ```

    """
    for _ in range(n):
        yield FakeEvent(seed=seed)
        if isinstance(interval, int):
            time.sleep(interval)
        elif interval in ("random"):
            r = random.randint(1, 5)
            time.sleep(r)


def fake_events(n: int) -> pd.DataFrame:
    """FakeEventのデータフレームを作成

    :Note:
        - `seed=None`、`interval=0`で`fake_events_generator`を実行
        - 結果を`pd.DataFrame`に変換

    :Args:
        - `n (int)`: 生成するFakeEventの数

    :Returns:
        - `data (pd.DataFrame)`: 擬似イベントのデータフレーム

    :Example:

    ```python
    events = fake_events(100)
    events.info()
    ```

    """
    events = []
    for fe in fake_events_generator(n, seed=None, interval=0):
        e = fe.model_dump()
        events.append(e)
    data = pd.DataFrame(events)
    return data
