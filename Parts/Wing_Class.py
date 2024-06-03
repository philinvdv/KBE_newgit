from math import radians, tan
from parapy.geom import *
from parapy.core import *
import numpy as np
from parapy.core.decorators import action
from parapy.exchange import STEPWriter
from parapy.core.widgets import (
    Button, CheckBox, ColorPicker, Dropdown, FilePicker, MultiCheckBox,
    ObjectPicker, SingleSelection, TextField)
from parapy.core.validate import *
from Parts.Spars import Spars
from Parts.RibPart import Rib
from Parts.Skins import Skins
import os
import pandas as pd

DIR = os.path.dirname(__file__)
material_library = pd.read_excel(io='Parts/Material_library.xlsx')
material_names=[]
for name in range(len(material_library.iloc[:, 0])):
    material_names.append(material_library.iloc[name, 0])
class Wing_me(GeomBase):
    """This class contains the wing itself, from the loaded airfoil points. Contains the components that are in the wing
    as well, including the (front and rear) spars and the (upper and lower) skins."""


    #Inputs
    span = Input(35.8, validator=GT(0, msg="Wing span cannot be smaller than " "{validator.limit}!"))
    leading_edge_sweep = Input(25,  validator=Between(-60, 60, msg="Leading edge sweep angle cannot be greater than +-{60}!")) #deg
    root_chord = Input(5.9, validator=GT(0, msg="Root chord cannot be smaller than " "{validator.limit}!"))
    twist_angle = Input(0)
    dihedral_angle = Input(0)
    wing_material = Input(0) #should somehow get the properties from this
    material = Input(material_names[0], widget=Dropdown(material_names,
                                                       autocompute=False))

    @Attribute
    def material_properties(self):
        index = material_names.index(self.material)
        density = material_library.iloc[index, 1]
        elastic_modulus = material_library.iloc[index, 2]
        poisson_ratio = material_library.iloc[index, 3]
        return [density, elastic_modulus, poisson_ratio]


    def smaller_than_span(self, value):
        return value < self.span/2 and value > 0, "Number should be greater than 0 and smaller than the half-span"

    kink_location = Input(6, validator=smaller_than_span) #measured from centerline of fuselage
    tip_chord = Input(1.64, validator=GT(0, msg="{value} cannot be greater than " "{validator.limit}!"))
    width_centerpiece = Input(3, validator=smaller_than_span)
    rib_pitch = Input(2, validator=GT(0, msg="{value} cannot be greater than " "{validator.limit}!"))
    hide_mesh = Input(True)



    @Attribute
    def start_wing_to_kink(self):
        return self.kink_location - self.width_centerpiece / 2

    @Attribute
    def tip_chord_kink(self):
        return self.root_chord - self.start_wing_to_kink * np.tan(radians(self.leading_edge_sweep)) #if trailing edge kink has zero sweep

    @Attribute
    def pts_pre(self):
        """ Extract airfoil coordinates from a data file and create a list of 3D points"""
        front_spar_coordinates = []
        rear_spar_coordinates = []
        with open('NACA_2412_points.dat', 'r') as f:
            points = []
            for line in f:
                x, y = line.split(' ', 1)  # separator = " "; max number of split = 1
                # Convert the strings to numbers and make 3D points for the FittedCurve class
                points.append(Point(float(x), float(y)))
                # Note that the points are imported in the X-Y plane. A rotation below (line 79) could be avoided if
                # points were imported in the X-Z plane, e.g. points.append(Point(float(x), 0, float(y)))
                if float(x) == 0.2:
                    # if (float(x) - 0.2) < abs(0.001):
                    front_spar_coordinates.append([float(x), float(y), 0])
                if float(x) == 0.7:
                    rear_spar_coordinates.append([float(x), float(y), 0])
        return points, front_spar_coordinates, rear_spar_coordinates

    @Attribute #split into the different components
    def pts(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return points

    @Attribute
    def front_spar_coordinates(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return front_spar_coordinates

    @Attribute
    def rear_spar_coordinates(self):
        points, front_spar_coordinates, rear_spar_coordinates = self.pts_pre
        return rear_spar_coordinates

    @Part
    def airfoil_from_3D_points(self):  # this curve is on the X-Y plane, with TE = (1, 0, 0) and LE = (0, 0, 0)
        return FittedCurve(points=self.pts,
                           mesh_deflection=0.0001)

    @Part
    def crv1_repositioned_inner(self):  # ***************THIS WON'T WORK!!! ************* a curve built from 3D points /
        # cannot be moved. It stays nailed to its 3D points!
        return FittedCurve(points=self.pts,
                           position=translate(rotate(XOY, 'x', 90, deg=True),
                                              'x', self.position.x, #-1
                                              'y', self.position.y,
                                              'z', self.position.z),
                           color="red")

    @Part  # TransformedCurve is making a carbon copy of the fitted curve, which can be moved (rotated and translated) /
    # from one position to another. /
    # In this case we want to position the fitted curve copy in the x-z plane of the wing reference system, with its /
    # TE in the origin (location) of this reference system. This requires a rotation and a few translations.
    def root_section_unscaled_inner(self):
        return TransformedCurve(
            curve_in=self.airfoil_from_3D_points,
            # the curve to be repositioned
            #from_position=rotate(translate(XOY, 'x', 1), 'x', -90, deg=True),
            from_position=rotate(translate(XOY, 'x', 0), 'x', -90, deg=True),
            # Can be thought of as moving a frame to the position on the curve from which you want to move it. It will
            # now be at the trailing edge and with X-Z plane aligned with curve plane.
            to_position=self.position,  # The wing relative reference system
            hidden=False
        )

    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def tip_section_unscaled_inner(self):
        return TransformedCurve(
            curve_in=self.root_section_unscaled_inner,
            # the curve to be repositioned
            from_position=self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.start_wing_to_kink,
                                  'x', 0
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part
    def root_section_inner(self):  # the ScaledCurve primitive allows scaling a given curve. Here it is used to scale /
        # the unit chord airfoil generated from the .dat file according to their actual chord length
        return ScaledCurve(
            curve_in=self.root_section_unscaled_inner,
            reference_point=self.root_section_unscaled_inner.start,  # this point (the curve TE in this case) / is kept fixed during scaling
            # Can also use "self.position.point" - This extracts the (x,y,z) origin of the wing class position.
            factor=self.root_chord,  # uniform scaling
            mesh_deflection=0.0001
        )

    @Part
    def tip_section_inner(self):
        return ScaledCurve(
            curve_in=self.tip_section_unscaled_inner,
            reference_point=self.tip_section_unscaled_inner.start,
            factor=self.tip_chord_kink
        )

    @Part
    def wing_loft_surf_inner(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.root_section_inner, self.tip_section_inner],
            mesh_deflection=0.0001
        )

    @Part #Mirror and transform
    def transform_mirror_wing_inner(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in = self.wing_loft_surf_inner, reference_point=Point(0,0,0), vector1=(1,0,0), vector2=(0,0,1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', -1, 'y', -self.width_centerpiece)  # New position of the curve
        )

    """Outer wing"""
    @Part  # for the wing tip we use the same type of airfoil used for the wing root. We use again TransformedCurve
    def tip_section_unscaled_outer(self):
        return TransformedCurve(
            curve_in=self.tip_section_unscaled_inner,
            # the curve to be repositioned
            from_position=self.root_section_unscaled_inner.position,
            to_position=translate(self.root_section_unscaled_inner.position,  # to_position, i.e. the wing tip section
                                  'y', self.span / 2 - self.width_centerpiece / 2 - self.start_wing_to_kink,
                                  'x', (self.span/2 - self.width_centerpiece/2) * np.tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.root_chord
                                  #'x', (self.span / 2 - self.kink_location) * tan(radians(self.leading_edge_sweep)) + self.tip_chord - self.tip_chord_kink + self.start_wing_to_kink * tan(radians(self.leading_edge_sweep))
                                  ),  # the sweep is applied
            hidden=True
        )

    @Part
    def tip_section_outer(self):
        return ScaledCurve(
            curve_in=self.tip_section_unscaled_outer,
            reference_point=self.tip_section_unscaled_outer.start,
            factor=self.tip_chord
        )

    @Part
    def wing_loft_surf_outer(self):  # generate a surface
        return LoftedSurface(
            profiles=[self.tip_section_inner, self.tip_section_outer],
            mesh_deflection=0.0001
        )

    @Part #Mirror and move outer wing
    def transform_mirror_wing_outer(self):
        return TransformedSurface(
            surface_in=MirroredSurface(surface_in=self.wing_loft_surf_outer, reference_point=Point(0, 0, 0), vector1=(1, 0, 0),
                               vector2=(0, 0, 1)),  # Original curve to transform
            from_position=self.position,  # Reference position of the original curve
            to_position=translate(XOY, 'x', -1, 'y', -self.width_centerpiece)  # New position of the curve
        )

    @Part
    def my_spars(self):
        return Spars(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,
                     hide_mesh=self.hide_mesh,
                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part
    def my_skins(self):
        return Skins(start_wing_to_kink=self.start_wing_to_kink, tip_chord_kink=self.tip_chord_kink, pts=self.pts,
                     front_spar_coordinates=self.front_spar_coordinates,
                     rear_spar_coordinates=self.rear_spar_coordinates,  # these are attributes
                     span=self.span, leading_edge_sweep=self.leading_edge_sweep, root_chord=self.root_chord,
                     twist_angle=self.twist_angle, dihedral_angle=self.dihedral_angle, wing_material=self.wing_material,
                     kink_location=self.kink_location, tip_chord=self.tip_chord,
                     width_centerpiece=self.width_centerpiece,
                     position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))

    @Part
    def my_ribs(self):
        return Rib(rib_pitch=self.rib_pitch, root_chord=self.root_chord, leading_edge_sweep=self.leading_edge_sweep,
                   width_centerpiece=self.width_centerpiece, span=self.span,
                   position=translate(self.position, 'x', 1, 'y', 0, 'z', 0))


    @Part
    def fused_wing_box(self):
        return Fused(shape_in=self.my_skins.fused_outer_lowerskin_and_flanges,
                     tool=(self.my_skins.fused_outer_upperskin_and_flanges,
                           self.my_skins.fused_inner_lowerskin_and_flanges,
                           self.my_skins.fused_inner_upperskin_and_flanges,
                           self.my_spars.rearspar_outer,
                           self.my_spars.rearspar_inner,
                           self.my_spars.frontspar_outer,
                           self.my_spars.front_spar_inner,
                           ))
    # @Attribute
    # def parts_list(self):
    #     return [Wing_me().wing_loft_surf_inner,
    #             Wing_me().wing_loft_surf_outer,
    #             Wing_me().my_skins.inner_upperskin_loft,
    #             Wing_me().my_skins.inner_lowerskin_loft,
    #             Wing_me().my_skins.outer_upperskin_loft,
    #             Wing_me().my_skins.outer_lowerskin_loft,
    #             Wing_me().my_spars.front_spar_inner]

    # @Attribute
    # def parts_counter(self):
    #     self.x = + 1
    #     return self.x

    # for p in range(5):
    #     @Part
    #     def mesh(self):
    #         return MeshingFunc(part_class=self.parts_list[self.p], n_mesh_points=50)

    # @Part
    # def mesh_inner_loft(self):
    #     return MeshingFunc(part_class=self.parts_list[0], n_mesh_points=50, hide_mesh=self.hide_mesh)
    # #
    # @Part
    # def mesh_outer_loft(self):
    #     return MeshingFunc(part_class=self.parts_list[1], n_mesh_points=50, hide_mesh=self.hide_mesh)
    # #
    # @Part
    # def mesh3(self):
    #     return MeshingFunc(part_class=self.parts_list[2], n_mesh_points=50)


    # @Part
    # def step_writer(self):
    #     return STEPWriter(nodes=[self.my_skins.fused_inner_upperskin_and_flanges,
    #                          self.my_skins.fused_inner_lowerskin_and_flanges,
    #                          self.my_skins.fused_outer_upperskin_and_flanges,
    #                          self.my_skins.fused_outer_lowerskin_and_flanges,
    #                          self.my_spars.front_spar_inner,
    #                          self.my_spars.frontspar_outer,
    #                          self.my_spars.rearspar_inner,
    #                          self.my_spars.rearspar_outer],
    #                   default_directory=DIR,
    #                   filename="aircraft.step")




    # @action
    # def write_inp_file(self):
    #     from Abaqus_analysisV3 import AbaqusINPwriter
    #     AbaqusINPwriter().my_inp_writer.write('output//wing_box.inp')


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing_me()
    display(obj)