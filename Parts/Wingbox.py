from math import radians, tan, cos
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.Meshing import *
from Parts.CustomPlane import *
from Parts.Skins import *
from Parts.Spars import *
from Parts.Stringers import *
from Parts.RibPart import *

class Wingbox(GeomBase):
    """This class contains the spar geometry, for the front and rear spar of the inner and outer wingbox. It also contains
    the other components that make up the wingbox, namely the skins, stringers and ribs"""
    #The attributes and inputs from Wing() (thus inherited)
    start_wing_to_kink = Input()
    tip_chord_kink = Input()
    pts = Input()
    front_spar_coordinates =Input()
    rear_spar_coordinates = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    wing_material = Input()  # should somehow get the properties from this
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()

    @Part #Call the skins
    def my_skins(self):
        return Skin(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,
                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part #Make the fusion of the flanges with the inner upperskin
    def fused_inner_upperskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.inner_upperskin_loft,
                     tool=(self.my_skins.flange_upperskin_inner_rear, self.my_skins.flange_upperskin_inner_front),
                     hidden=True)

    @Part #Make the fusion of the flanges with the inner lowerskin
    def fused_inner_lowerskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.inner_lowerskin_loft,
                     tool=(self.my_skins.flange_lowerskin_inner_rear, self.my_skins.flange_lowerskin_inner_front),
                     hidden=True)

    @Part #Make the fusion of the flanges with the outer upperskin
    def fused_outer_upperskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.outer_upperskin_loft,
                     tool=(self.my_skins.flange_upperskin_outer_rear, self.my_skins.flange_upperskin_outer_front),
                     hidden=True)

    @Part #Make the fusion of the flanges with the outer lowerskin
    def fused_outer_lowerskin_and_flanges(self):
        return Fused(shape_in=self.my_skins.outer_lowerskin_loft,
                     tool=(self.my_skins.flange_lowerskin_outer_rear, self.my_skins.flange_lowerskin_outer_front),
                     hidden=True)

    @Part #Call the spars
    def my_spars(self):
        return Spar(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,

                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part #Fuse the parts that make up the inner wingbox (only the shell; skins and spars)
    def fused_wingbox_inner(self):
        return Fused(shape_in=self.fused_inner_upperskin_and_flanges,
                     tool=(self.my_spars.front_spar_inner, self.fused_inner_lowerskin_and_flanges,
                           self.my_spars.rearspar_inner),
                     hidden=True)

    @Part #Do the same for the outer wingbox
    def fused_wingbox_outer(self):
        return Fused(shape_in= self.fused_outer_upperskin_and_flanges,
                     tool=(self.my_spars.frontspar_outer, self.fused_outer_lowerskin_and_flanges,
                           self.my_spars.rearspar_outer),
                     hidden=True)

    @Part #Combine inner and outer
    def fused_wingbox_total(self):
        return Fused(shape_in=self.fused_wingbox_inner,
                     tool=self.fused_wingbox_outer)

    @Part #Go to sibling class (centerpiece) and fuse upperskin and frontspar
    def fused_cp1(self):
        return Fused(shape_in=self.parent.my_centerpiece.upperskin_centerpiece_loft,
                     tool=self.parent.my_centerpiece.frontspar_surf_centerpiece,hidden=True)

    @Part #Go to sibling class (centerpiece) and fuse lowerskin and rearspar
    def fused_cp2(self):
        return Fused(shape_in=self.parent.my_centerpiece.lowerskin_centerpiece_loft,
                     tool=self.parent.my_centerpiece.rearspar_loft_centerpiece,hidden=True)

    @Part #Combine the two
    def fused_centerpiece(self):
        return Fused(shape_in=self.fused_cp1,
                     tool=self.fused_cp2, hidden=True)

    @Part #Fuse the complete wingbox, centerpiece and wing. This will be needed to cut some things later
    def fused_wingbox_centerpiece(self):
        return Fused(shape_in=self.fused_wingbox_total,
                     tool=self.fused_centerpiece, hidden=True)

    @Part #Call the ribs
    def my_ribs(self):
        return Rib(root_chord=self.root_chord, tip_chord=self.tip_chord,
                   leading_edge_sweep=self.leading_edge_sweep, width_centerpiece=self.width_centerpiece, span=self.span)

    @Part #Call the stringers
    def my_stringers(self):
        return Stringer(tip_chord_kink=self.tip_chord_kink,
                        span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                        kink_location=self.kink_location, tip_chord=self.tip_chord,
                        width_centerpiece=self.width_centerpiece,
                        start_wing_to_kink = self.start_wing_to_kink,
                        )

