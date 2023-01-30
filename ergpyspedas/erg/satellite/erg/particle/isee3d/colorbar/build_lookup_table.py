import vtk

from . import spedas_colorbar
from .cmaps import cmaps


def build_lookup_table(colormap_name = 'jet'):
    if colormap_name == 'spedas':
        colormap = [rgb for rgb in zip(spedas_colorbar.r, spedas_colorbar.g, spedas_colorbar.b)]
    else:
        colormap_hex = cmaps[colormap_name]
        colormap = [hex2rgb(hex) for hex in colormap_hex]
    lut = vtk.vtkLookupTable()
    colorSeries = vtk.vtkColorSeries()
    colorSeries.SetNumberOfColors(len(colormap))
    for i, (rgb) in enumerate(colormap):
       colorSeries.SetColor(i, vtk.vtkColor3ub(rgb))
    colorSeries.BuildLookupTable(lut, colorSeries.ORDINAL)
    return lut

def hex2rgb(hx):
    h = hx.lstrip("#")
    rgb = [int(h[i : i + 2], 16) for i in (0, 2, 4)]
    return rgb

def validate_colormap_name(colormap_name):
    colormap_names = list(cmaps.keys()) + ['spedas']
    if colormap_name in colormap_names:
        return True
    else:
        return False