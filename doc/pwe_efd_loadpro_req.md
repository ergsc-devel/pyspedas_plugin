## 移植対象 / script to be ported:
erg_load_pwe_efd.pro 

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
- datatype : ['E_spin', 'spec', 'spec', '64Hz', '256Hz', 'pot', 'pot8Hz'] 
- coord : ['wpt', 'dsi'] 

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_pwe_efd_l2_E_spin_Eu_dsi, erg_pwe_efd_l2_E_spin_Ev_dsi
  - labels=['Ex', 'Ey']
  - ytitle=['Ex', 'Ey']+' vector in DSI'
  - constant=0

- erg_pwe_efd_l2_E64Hz_dsi_Ex_waveform, erg_pwe_efd_l2_E64Hz_dsi_Ey_waveform, erg_pwe_efd_l2_E64Hz_wpt_Ex_waveform, erg_pwe_efd_l2_E64Hz_wpt_Ey_waveform, erg_pwe_efd_l2_E256Hz_dsi_Ex_waveform, erg_pwe_efd_l2_E256Hz_dsi_Ey_waveform, erg_pwe_efd_l2_E256Hz_wpt_Ex_waveform, erg_pwe_efd_l2_E256Hz_wpt_Ey_waveform
  - l.224からl.244までの、波形２次元配列を１次元配列へ展開するところ 

- erg_pwe_efd_l2_pot_Vu1
  - ytitle='Vu1 potential'
  - constant=0

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_pwe_efd_l2_E_spin_Eu_dsi, erg_pwe_efd_l2_E_spin_Ev_dsi
  - timespan, '2017-04-01/16:20', 30, /m
  - erg_load_pwe_efd, level='l2', datatype='E_spin'
  - tplot, [ 'erg_pwe_efd_l2_E_spin_Eu_dsi', 'erg_pwe_efd_l2_E_spin_Ev_dsi' ] 

  ![plot example](/doc/imgs/efd_l2_E_spin_plot.png) 

- erg_pwe_efd_l2_E64Hz_dsi_Ex_waveform, erg_pwe_efd_l2_E64Hz_dsi_Ey_waveform, erg_pwe_efd_l2_E64Hz_wpt_Ex_waveform, erg_pwe_efd_l2_E64Hz_wpt_Ey_waveform, erg_pwe_efd_l2_E256Hz_dsi_Ex_waveform, erg_pwe_efd_l2_E256Hz_dsi_Ey_waveform, erg_pwe_efd_l2_E256Hz_wpt_Ex_waveform, erg_pwe_efd_l2_E256Hz_wpt_Ey_waveform
  - timespan, '2017-04-01/11:30', 10, /m
  - erg_load_pwe_efd, level='l2', datatype='E64', coord='dsi'
  - erg_load_pwe_efd, level='l2', datatype='E64', coord='wpt'
  - erg_load_pwe_efd, level='l2', datatype='E256', coord='dsi'
  - erg_load_pwe_efd, level='l2', datatype='E256', coord='wpt'
  - tplot, [ 'erg_pwe_efd_l2_*waveform' ] 

  ![plot example](/doc/imgs/efd_l2_E_waveform.png) 
  
- erg_pwe_efd_l2_sepc_spectra
  - timespan, '2017-04-01'
  - erg_load_pwe_efd, level='l2', datatype='spec'
  - tplot, [ 'erg_pwe_efd_l2_sepc_spectra' ] 

  ![plot example](/doc/imgs/efd_l2_E_spec.png) 

- erg_pwe_efd_l2_pot_Vu1
  - timespan, '2017-04-01'
  - erg_load_pwe_efd, level='l2', datatype='pot'
  - tplot, [ 'erg_pwe_efd_l2_pot_Vu1' ] 

  ![plot example](/doc/imgs/efd_l2_E_pot.png) 

- erg_pwe_efd_l2_pot8Hz_Vu1_waveform_8Hz, erg_pwe_efd_l2_pot8Hz_Vv1_waveform_8Hz, erg_pwe_efd_l2_pot8Hz_Vu2_waveform_8Hz, erg_pwe_efd_l2_pot8Hz_Vv2_waveform_8Hz
  - timespan, '2017-04-01/10-:30', 1, /m
  - erg_load_pwe_efd, level='l2', datatype='pot8Hz'
  - tplot, [ 'erg_pwe_efd_l2_pot8Hz_Vu1_waveform_8Hz', 'erg_pwe_efd_l2_pot8Hz_Vv1_waveform_8Hz', 'erg_pwe_efd_l2_pot8Hz_Vu2_waveform_8Hz', 'erg_pwe_efd_l2_pot8Hz_Vv2_waveform_8Hz' ] 

  ![plot example](/doc/imgs/efd_l2_E_pot8Hz.png) 
