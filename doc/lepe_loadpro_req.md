## script to be ported:
erg_load_lepe.pro 

## necessary options:
### common:
- level : "l2", "l3"
- datatype : "3dflux", "omniflux"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)
- only_fedu : (boolean)
- fine : (boolean)
- et_diagram : (boolean)
### script-specific: 
- version : (a string such as "v03_01")

## tplot variables to be checked and options to be set:
- erg_lepe_l2_3dflux(_fine_ch)_FEDU
  - sample command: timespan, '2017-05-01' & erg_load_lepe, level='l2', datatype='3dflux'(,/fine)
  - spec=1, ysubtitle='[eV]', ztickformat='pwr10tick', extend_y_edges=1, datagap=17., zticklen=-0.4
  - ylim, 19, 21*1e3, 1
  - zlim, 1, 1e6, 1
- erg_lepe_l2_omniflux_FEDO
  - sample command: timespan, '2017-05-01' & erg_load_lepe, level='l2'
  - ztitle = '[/cm!U2!N-str-s-eV]', spec=1, ystyle=1, 
  - ytitle='ERG!CLEP-e!CFEDO!CEnergy', ysubtitle='[eV]'
  - zticklen=-0.4, zlog=1, ztickunits='pwr10tick'
  - ylim, 19, 21*1e3, 1
  - zlim, 1, 1e6, 1
- erg_lepe_l3_pa(_fine)_FEDU
  - sample command: timespan, '2017-05-01' & erg_load_lepe, level='l3'(, /fine)
  - ylim, 19, 21*1e3, 1
  - zlim, 1, 1e6, 1
  - spec=1, ysubtitle='[eV]', extend_y_edges=1
  - ztickunits='pwr10tick', zticklen=-0.4
- erg_lepe_l3_pa(_fine)_pabin_??(??:01,01,..16)_FEDU(, /fine)
  - sample command: timespan, '2017-05-01' & erg_load_lepe, level='l3'
  - ylim, 0, 180, 0
  - zlim, 1, 1e6, 1
  - ytitle='ERG LEP-e!C'+string(energy_arr[0,j],'(f9.2)')+' eV!CPitch angle', YSUBTITLE = '[deg]', yrange=[0,180],ytickinterval=30
- erg_lepe_l3_pa(_fine)_pabin_??(??:01,01,..16)_FEDU
  - sample command: timespan, '2017-05-01' & erg_load_lepe, level='l3',/et_diagram(, /fine)
  - ylim, 19, 21*1e3, 1
  - zlim, 1, 1e6, 1
  - ytitle='ERG LEP-e!c'+string(pa_arr[j],'(f7.3)')+' deg!CEnergy'


## Plot commands and plot examples
- erg_lepe_l2_FEDO
  - timespan, '2017-05-01' & erg_load_lepe, level='l2'
  - tplot, [ 'erg_lepe_l2_FEDO' ] 
 ![plot example](/doc/imgs/lepe_l2_fedo.png)

- erg_lepi_l3_pa_FPDU, erg_lepi_l3_pa_enech_??(01,02..)_FEDU
  - timespan, '2017-05-01' & erg_load_lepe, level='l3' 
  - tplot, ['erg_lepe_l3_pa_enech_07' ] 

 ![plot example](/doc/imgs/lepi_l3_fpdu.png)

- erg_lepi_l3_pa_pabin_??(01,02..)_FEDU
  - timespan, '2017-05-01' & erg_load_lepe, level='l3' ,/et_diagram
  - tplot, ['erg_lepe_l3_pa_pabin_09' ] 

 ![plot example](/doc/imgs/lepe_l3_fedu_et_diagram.png)
 
  