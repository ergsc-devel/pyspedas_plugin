## 移植対象 / script to be ported:
erg_load_pwe_ofa.pro 

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
- 

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_pwe_ofa_l2_spec_E_spectra_132
  - sample command: timespan, '2017-03-27' & erg_load_pwe_ofa, level='l2', datatype='spec'
  - ylim, 32e-3, 20., 1
  - zlim, 1e-9, 1e-2, 1
  - no_interp=1 
  - datagap=8.
  - ytitle='ERG PWE/OFA-SPEC (E)'
  - ztitle='mV^2/m^2/Hz'
  - ztickunits='scientific'
- erg_pwe_ofa_l2_spec_B_spectra_132
  - ylim, 32e-3, 20., 1
  - zlim, 1e-4, 1e2, 1  
  - no_interp=1 
  - datagap=8.
  - ytitle='ERG PWE/OFA-SPEC (B)'
  - ztitle='pT^2/Hz'
  - ztickunits='scientific'

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_pwe_ofa_l2_spec_E_spectra_132, erg_pwe_ofa_l2_spec_B_spectra_132
  - timespan, '2017-03-27' & erg_load_pwe_ofa, level='l2', datatype='spec' 
  - tplot, [ 'erg_pwe_ofa_l2_spec_E_spectra_132', 'erg_pwe_ofa_l2_spec_B_spectra_132' ] 

  ![plot example](/doc/imgs/ofa_l2_spec_eb_plot.png) 

  