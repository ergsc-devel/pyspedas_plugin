# Python版ISEE_Wave　プログラム実行手順書

## 前提事項・諸注意

以降で説明するPythonスクリプトやデータ等のパスは、全て`source/`を基点とした相対パス表記である

## フォルダ構成

```txt
source
├── README.md
│       本ファイル
├── requirements.txt
│       開発した際のライブラリ環境一覧
├── assets
│   └── images
│       └── arase_logo.png
│               ロゴの画像ファイル
├── add_fc.py
│       FCに関するデータのロードを行う関数
├── add_orb.py
│       ORBに関するデータのロードを行う関数
├── authentication_model.py
│       ユーザー認証を行うクラス
├── erg_calc_pwe_wna.py
│       WFC解析ボタン押下時の処理(WFCデータのロードを含む)を行う関数
├── get_uname_passwd.py
│       tplot変数からユーザー名とパスワードを取得する関数
├── isee_wave.py
│       ISEE_Waveプログラムを起動する関数
├── login_presenter.py
│       ログイン画面の描画ロジックを担うクラス
├── login_view.py
│       ログイン画面の描画要素をまとめたクラス
├── login_view_controller.py
│       ログイン画面の描画を実際に行うクラス
├── ofa_view_controller.py
│       OFA画面の描画を実際に行うクラス
├── ofa_view.py
│       OFA画面の描画要素をまとめたクラス
├── orb_predict.py
│       ORB(Predict)のデータのロードを行う関数
├── plot_ofa.py
│       OFAプロットを行う関数
├── plot_wfc.py
│       WFCプロットを行う関数
├── pw_start.py
│       ログイン画面を開く関数
├── pwe_wfc_info.py
│       WFC(Info)データのロードを行う関数
├── utils.py
│       汎用的な関数をまとめたモジュール
└── wfc_options.py
        WFC画面に関するオプションをまとめたモジュール
```

## 動作確認環境

* OS: Windows 10
* CPU: Intel(R) Core(TM) i9-9900KF CPU @ 3.60GHz
* メモリ: 64 GB

## Python環境構築

* Pythonバージョン: 3.10.9
* ライブラリ: `requirements.txt`を参照

ライブラリをインストールするコマンド:

```sh
pip install -r requirements.txt
```

## 実行方法

### ログイン画面の表示

以下のコマンドを実行するとログイン画面が表示される。

```sh
python isee_wave.py
```

IDL版のISEE_Wave同様にログイン画面の操作が可能である。但し、ユーザー/ゲストログインに成功した場合、OFA/WFC画面には遷移せず、ログイン画面が閉じるだけである。

### OFA画面の表示

以下のコマンドを実行するとOFA画面が表示される。

```sh
python ofa_view_controller.py
```

IDL版のISEE_Wave同様にOFA画面の操作が可能である。

### WFCプロットの描画

以下のコマンドを実行するとWFCプロットが表示される。

```sh
python plot_wfc.py
```

但し、現在のディレクトリに、IDL版のISEE_Waveのデフォルトの設定でWFC解析して得られた解析結果のtplot変数のファイル(`espec.tplot`、`bspec.tplot`、`wna.tplot`、`polarization.tplot`、`planarity.tplot`、`poyntingvec.tplot`)が格納されている必要がある。ファイルが存在しない場合、以下のようなエラーメッセージがコンソールに表示されるはずである。

```
FileNotFoundError: Dummy data files does not exist
```

以上