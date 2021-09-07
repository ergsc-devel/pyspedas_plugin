## 移植対象 / script to be ported:
erg_load_pwe_hfa.pro 

## 要移植オプション / necessary options:
### 共通 / common:
- level : "l2"
- mode : "low", "monit", "high"
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
- erg_pwe_hfa_l2_low_spectra_eu, erg_pwe_hfa_l2_low_spectra_ev, erg_pwe_hfa_l2_low_spectra_esum
  - sample command: timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - ylim, 2.0, 10000.0, 1
  - zlim, 1e-10, 1e-3, 1
  - no_interp=1 
  - datagap=70.
  - ytitle='ERG PWE/HFA (EU)', 'ERG PWE/HFA (EV)', 'ERG PWE/HFA (ESUM)'
  - ztitle='mV^2/m^2/Hz'
  - ztickunits='scientific'

- erg_pwe_hfa_l2_low_spectra_e_ar
  - sample command: timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - ylim, -1, 1, 0
  - zlim, 1e-10, 1e-3, 1
  - no_interp=1 
  - datagap=70.
  - ytitle='ERG PWE/HFA (E_AR)'
  - ztitle='LH:-1/RH:+1'

- erg_pwe_hfa_l2_low_spectra_bgamma
  - sample command: timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - ylim, 2.0, 200.0, 1
  - zlim, 1e-4, 1e2, 1 
  - no_interp=1 
  - datagap=70.
  - ytitle='ERG PWE/HFA (BGAMMA)'
  - ztitle='pT^2/Hz'
  - ztickunits='scientific'

- erg_pwe_hfa_l3_1min_Fuhr
  - sample command: timespan, '2018-09-09' & erg_load_pwe_hfa, level='l3'
  - datagap=60.
  - ytitle='UHR frequency [Mhz]'

- erg_pwe_hfa_l3_1min_ne_mgf
  - sample command: timespan, '2018-09-09' & erg_load_pwe_hfa, level='l3'
  - datagap=60.
  - ytitle='eletctorn density [/cc]'

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_pwe_hfa_l2_low_spectra_eu, erg_pwe_hfa_l2_low_spectra_ev, erg_pwe_hfa_l2_low_spectra_esum
  - timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - tplot, [ 'erg_pwe_hfa_l2_low_spectra_eu', 'erg_pwe_hfa_l2_low_spectra_ev', 'erg_pwe_hfa_l2_low_spectra_esum' ] 

  ![plot example](/doc/imgs/hfa_l2_low_e_plot.png) 

- erg_pwe_hfa_l2_low_spectra_e_ar
  - timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - tplot, [ 'erg_pwe_hfa_l2_low_spectra_e_ar' ] 

  ![plot example](/doc/imgs/hfa_l2_low_ear_plot.png) 
  
- erg_pwe_hfa_l2_low_spectra_bgamma
  - timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - tplot, [ 'erg_pwe_hfa_l2_low_spectra_e_ar' ] 

  ![plot example](/doc/imgs/hfa_l2_low_b_plot.png) 

- erg_pwe_hfa_l3_1min_Fuhr, erg_pwe_hfa_l3_1min_ne_mgf
  - timespan, '2018-09-09' & erg_load_pwe_hfa, level='l2', datatype='low'
  - tplot, [ 'erg_pwe_hfa_l3_1min_Fuhr', 'erg_pwe_hfa_l3_1min_ne_mgf' ] 

  ![plot example](/doc/imgs/hfa_l3_plot.png) 
