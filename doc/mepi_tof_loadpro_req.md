## 移植対象 / script to be ported:
erg_load_mepi_tof.pro


## 要移植オプション / necessary options:

### 共通 / common:
- level : "l2"
- datatype : "flux", "raw" 
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- downloadonly : (boolean)
- no_download : (boolean)
- uname, passwd : (a string)

### スクリプト特有 / script-specific:
(N/A)

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:

- erg_mepi_l2_tofflux_{FPDU | FHE2DU | FHEDU | FOPPDU | FODU | FO2PDU}
- erg_mepi_l2_tofflux_count_raw_{P | HE2 | HE | OPP | O | O2P}
  - sample command: timespan, '2017-03-27' & erg_load_mepi_tof, level='l2', datatype='flux'

  - spec=1, ysubtitle='[keV/q]', no_interp=1
  - ztitle='[/s-cm!U2!N-sr-keV/q]'  (for F?DU)
  - ztitle='[cnt/smpl]'  (for count_raw_?)
  - ylim, 4., 190., 1
  - zlim, 0, 0, 1  (set to be auto-scaling)
  - datagap=33., extend_y_edges=1

- erg_mepi_l2_tofraw_count, erg_mepi_l2_tofraw_spin_phase
  - sample command: timespan, '2017-03-27' & erg_load_mepi_tof, level='l2', datatype='raw'

  - spec=1, datagap=33., extend_y_edges=1
  - zlim, 0, 0, 1   (set to be auto-scaling)

## プロットコマンドとプロット例 / Plot commands and plot examples

- erg_mepi_l2_tofflux_{FPDU | FHE2DU | FHEDU | FOPPDU | FODU | FO2PDU}
- erg_mepi_l2_tofflux_count_raw_{P | HE2 | HE | OPP | O | O2P}
  - Not to be plotted as they are.

- erg_mepi_l2_tofraw_count, erg_mepi_l2_tofraw_spin_phase
  - Not to be plotted as they are.
