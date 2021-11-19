"""
; --- This program calculates the unit vector of sight direction (in SGI
;     coordinates [satellite spin coordinates]) of the  n-th MEPe/MEPi channel.
;
; --- You can find some documents on the geometory of MEPs in the MEP server
;     directory: /raid/meps/docs. The geometory of MEPe explained in
;     MEPe_EPS_r1_black.pdf is used in this function. The document that
;     describes MEPi geometory is missing now (2017/Oct/01).
;
"""

def get_mepe_az_dir_in_sga(fluxdir=False):

    """
    ;parameter
    ;channel azimuthal angle
    ; --- starts from -Z(SGI) axis and increases toward -Y(SGI) axis.
    ;     Note that MEPe channel number is clockwise when you see from
    ;     +X(SGI) direction.
    """


    