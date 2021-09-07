## script to be ported:
erg_load_orb_l3.pro 

## necessary options:
### common:
- model : "op","t89","ts04"
- varformat : (any string)
- trange : (a two-element string array or floating-point array)
- no_download : (boolean)
- download_only : (boolean)
- uname : (a string)
- passwd : (a string)

###  script-specific: 
- version : (a string such as "v03")

## tplot variables to be checked and options to be set:
- erg_orb_l3_pos_lm_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='Lmc ('+model_name+')'
  - ysubtitle='[dimensionless]'
  - labels = ['90deg','80deg','70deg','60deg','50deg','40deg','30deg','20deg','10deg']
- erg_orb_l3_pos_lstar_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='Lstar ('+model_name+')'
  - ysubtitle='[dimensionless]'
  - labels = ['90deg','80deg','70deg','60deg','50deg','40deg','30deg','20deg','10deg']
- erg_orb_l3_pos_I_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='I ('+model_name+')'
  - ysubtitle='[Re]'
  - labels = ['90deg','80deg','70deg','60deg','50deg','40deg','30deg','20deg','10deg']
- erg_orb_l3_pos_blocal_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='Blocal ('+model_name+')'
  - ysubtitle='[nT]'
  - labels = '|B|'
  - ylog = 1
- erg_orb_l3_pos_beq_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='Beq ('+model_name+')'
  - ysubtitle='[nT]'
  - labels = '|B|'
  - ylog = 1
- erg_orb_l3_pos_eq_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='Eq_pos ('+model_name+'Q)'
  - ysubtitle='[Re Hour]'
  - labels = ['Re','MLT']
- erg_orb_l3_pos_iono_north_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='footprint_north ('+model_name+')'
  - ysubtitle='[deg. deg.]'
  - labels = ['GLAT','GLON']
- erg_orb_l3_pos_iono_south_[op, t89, ts04]
  - sample command: timespan, '2017-05-01' & erg_load_orb_l3(, model='t89' or 'ts04')
  - ytitle='footprint_south ('+model_name+')'
  - ysubtitle='[deg. deg.]'
  - labels = ['GLAT','GLON']

## Plot commands and plot examples
- erg_orb_l3_lstar_[op, t89,ts04]
  - timespan, '2017-05-01' & erg_load_orb_l3
  - tplot, [ 'erg_orb_l3_pos_lstar_op' ] 
 ![plot example](/doc/imgs/orb_l3_lstar_op.png)
  