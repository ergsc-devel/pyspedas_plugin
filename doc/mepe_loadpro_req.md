## 移植対象 / script to be ported:
erg_load_mepe.pro


## 要移植オプション / necessary options:

### 共通 / common:
- level : "l2", "l3"
- datatype : "3dflux", "omniflux" 
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- downloadonly : (boolean)
- no_download : (boolean)
- uname, passwd : (a string)

### スクリプト特有 / script-specific:


## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:

- erg_mepe_l2_3dflux_FEDU, erg_mepe_l2_3dflux_FEDU_n
  - sample command: timespan, '2017-03-27' & erg_load_mepe, level='l2', datatype='3dflux'

  - spec=1, ysubtitle='[keV]', no_interp=1
  - ztitle='[/s-cm!U2!N-sr-keV]'
  - ylim, 6., 100., 1
  - zlim, 0, 0, 1  (set to be auto-scaling)
  - datagap=17. 
  - extend_y_edges=1 

- erg_mepe_l2_3dflux_count_raw, erg_mepe_l2_3dflux_spin_phase
  - sample command: timespan, '2017-03-27' & erg_load_mepe, level='l2', datatype='3dflux'

  - spec=1, ysubtitle='[keV]' (only for count_raw)
  - ylim, 6., 100., 1  (only for count_raw)

- erg_mepe_l2_omniflux_FEDO
  - sample command: timespan, '2017-03-27' & erg_load_mepe, level='l2', datatype='omniflux'

  - spec=1, ysubtitle='[keV]', no_interp=1
  - ztitle='[/s-cm!U2!N-sr-keV]'
  - ylim, 6., 100., 1
  - zlim, 0, 0, 1  (set to be auto-scaling)
  - datagap=17. 
  - extend_y_edges=1 

- erg_mepe_l3_3dflux_FEDU, erg_mepe_l3_3dflux_FEDU_alpha 
  - sample command: timespan, '2017-03-27' & erg_load_mepe, level='l3' 

  - (No options to be set for these tplot variables )


## プロットコマンドとプロット例 / Plot commands and plot examples 

- erg_mepe_l2_3dflux_FEDU, erg_mepe_l2_3dflux_FEDU_n, erg_mepe_l2_3dflux_count_raw, erg_mepe_l3_3dflux_FEDU, erg_mepe_l3_3dflux_FEDU_alpha, erg_mepe_l2_3dflux_spin_phase: Not to be plotted as they are.

- erg_mepe_l2_omniflux_FEDO
  - timespan, '2017-03-27' & erg_load_mepe, level='l2', datatype='omniflux'
  - tplot, 'erg_mepe_l2_omniflux_FEDO' 

  ![plot example](/doc/imgs/mepe_fedo_plot.png)
  

