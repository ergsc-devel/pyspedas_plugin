## 移植対象 / script to be ported:
erg_load_pwe_wfc.pro 

## 要移植オプション / necessary options:
### 共通 / common:
- level : "l2"
- datatype : "spec"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)
- ror : (boolean)
### スクリプト特有 / script-specific: 
- coord : 'sgi'
- component : 'all'
- mode : '65khz'
- datatype : ['waveform', 'spec']

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_pwe_wfc_l2_e_65khz_E_spectra
  - ylim, 32., 2e4, 1
  - zlim, 1e-9, 1e-2, 1
  - ysubtitle, '[Hz]'
  - ztitle, '[mV^2/m^2/Hz]'
  - ztickunits='scientific'
- erg_pwe_wfc_l2_e_65khz_B_spectra
  - ylim, 32., 2e4, 1
  - zlim, 1e-4, 1e2, 1
  - ysubtitle, '[Hz]'
  - ztitle, '[pT^2/Hz]'
  - ztickunits='scientific'

- erg_pwe_wfc_l2_e_65khz_Ex_waveform, erg_pwe_wfc_l2_e_65khz_Bx_waveform
  - l.172からl.234までの波形２次元データを１次元に展開するところ
  - l.199 : データが非常に重いので、展開範囲の再確認
  - 時刻データ操作時にtt2000オプションを必ずつけてください。


## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_pwe_wfc_l2_e_65khz_E?_waveform, erg_pwe_wfc_l2_e_65khz_B?_waveform
  - timespan, '2017-04-01/12:57:59.5', 1, /s
  - erg_load_pwe_wfc, level='l2', datatype='waveform' 
  - tplot, [ 'erg_pwe_wfc_l2_e_65khz_E?_waveform', 'erg_pwe_wfc_l2_e_65khz_B?_waveform' ] 
  - tlimit, ['2017-04-01/12:58:00.000', '2017-04-01/12:58:00.001']

  ![plot example](/doc/imgs/wfc_l2_waveform_eb_plot.png) 


- erg_pwe_wfc_l2_e_65khz_E_spectra, erg_pwe_wfc_l2_e_65khz_B_spectra
  - timespan, '2017-04-01/14:04:39', 1, /m
  - erg_load_pwe_wfc, level='l2', datatype='spec' 
  - tplot, [ 'erg_pwe_wfc_l2_e_65khz_E_spectra', 'erg_pwe_wfc_l2_e_65khz_E_spectra' ] 

  ![plot example](/doc/imgs/wfc_l2_spec_eb_plot.png) 
