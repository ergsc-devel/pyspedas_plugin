## 移植対象 / script to be ported:
erg_load_lepi_nml.pro 

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
- version : (a string such as "v03_00")

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_lepi_l2_3dflux_FPDU,erg_lepi_l2_3dflux_FHEDU,erg_lepi_l2_3dflux_FODU
  - sample command: timespan, '2017-05-01' & erg_load_lepi_nml, level='l2', datatype='3dflux'
  - no_interp=1, 
  - tclip, -1.0e+10, 1.0e+10
- erg_lepi_l2_omniflux_FPDO,erg_lepi_l2_omniflux_FHEDO,erg_lepi_l2_omniflux_FODO
  - sample command: timespan, '2017-05-01' & erg_load_lepi_nml, level='l2'
  - ztitle = '[/cm!U2!N-str-s-keV]', spec=1, ystyle=1, 
  - ytitle='LEPi!Comniflux!CLv2!CEnergy', ysubtitle='[keV]'
  - zticklen=-0.4, zlog=1, ztickunits='scientific'
  - ylim, 0.01, 25.0, 1
  - zlim, 1e+1, 1e+9, 1
- erg_lepi_l3_pa_FPDU(FODU,FHEDU), erg_lepi_l3_pa_pabin_??(??:00,01,..29)_FPDU(FODU,FHEDU)
  - sample command: timespan, '2017-05-01' & erg_load_lepi_nml, level='l3'
  - ylim, 0, 180, 0
  - zlim, 1e+1, 1e+9, 1
  - spec=1, ysubtitle='PA [deg]', extend_y_edges=1
  - ztickunits='scientific', zticklen=-0.4, ztitle='[/keV/cm!U2!N/sr/s]'
  - ytickinterval=45., constant=[45., 90., 135.] 

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_lepi_l2_FPDO (FHEDO,FODO)
  - timespan, '2017-05-01' & erg_load_lepi_nml, level='l2'
  - tplot, [ 'erg_lepi_l2_FPDO' ] 

- erg_lepi_l3_pa_FPDU, erg_lepi_l3_pa_pabin_??(00,01..)_FPDU
  - timespan, '2017-05-01' & erg_load_lepi_nml, level='l3' 
  - tplot, ['erg_lepi_l3_pa_pabin_01_FPDU' ] 

 ![plot example](/doc/imgs/lepi_l3_fpdu.png)
 
  