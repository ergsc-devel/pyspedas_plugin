## 移植対象 / script to be ported:
erg_load_xep.pro 

## 要移植オプション / necessary options:
### 共通 / common:
- level : "l2"
- datatype : "2dflux", "omniflux"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)
- ror : (boolean)
### スクリプト特有 / script-specific: 


## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_xep_l2_FEDU_SSD
  - sample command: timespan, '2017-04-01' & erg_load_xep, datatype='2dflux'
  - no_interp=1, 
  - tclip, -1.0e+10, 1.0e+10
- erg_xep_l2_FEDO_SSD
  - sample command: timespan, '2017-04-01' & erg_load_xep, datatype='omniflux'
  - ztitle = '[/cm!U2!N-str-s-keV]', spec=1, ystyle=1, 
  - ytitle='XEP!Comniflux!CLv2!CEnergy', ysubtitle='[keV]'
  - zticklen=-0.4, zlog=1, ztickunits='scientific'
  - ylim, 0.01, 25.0, 1
  - zlim, 1e+1, 1e+9, 1

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_XEP_l2_FEDO_SSD
  - timespan, '2017-04-01' & erg_load_xep, datatype='omniflux'
  - tplot,'erg_xep_l2_FEDO_SSD'
 ![plot example](/doc/imgs/xep_l2_fedo.png)

  