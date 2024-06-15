from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from Parts.CustomPlane import *
from Parts.Stringer_part import *

class Stringer(GeomBase):
    """In this class, the stringers are defined as well as their locations. You can have a different amount of stringers
    for the inner and outer wingbox, as well as for the upper and lower panels."""
    nr_stringers_upper_inner = Input(4)
    nr_stringers_lower_inner = Input(4)
    nr_stringers_upper_outer = Input(4)
    nr_stringers_lower_outer = Input(4)
    stringer_width = Input(0.02)
    stringers_height = Input(0.02)

    tip_chord_kink = Input()
    span = Input()
    leading_edge_sweep = Input()  # deg
    root_chord = Input()
    kink_location = Input()  # measured from centerline of fuselage
    tip_chord = Input()
    width_centerpiece = Input()

    @Attribute
    def start_wing_to_kink(self):
        return self.kink_location - self.width_centerpiece / 2

    """STRINGERS"""

    """Upper inner"""
    @Attribute
    def LE_stringer_pts_upper_inner(self):
        sp = np.linspace(0.3 * self.root_chord, 0.8 * self.root_chord,
                            self.nr_stringers_upper_inner + 2)
        pts = np.delete(sp, 0)
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute
    def kink_stringer_pts_upper_inner(self):
        sp_kink = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                           (self.nr_stringers_upper_inner + 2))
        pts_kink = np.delete(sp_kink, 0)
        pts_kink_ = np.delete(pts_kink, -1)
        return pts_kink_

    @Part  # plane for upper inner stringers
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

    @Part
    def stringer_upper_inner(self):
        return Stringer_Part(quantify=len(self.line_str_upper_inner),
                             edge_in=self.line_str_upper_inner[child.index].edges[0], up_down=-1, angle_sign=1,
                             width_stringer=0.1)#, angle_y=self.parent.my_skins.angle_upperskin_inner)


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

    @Part
    def stringer_lower_inner(self):
        return Stringer_Part(quantify=len(self.line_str_lower_inner),
                             edge_in=self.line_str_lower_inner[child.index].edges[0], up_down=1, angle_sign=1,
                             width_stringer=0.1)#, angle_y=0)

    """Outer upper"""
    @Attribute
    def kink_stringer_pts_upper_outer(self):
        sp = np.linspace(0.3 * self.tip_chord_kink, 0.8 * self.tip_chord_kink,
                         self.nr_stringers_upper_outer + 2)
        pts = np.delete(sp, 0)
        pts_ = np.delete(pts, -1)
        return pts_

    @Attribute
    def tip_stringer_pts_upper_outer(self):
        start_x = -((self.span / 2 - self.width_centerpiece / 2) * np.tan(
                    radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord)
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
                           width_section=(self.span/2 - self.width_centerpiece/2 - self.start_wing_to_kink),
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
        return Stringer_Part(quantify=len(self.line_str_upper_outer),
                             edge_in=self.line_str_upper_outer[child.index].edges[0], up_down=-1, angle_sign=1,
                             width_stringer=0.05)#, angle_y=self.parent.my_skins.angle_upperskin_outer)

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
        start_x = -((self.span / 2 - self.width_centerpiece / 2) * np.tan(
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
                           width_section=(self.span / 2 - self.width_centerpiece / 2 - self.start_wing_to_kink),
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
        return Stringer_Part(quantify=len(self.line_str_lower_outer),
                             edge_in=self.line_str_lower_outer[child.index].edges[0], up_down=-1,angle_sign=1,
                             width_stringer=0.05)#, angle_y=0)

    # @Part  # This gives the curves on the wingbox at the location of the stringers
    # def intersected_str_upper(self):
    #     return IntersectedShapes(
    #         quantify=len(self.stringers_CP_upper),
    #         shape_in=self.upperskin_centerpiece_loft,
    #         tool=self.stringers_CP_upper[child.index].custom_plane,
    #         hidden=False
    #     )
    #
    # @Part  # This gives the curves on the wingbox at the location of the stringers
    # def intersected_str_lower(self):
    #     return IntersectedShapes(
    #         quantify=len(self.stringers_CP_lower),
    #         shape_in=self.lowerskin_centerpiece_loft,
    #         tool=self.stringers_CP_lower[child.index].custom_plane,
    #         hidden=False
    #     )
    #




    # @Part
    # def lines_upper_inner(self):
    #     return RectangularSurface(quantify=len(self.LE_stringer_points_upper), width=self.stringer_width,
    #                               position=translate(rotate(rotate90(translate(self.position, 'y', self.rib_pos[0],
    #                                                                            'x', - self.root_chord),
    #                                                                  'x'), 'y', -self.leading_edge_sweep, deg=True),
    #                                                  'z', -self.LE_rib_pos[child.index]))

    # @Part
    # def lines_upper_inner(self):
    #     return Rectangle(quantity=len(self.LE_stringer_points_upper),
    #         start=Point(self.LE_stringer_points_upper[child.index], 0, 0),
    #                        end=Point(self.kink_stringer_points_upper[child.index], self.start_wing_to_kink, 0))

    # @Attribute
    # def stringer_lines(self):
    #     le_points = self.LE_stringer_points_upper
    #     kink_points = self.kink_stringer_points_upper
    #     lines = []
    #     for le, kink in zip(le_points, kink_points):
    #         line = Line(start=Point(le, 0, 0), end=Point(kink, 1, 0))  # Adjust y, z coordinates as needed
    #         lines.append(line)
    #     return lines

    # @Part
    # def LE_points_stringers(self):
    #     return Point(self.LE_stringer_points_upper[child.index], 0, 0
    #     ) #change y
    # #
    # @Attribute
    # def stringer_pos(self):
    #     return np.linspace(0, self.LE_length, round(self.rib_pitch * (self.half_span-self.width_centerpiece/2)) + 1)
