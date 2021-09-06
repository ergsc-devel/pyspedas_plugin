## 移植対象 / script to be ported:
erg_load_mepi_nml.pro


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

- erg_mepi_l2_3dflux_{FPDU | FHE2DU | FHEDU | FOPPDU | FODU | FO2PDU}
- erg_mepi_l2_3dflux_count_raw_{P | HE2 | HE | OPP | O | O2P}
  - sample command: timespan, '2017-03-27' & erg_load_mepi_nml, level='l2', datatype='3dflux'

  - spec=1, ysubtitle='[keV/q]', no_interp=1
  - ztitle='[/s-cm!U2!N-sr-keV]'  (only for F?DU)
  - ylim, 4., 190., 1
  - zlim, 0, 0, 1  (set to be auto-scaling)
  - datagap=33. 
  - extend_y_edges=1 

- erg_mepi_l2_omniflux_{FPDO | FHE2DO | FHEDO | FOPPDO | FODO | FO2PDO}
- erg_mepi_l2_omniflux_{FPDO_tof | FHE2DO_tof | FHEDO_tof | FOPPDO_tof | FODO_tof | FO2PDO_tof}
  - sample command: timespan, '2017-03-27' & erg_load_mepi_nml, level='l2', datatype='omniflux' 

  - spec=1, ysubtitle='[keV/q]', no_interp=1
  - ztitle='[/s-cm!U2!N-sr-keV]'
  - ylim, 4., 190., 1
  - zlim, 0, 0, 1 (set to be auto-scaling)
  - datagap=33.
  - extend_y_edges=1

## プロットコマンドとプロット例 / Plot commands and plot examples

- erg_mepi_l2_3dflux_{FPDU | FHE2DU | FHEDU | FOPPDU | FODU | FO2PDU}
- erg_mepi_l2_3dflux_count_raw_{P | HE2 | HE | OPP | O | O2P}
  - NOT to be plotted as they are.

- erg_mepi_l2_omniflux_{FPDO | FHE2DO | FHEDO | FOPPDO | FODO | FO2PDO}
- erg_mepi_l2_omniflux_{FPDO_tof | FHE2DO_tof | FHEDO_tof | FOPPDO_tof | FODO_tof | FO2PDO_tof}
  - timespan, '2017-03-27' & erg_load_mepi_nml, level='l2', datatype='omniflux' 
  - tplot, ['erg_mepi_l2_omniflux_FPDO', 'erg_mepi_l2_omniflux_FPDO_tof']

  ![plot example](/doc/imgs/mepi_fpdo_plot.png)
  

