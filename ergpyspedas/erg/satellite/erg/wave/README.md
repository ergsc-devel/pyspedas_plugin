# Python版ISEE_Wave プログラム実行手順書

最終更新: 2023/03/30

## 前提事項・諸注意

以降で説明するPythonスクリプトやデータ等のパスは、全て`wave/`を基点とした相対パス表記である

## フォルダ構成

```txt
wave
├── README.md                           # 本ファイル
├── requirements.txt                    # 依存ライブラリ一覧
├── MANIFEST.in                         # パッケージに含めるデータの情報
├── setup.py                            # インストール用スクリプト
└── isee_wave
    ├── __init__.py                     # パッケージ化用ファイル
    ├── __version__.py                  # バージョンを記したファイル
    ├── assets
    │   └── images
    │       └── arase_logo.png          # ロゴの画像ファイル
    ├── isee_wave.py                    # メインプログラム
    ├── load
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   ├── orb_predict.py              # orb(predict)データをロードする関数
    │   └── pwe_wfc_info.py             # pwe_wfc(info)データをロードする関数
    ├── login
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   ├── authentication_model.py     # ユーザー認証を行うクラス
    │   ├── login_presenter.py          # ログイン画面の描画ロジックを担うクラス
    │   ├── login_view.py               # ログイン画面の描画要素のクラス
    │   └── login_view_controller.py    # ログイン画面を実際に描画するクラス
    ├── ofa
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   ├── add_orb.py                  # orbデータを追加する関数
    │   ├── load_ofa.py                 # OFAデータをまとめてロードする関数
    │   ├── ofa_view.py                 # OFA画面の描画要素のクラス
    │   ├── ofa_view_controller.py      # OFA画面を実際に描画するクラス
    │   └── plot_ofa.py                 # OFAプロットを行う関数
    ├── options
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   ├── data_option.py              # WFC解析結果データの設定
    │   ├── ofa_view_option.py          # OFA画面の設定
    │   ├── orbital_info_option.py      # 軌道の情報の設定
    │   ├── support_line_option.py      # 支持線の情報の設定
    │   └── wfc_view_option.py          # WFC画面の設定
    ├── plot
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   └── common.py                   # tplot関数の拡張版
    ├── utils
    │   ├── __init__.py                 # パッケージ化用ファイル
    │   ├── colormaps.py                # カラーマップを定義するモジュール
    │   ├── get_uname_passwd.py         # ユーザー名とパスワードを取得する関数
    │   ├── progress_manager.py         # プログレスダイアログ
    │   ├── utils.py                    # 汎用的な関数をまとめたモジュール
    │   └── widgets.py                  # PySideの汎用的なウィジェット
    └── wfc
        ├── __init__.py                 # パッケージ化用ファイル
        ├── add_fc.py                   # fcデータを追加する関数
        ├── erg_calc_pwe_wna.py         # WFC解析を行う関数
        ├── load_wfc.py                 # WFCデータをまとめてロードする関数
        ├── mask.py                     # マスク処理を扱うクラス
        ├── plot_wfc.py                 # WFCプロットを行う関数
        ├── erg_search_pwe_wfc_wf.py    # pwe_wfc_wfデータをロードする関数
        ├── wfc_view.py                 # WFC画面の描画要素のクラス
        └── wfc_view_controller.py      # WFC画面を実際に描画するクラス
```

## 動作確認環境

### OS・ハードウェア

* OS: Windows 11 Home
* CPU: 11th Gen Intel(R) Core(TM) i9-11980HK @ 2.60GHz
* メモリ: 64 GB

### Python環境

* Pythonバージョン: `3.8.10`
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

以上