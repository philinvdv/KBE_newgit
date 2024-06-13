# from math import radians, tan
# from parapy.geom import *
# from parapy.core import *
# import numpy as np
# from parapy.geom.generic.positioning import VX, VY  # parapy.geom from 1.2.9
#
# from globs import AIRFOIL_DATA
#
# class Skin(GeomBase):
#     side = Input(validator=val.OneOf(["left", "right"]))
#     root_chord = Input()
#     tip_chord = Input()
#     kink_span = Input()
#     center_section_span = Input()
#     half_span = Input()
#     LE_sweep = Input()
#     TE_sweep = Input()
#     rib_pitch = Input()
#
#     @Attribute
#     def kink_chord(self):
#         return self.root_chord - (tan(radians(self.LE_sweep)) * (self.kink_span - self.center_section_span)) - (
#                     tan(radians(self.TE_sweep)) * (self.kink_span - self.center_section_span))
#
#     @Attribute
#     def tip_x_pos(self):
#         return -self.root_chord + (
#                     tan(radians(self.LE_sweep)) * (self.half_span - self.center_section_span)) + self.tip_chord
#
#     @Attribute
#     def kink_x_pos(self):
#         return - tan(radians(self.TE_sweep)) * (self.kink_span - self.center_section_span)
#
#     # @Attribute
#     # def points(self):
#     #     """Read airfoil coordinates from file.
#     #
#     #     :rtype: list[Point]
#     #     """
#     #     lst = []
#     #     with open(AIRFOIL_DATA) as f:
#     #         for line in f:
#     #             x, y = line.split(' ', 1)
#     #             pt = Point(float(x), float(y), 0)
#     #             lst.append(pt)
#     #     return lst
#
#     @Attribute
#     def points(self):
#         """ Extract airfoil coordinates from a data file and create a list of 3D points"""
#         with open('NACA_2412_points.dat', 'r') as f:
#             lst = []
#             for line in f:
#                 x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
#                 # Convert the strings to numbers and make 3D points for the FittedCurve class
#                 lst.append(Point(float(x), float(y)))
#                 # Note that the points are imported in the X-Y plane. A rotation below (line 79) could be avoided if
#                 # points were imported in the X-Z plane, e.g. points.append(Point(float(x), 0, float(y))
#         return lst
#
#     @Part
#     def fitted_curve(self):
#         return FittedCurve(points=self.points)
#
#     @Attribute
#     def from_position(self):
#         points = self.fitted_curve.points
#         te_point = points[0].midpoint(points[-1])  # works for blunt airfoils
#         orientation = Orientation(x=VX, z=VY)
#         return Position(te_point, orientation)
#
#     @Part
#     def root_curve(self):
#         return TransformedCurve(curve_in=self.fitted_curve,
#                                 from_position=self.from_position,
#                                 to_position=translate(self.fitted_curve.position, 'y', self.center_section_span))
#
#     @Part
#     def scaled_root_curve(self):
#         return ScaledCurve(curve_in=self.root_curve,
#                            reference_point=self.root_curve.start,
#                            factor=self.root_chord)
#
#     @Part
#     def kink_curve(self):
#         return TransformedCurve(curve_in=self.fitted_curve,
#                                 from_position=self.from_position,
#                                 to_position=translate(self.fitted_curve.position, 'y', self.kink_span, 'x',
#                                                       self.kink_x_pos))
#
#     @Part
#     def scaled_kink_curve(self):
#         return ScaledCurve(curve_in=self.kink_curve,
#                            reference_point=self.kink_curve.start,
#                            factor=self.kink_chord)
#
#     @Part
#     def tip_curve(self):
#         return TransformedCurve(curve_in=self.fitted_curve,
#                                 from_position=self.from_position,
#                                 to_position=translate(self.fitted_curve.position, 'y', self.half_span, 'x', self.tip_x_pos))
#
#     @Part
#     def scaled_tip_curve(self):
#         return ScaledCurve(curve_in=self.tip_curve,
#                            reference_point=self.tip_curve.start,
#                            factor=self.tip_chord)
#
#     @Part
#     def Inner_wing_section(self):
#         return LoftedSurface(profiles=[self.scaled_root_curve, self.scaled_kink_curve])
#
#     @Part
#     def Outer_wing_section(self):
#         return LoftedSurface(profiles=[self.scaled_kink_curve, self.scaled_tip_curve])
#
#     @Part
#     def skin(self):
#         return Fused(self.Outer_wing_section, self.Inner_wing_section)
# # if __name__ == '__main__':
# #     from parapy.gui import display
# #     obj = Skin()
# #     display(obj)