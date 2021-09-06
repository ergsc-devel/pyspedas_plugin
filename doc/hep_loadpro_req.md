## 移植対象 / script to be ported:
erg_load_hep.pro 

## 要移植オプション / necessary options:
### 共通 / common:
- level : "l2", "l3"
- datatype : "3dflux", "omniflux"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)
- ror : (boolean)
### スクリプト特有 / script-specific: 
- version : (a string such as "v01_02", "v01_03", ...)

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_hep_l2_FEDU_L, erg_hep_l2_FEDU_H
  - sample command: timespan, '2017-03-27' & erg_load_hep, level='l2', datatype='3dflux'

  - no_interp=1, 
  - tclip, -1.0e+10, 1.0e+10
- erg_hep_l2_FEDO_L
  - sample command: timespan, '2017-03-27' & erg_load_hep, level='l2', datatype='omniflux'
  
  - ztitle = '[/cm!U2!N-str-s-keV]', spec=1, ystyle=1, 
  - ytitle='HEP-L!Comniflux!CLv2!CEnergy', ysubtitle='[keV]'
  - zticklen=-0.4, zlog=1, ztickunits='scientific'
  - ylim, 30, 1800, 1
  - zlim, 1e+1, 1e+6, 1
- erg_hep_l2_FEDO_H
  - sample command: timespan, '2017-03-27' & erg_load_hep, level='l2', datatype='omniflux'

  - ztitle = '[/cm!U2!N-str-s-keV]', spec=1, ystyle=1, 
  - ytitle='HEP-L!Comniflux!CLv2!CEnergy', ysubtitle='[keV]'
  - zticklen=-0.4, zlog=1, ztickunits='scientific'
  - ylim, 70, 2048, 1
  - zlim, 1e+0, 1e+5, 1
- erg_hep_l3_FEDU_L, erg_hep_l3_FEDU_L_paspec_ene?? (??: 00, 01, 02, ..., 15)
  - sample command: timespan, '2017-03-27' & erg_load_hep, level='l3'

  - ylim, 0, 180, 0
  - zlim, 1e+2, 1e+6, 1
  - spec=1, ysubtitle='PA [deg]', extend_y_edges=1
  - ztickunits='scientific', zticklen=-0.4, ztitle='[/keV/cm!U2!N/sr/s]'
  - ytickinterval=45., constant=[45., 90., 135.] 
  - datagap=130. (if possible) 
- erg_hep_l3_FEDU_H, erg_hep_l3_FEDU_H_paspec_ene?? (??: 00, 01, 02, ..., 10)
  - sample command: timespan, '2017-03-27' & erg_load_hep, level='l3'

  - ylim, 0, 180, 0
  - zlim, 1e+1, 1e+4, 1
  - spec=1, ysubtitle='PA [deg]', extend_y_edges=1
  - ztickunits='scientific', zticklen=-0.4, ztitle='[/keV/cm!U2!N/sr/s]'
  - ytickinterval=45., constant=[45., 90., 135.] 
  - datagap=130. (if possible to apply to only this tplot variable) 

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_hep_l2_FEDU_L, erg_hep_l2_FEDU_H: NOT to be plotted as they are. 

- erg_hep_l2_FEDO_L, erg_hep_l2_FEDO_H
  - timespan, '2017-03-27' & erg_load_hep, level='l2', datatype='omniflux' 
  - tplot, [ 'erg_hep_l2_FEDO_L', 'erg_hep_l2_FEDO_H' ] 

  ![plot example](/doc/imgs/hep_fedo_lh_plot.png) 

- erg_hep_l3_FEDU_L, erg_hep_l3_FEDU_H: NOT to be plotted as they are.

- erg_hep_l3_FEDU_L_paspec_ene??, erg_hep_l3_FEDU_H_paspec_ene??
  - timespan, '2017-03-27' & erg_load_hep, level='l3' 
  - tplot, [ 'erg_hep_l3_FEDU_L_paspec_ene01', 'erg_hep_l3_FEDU_H_paspec_ene01' ] 

 ![plot example](/doc/imgs/hep_l3_fedu_lh.png)
 
  