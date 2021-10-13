from pytplot import tplot_copy

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
                        