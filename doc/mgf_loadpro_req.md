## 移植対象 / script to be ported:
erg_load_mgf.pro 

## 要移植オプション / necessary options:
### 共通 / common:
- level : "l2"
- datatype : "8sec", "64hz", "128hz", "256hz"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)
- ror : (boolean)
### スクリプト特有 / script-specific: 
- coord : "sm", "dsi", "gse", "gsm", "sgi" 
- version : (a string such as "v03.03", "v03.04", ...)

## 要確認tplot変数と要設定オプション / tplot variables to be checked and options to be set:
- erg_mgf_l2_mag_8sec_{dsi|gse|gsm|sm}
- erg_mgf_l2_mag_8sec_magt_8sec
- erg_mgf_l2_rmsd_8sec_{dsi|gse|gsm|sm}
- erg_mgf_l2_igrf_8sec_{dsi|gse|gsm|sm}
- erg_mgf_l2_dyn_rng_8sec
  - sample command: timespan, '2017-03-27' & erg_load_mgf, level='l2', datatype='8sec'

  - tclip, -1e+6, +1e+6
  - tclip, -120, +1e+6   (only for erg_mgf_l2_dyn_rng_8sec)
  - labels=['Bx','By','Bz'] colors=[2,4,6]  (only for erg_mgf_l2_mag_8sec_*, erg_mgf_l2_igrf_8sec_*, erg_mgf_l2_rmsd_8sec_* )


- erg_mgf_l2_mag_64hz_{sgi|dsi|gse|gsm|sm}
  - sample command: timespan, '2017-03-27/10:00', 1, /hour & erg_load_mgf, level='l2', datatype='64hz', coord='sm'  (smの場合)

  - tclip, -1e+6, +1e+6 
  - labels=['Bx','By','Bz'] colors=[2,4,6]


- erg_mgf_l2_mag_128hz_{sgi|dsi|gse|gsm|sm}
  - sample command: timespan, '2017-03-27/16:00', 1, /hour & erg_load_mgf, level='l2', datatype='128hz', coord='sm'  (smの場合)

  - tclip, -1e+6, +1e+6 
  - labels=['Bx','By','Bz'] colors=[2,4,6]


- erg_mgf_l2_mag_256hz_{sgi|dsi|gse|gsm|sm}
  - sample command: timespan, '2017-03-27/07:00', 1, /hour & erg_load_mgf, level='l2', datatype='256hz', coord='sm'  (smの場合)

  - tclip, -1e+6, +1e+6 
  - labels=['Bx','By','Bz'] colors=[2,4,6]

## プロットコマンドとプロット例 / Plot commands and plot examples
- erg_mgf_l2_mag_8sec_{dsi|gse|gsm|sm}
  - timespan, '2017-03-27' & erg_load_mgf, level='l2', datatype='8sec'
  - tplot, [ 'erg_mgf_l2_mag_8sec_sm' ]
  
  ![plot example](/doc/imgs/mgf_l2_8sec.png)

- erg_mgf_l2_mag_64hz_{dsi|gse|gsm|sm}
  - timespan, '2017-03-27/10:00', 1, /hour & erg_load_mgf, level='l2', datatype='64hz'
  - tplot, [ 'erg_mgf_l2_mag_64hz_sm' ]
  
  ![plot example](/doc/imgs/mgf_l2_64hz.png)

- erg_mgf_l2_mag_128hz_{dsi|gse|gsm|sm}
  - timespan, '2017-03-27/16:00', 1, /hour & erg_load_mgf, level='l2', datatype='128hz'
  - tplot, [ 'erg_mgf_l2_mag_128hz_sm' ]
  
  ![plot example](/doc/imgs/mgf_l2_128hz.png)

- erg_mgf_l2_mag_8sec_mag_8sec_{dsi|gse|gsm|sm}
  - timespan, '2017-03-27/07:00', 1, /hour & erg_load_mgf, level='l2', datatype='256hz'
  - tplot, [ 'erg_mgf_l2_mag_256hz_sm' ]
  
  ![plot example](/doc/imgs/mgf_l2_256hz.png)

