from pytplot import tplot_copy
from pyspedas import tnames
from common.cotrans.sgi2dsi import sgi2dsi
from common.cotrans.sga2sgi import sga2sgi

def erg_replace_coord_suffix(in_name=None, out_coord=None):
    nms = in_name.split('_')
    nms[-1] = out_coord
    return '_'.join(nms)

def erg_coord_trans(in_name=None,
                    out_name=None,
                    in_coord=None,
                    out_coord=None,
                    noload=False):

                    if in_coord == out_coord:
                        tplot_copy(in_name, out_name)
                        return
                        
                    #From DSI
                    if in_coord == 'dsi':

                        if out_coord == 'sga': # dsi --> sgi --> sga
                            name_sgi = erg_replace_coord_suffix(in_name=in_name, out_coord='sgi')
                            sgi2dsi(name_in=in_name, name_out=name_sgi, DSI2SGI=True, noload=noload)
                            sga2sgi(name_in=name_sgi, name_out=out_name, SGI2SGA=True, noload=noload)

#;;;; Main routine for coordinate transformation ;;;;; 
def erg_cotrans(in_name='',
                out_name='',
                in_coord='',
                out_coord='',
                noload=False):

                valid_suffixes = ['sga', 'sgi', 'dsi', 'j2000']

                in_names=tnames(in_name)
                if len(in_names) == 0:
                    print('in_name is not match in stored Tplot Variables, return')
                    return

                for input_name in in_names:
                    if in_coord not in valid_suffixes:
                        if (input_name.split('_')[-1] in valid_suffixes):
                            in_suf = input_name.split('_')[-1]
                        else:
                            print(f'Cannot get a valid coord. suffix of input variable for {input_name}.')
                            continue
                    else:
                        in_suf = in_coord
                    if out_coord not in valid_suffixes:
                        if out_name.split('_')[-1] in valid_suffixes:
                            out_suf = out_name.split('_')[-1]
                        else:
                            print(f'Cannot get a valid coord. suffix of output variable for {input_name}.')
                            continue
                    else:
                        out_suf = out_coord
                    
