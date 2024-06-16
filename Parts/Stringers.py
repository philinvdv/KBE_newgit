from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.CustomPlane import *
from Parts.StringerPart import *

class Stringer(GeomBase):
    """In this class, the stringers are defined as well as their locations. You can have a different amount of stringers
    for the inner and outer wingbox, as well as for the upper and lower panels."""
    stringer_width = Input(0.1)

    start_wing_to_kink = Input()
    tip_chord_kink = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()
    nr_stringers_upper_inner = Input(4)  # number of stringers in the inner wingbox on the upperskin
    nr_stringers_lower_inner = Input(4)  # number of stringers in the inner wingbox on the lowerskin
    nr_stringers_upper_outer = Input(4)  # number of stringers in the outer wingbox on the upperskin
    nr_stringers_lower_outer = Input(4)  # number of stringers in the outer wingbox on the lowerskin

    """Upper inner"""
    @Attribute #Split the root chord into the amount of stringers that we have, giving the starting points of the stringer
    def LE_stringer_pts_upper_inner(self):
        sp = np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
                            self.nr_stringers_upper_inner + 2)
        pts = np.delete(sp, 0) #You dont want a stringer at the front- and rearspar, so delete these points from the list
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute #Do the same at the kink
    def kink_stringer_pts_upper_inner(self):
        sp_kink = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                           (self.nr_stringers_upper_inner + 2))
        pts_kink = np.delete(sp_kink, 0)
        pts_kink_ = np.delete(pts_kink, -1)
        return pts_kink_

    @Part  # plane for upper inner stringers. The stringers are on the lines that are the connection of the location
    #points on the root and the kink. All stringers have a different orientation, so to account for this a custom plane
    #class is made. See CustomPlane.py for more information
    def stringers_upper_inner_plane(self):
        return CustomPlane(quantify=self.nr_stringers_upper_inner,
                           stringer_location_1=self.LE_stringer_pts_upper_inner[child.index],
                           stringer_location_2=self.kink_stringer_pts_upper_inner[child.index],
                           width_section=self.start_wing_to_kink,
                           chord=self.root_chord,
                           sign=1, start_y=0, hidden=True)

    @Part  # This gives the curves on the wingbox at the location of the stringers
    def line_str_upper_inner(self):
        return IntersectedShapes(
            quantify=len(self.stringers_upper_inner_plane),
            shape_in=self.parent.my_skins.inner_upperskin_loft, #this takes the upperskin from Skins, which is a sibling
            tool=self.stringers_upper_inner_plane[child.index].custom_plane,
            hidden=False
        )

    @Part #Use the custom made StringerPart class to generate stringers at the locations defined by the lines. See
    #StringerPart.py for more information
    def stringer_upper_inner(self):
        return StringerPart(quantify=len(self.line_str_upper_inner),
                             edge_in=self.line_str_upper_inner[child.index].edges[0], up_down=-1, angle_sign=1,
                             width_stringer=self.stringer_width)

    #Repeat the same process for the different the different sections
    """Lower inner"""
    @Attribute
    def LE_stringer_pts_lower_inner(self):
        sp = np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
                         self.nr_stringers_lower_inner + 2)
        pts = np.delete(sp, 0)
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute
    def kink_stringer_pts_lower_inner(self):
        sp_kink = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                              (self.nr_stringers_lower_inner + 2))
        pts_kink = np.delete(sp_kink, 0)
        pts_kink_ = np.delete(pts_kink, -1)
        return pts_kink_

    @Part  # plane for lower inner stringers
    def stringers_lower_inner_plane(self):
        return CustomPlane(quantify=self.nr_stringers_lower_inner,
                           stringer_location_1=self.LE_stringer_pts_lower_inner[child.index],
                           stringer_location_2=self.kink_stringer_pts_lower_inner[child.index],
                           width_section=self.start_wing_to_kink,
                           chord=self.root_chord,
                           sign=1, start_y=0, hidden=True)

    @Part  # This gives the curves on the wingbox at the location of the stringers
    def line_str_lower_inner(self):
        return IntersectedShapes(
            quantify=len(self.stringers_lower_inner_plane),
            shape_in=self.parent.my_skins.inner_lowerskin_loft, #this takes the lowerskin from Skins, which is a sibling
            tool=self.stringers_lower_inner_plane[child.index].custom_plane,
            hidden=False
        )

    @Part #This gives the actual stringers
    def stringer_lower_inner(self):
        return StringerPart(quantify=len(self.line_str_lower_inner),
                             edge_in=self.line_str_lower_inner[child.index].edges[0], up_down=1, angle_sign=1,
                             width_stringer=self.stringer_width)

    """Outer upper"""
    @Attribute
    def kink_stringer_pts_upper_outer(self):
        sp = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                         self.nr_stringers_upper_outer + 2)
        pts = np.delete(sp, 0)
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute #This one is slightly different, since the outer wingbox does not start at the origin
    def tip_stringer_pts_upper_outer(self):
        start_x = -((self.span / 2 - self.width_centerpiece) * np.tan(radians(self.leading_edge_sweep))
                    + self.tip_chord - self.root_chord)
        sp_kink = np.linspace(start_x + 0.3 * self.tip_chord, start_x + 0.8 * self.tip_chord,
                              (self.nr_stringers_upper_outer + 2))
        pts_kink = np.delete(sp_kink, 0)
        pts_kink_ = np.delete(pts_kink, -1)
        return pts_kink_

    @Part  # Planes for upper outer stringers
    def stringers_upper_outer_plane(self):
        return CustomPlane(quantify=self.nr_stringers_upper_outer,
                           stringer_location_1=self.kink_stringer_pts_upper_outer[child.index],
                           stringer_location_2=self.tip_stringer_pts_upper_outer[child.index],
                           width_section=(self.span/2 - self.width_centerpiece - self.start_wing_to_kink),
                           chord=self.root_chord,
                           sign=1, start_y=self.start_wing_to_kink, hidden=True)

    @Part  # This gives the curves on the wingbox at the location of the stringers
    def line_str_upper_outer(self):
        return IntersectedShapes(
            quantify=len(self.stringers_upper_outer_plane),
            shape_in=self.parent.my_skins.outer_upperskin_loft, #this takes the upperskin from Skins, which is a sibling
            tool=self.stringers_upper_outer_plane[child.index].custom_plane,
            hidden=False
        )

    @Part
    def stringer_upper_outer(self):
        return StringerPart(quantify=len(self.line_str_upper_outer),
                             edge_in=self.line_str_upper_outer[child.index].edges[0], up_down=-1, angle_sign=1,
                             width_stringer=0.5*self.stringer_width)

    """Outer lower"""
    @Attribute
    def kink_stringer_pts_lower_outer(self):
        sp = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                         self.nr_stringers_lower_outer + 2)
        pts = np.delete(sp, 0)
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute
    def tip_stringer_pts_lower_outer(self):
        start_x = -((self.span / 2 - self.width_centerpiece) * np.tan(
            radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord)
        sp_kink = np.linspace(start_x + 0.3 * self.tip_chord, start_x + 0.8 * self.tip_chord,
                              (self.nr_stringers_lower_outer + 2))
        pts_kink = np.delete(sp_kink, 0)
        pts_kink_ = np.delete(pts_kink, -1)
        return pts_kink_

    @Part  # lower outer stringers
    def stringers_lower_outer_plane(self):
        return CustomPlane(quantify=self.nr_stringers_lower_outer,
                           stringer_location_1=self.kink_stringer_pts_lower_outer[child.index],
                           stringer_location_2=self.tip_stringer_pts_lower_outer[child.index],
                           width_section=(self.span / 2 - self.width_centerpiece - self.start_wing_to_kink),
                           chord=self.root_chord,
                           sign=1,
                           start_y=self.start_wing_to_kink, hidden=True)

    @Part  # This gives the curves on the wingbox at the location of the stringers
    def line_str_lower_outer(self):
        return IntersectedShapes(
            quantify=len(self.stringers_lower_outer_plane),
            shape_in=self.parent.my_skins.outer_lowerskin_loft, #this takes the upperskin from Skins, which is a sibling
            tool=self.stringers_lower_outer_plane[child.index].custom_plane,
            hidden=False
        )

    @Part
    def stringer_lower_outer(self):
        return StringerPart(quantify=len(self.line_str_lower_outer),
                             edge_in=self.line_str_lower_outer[child.index].edges[0], up_down=-1,angle_sign=-1,
                             width_stringer=0.5*self.stringer_width)
