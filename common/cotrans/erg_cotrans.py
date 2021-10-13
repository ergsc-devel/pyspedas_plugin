def erg_replace_coord_suffix(in_name=None, out_coord=None):
    nms = in_name.split('_')
    nms[-1] = out_coord
    return '_'.join(nms)