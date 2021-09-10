## script to be ported:
erg_load_orb_predict.pro 

## necessary options:
### common:
- datatype :  "pre", "spre", "mpre", "lpre" 
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)

###  script-specific: 
- version : (a string such as "v03")

## tplot variables to be checked and options to be set:
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_(gse, gsm, sm)
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['X','Y','Z']
  - colors=[2,4,6]
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_rmlatmlt
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['Re','MLAT','MLT']
  - colors=[2,4,6]
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_eq
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['Req','MLT']
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_iono_(north, south)
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['GLAT','GLON']
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_blocal
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['X','Y','Z']
  - colors=[2,4,6]
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_blocal_mag
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label='B(model)!C_at_ERG'
  - ylog=1
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_beq
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['X','Y','Z']
  - colors=[2,4,6]
  - ylog=1
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_lm
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['90deg','60deg','30deg']
  - colors=[2,4,6]
- erg_orb_[pre, spre, mpre, lpre)_l2_vel_(gse, gsm, sm)
  - sample command: timespan, '2017-05-01' & erg_load_orb_predict
  - label=['X[km/s]','Y[km/s]','Z[km/s]']
  - colors=[2,4,6]

## Plot commands and plot examples
- erg_orb_(pre, spre, mpre, lpre)_l2_pos_(gse, gsm, sm)
  - timespan, '2017-05-01' & erg_load_orb_predict
  - tplot, [ 'erg_orb_pre_l2_pos_sm' ] 
 ![plot example](/doc/imgs/orb_pre_l2_sm.png)

  