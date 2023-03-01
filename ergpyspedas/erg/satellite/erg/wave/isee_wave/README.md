# Python版ISEE_Wave プログラム実行手順書

最終更新: 2023/03/01

## 前提事項・諸注意

以降で説明するPythonスクリプトやデータ等のパスは、全て`wave/`を基点とした相対パス表記である

## フォルダ構成

```txt
wave
└── isee_wave
    ├── README.md                       # 本ファイル
    ├── requirements.txt                # 依存ライブラリ一覧
    ├── __init__.py                     # パッケージ化用ファイル
    ├── assets
    │   └── images
    │       └── arase_logo.png          # ロゴの画像ファイル
    ├── isee_wave.py                    # メインプログラム
    ├── load                            # データ入力用
    │   ├── __init__.py
    │   ├── add_fc.py
    │   ├── add_orb.py
    │   ├── erg_search_pwe_wfc_wf.py
    │   ├── orb_predict.py
    │   └── pwe_wfc_info.py
    ├── login                           # ログイン画面
    │   ├── __init__.py
    │   ├── authentication_model.py
    │   ├── login_presenter.py
    │   ├── login_view.py
    │   └── login_view_controller.py
    ├── ofa                             # OFA画面
    │   ├── __init__.py
    │   ├── ofa_view.py
    │   ├── ofa_view_controller.py
    │   └── plot_ofa.py
    ├── options                         # データ構造
    │   ├── __init__.py
    │   └── options.py
    ├── utils                           # 汎用モジュール
    │   ├── __init__.py
    │   ├── colormaps.py
    │   ├── get_uname_passwd.py
    │   └── utils.py
    └── wfc                             # WFC画面
        ├── __init__.py
        ├── erg_calc_pwe_wna.py
        ├── plot_wfc.py
        ├── wfc_view.py
        └── wfc_view_controller.py
```

## 動作確認環境

### OS・ハードウェア

* OS: Windows 10
* CPU: Intel(R) Core(TM) i9-9900KF CPU @ 3.60GHz
* メモリ: 64 GB

### Python環境

* Pythonバージョン: 3.10.9
* 依存ライブラリ: `requirements.txt`を参照

## 実行方法

本プログラムは、PySPEDASのERGモジュールの一機能として作成されている。本プログラムの実行方法には、モジュールとしてインストールせずに実行する方法と、モジュールとしてインストールして実行する方法がある。

### モジュールとしてインストールせずに実行する方法

依存ライブラリは、以下のコマンドでインストールすることができる。

```sh
pip install -r requirements.txt
```

依存ライブラリがインストールされている場合は、現在のディレクトリが`wave/`である状態で以下のコマンドによってプログラムを実行することができる。

```sh
python -m isee_wave.isee_wave
```

### モジュールとしてインストールして実行する方法

本プログラムを含むモジュールは、現時点ではリポジトリ`ergsc-devel/pyspedas_plugin`のブランチ`enh_iseewave`にコミットされている。したがって、以下のコマンドでモジュールとその依存ライブラリをインストールすることができる。

```sh
pip install git+https://github.com/ergsc-devel/pyspedas_plugin.git@enh_iseewave
```

モジュールとしてインストールされている場合は、モジュールとしてインストールせずに実行する方法に加えて、Pythonインタプリタ上で以下のコマンドで実行することができる。インタプリタ上で実行する場合は、現在のディレクトリに制限はない。

```python
from ergpyspedas.erg import isee_wave
isee_wave()
```

### WFC画面について

現時点では、WFC画面は一部未実装である。したがって、時刻をデフォルトにした状態で、現在のディレクトリにIDL版のISEE_Waveで同時刻分をWFC解析して得られた解析結果のtplot変数のファイル(`espec.tplot`、`bspec.tplot`、`wna.tplot`、`polarization.tplot`、`planarity.tplot`、`poyntingvec.tplot`)が格納されている場合のみ、ボタン`Start calculation`を押下すると、WFC解析を行う代わりにその結果を読み取ることで、WFCプロットを行うことができる。WFCプロットを行うことができれば、プロットの調整機能や出力機能を使用することができる。

ファイルが存在しない場合、以下のようなエラーメッセージがコンソールに表示されるはずである。

```
FileNotFoundError: Dummy data files does not exist
```

以上