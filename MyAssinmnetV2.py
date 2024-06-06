from parapy.geom import *
from parapy.core import *

from parapy.core.validate import *
import Parts
import Parts.output
from parapy.exchange import STEPWriter
import os

DIR = os.path.dirname(__file__)


class Aircraft(GeomBase):
    """This is the Superclass. It only contains the Wing class."""
    span = Input(35.8, validator=GT(0, msg="Wing span cannot be smaller than " "{validator.limit}!"))
    leading_edge_sweep = Input(25,  validator=Between(-60, 60, msg="Leading edge sweep angle cannot be greater than +-{60}!"))
    width_centerpiece = Input(5, validator=GT(0, msg="Centre section width cannot be smaller than " "{validator.limit}!"))
    rib_pitch = Input(2, validator=GT(0, msg="Rib pitch cannot be smaller than " "{validator.limit}!"))
    hide_mesh = Input(True)
    load_factor = Input(2.5, validator=GT(0, msg="Load factor cannot be smaller than " "{validator.limit}!"))
    aircraft_mass = Input(10000, validator=GT(0, msg="Aircraft mass cannot be smaller than " "{validator.limit}!"))
    engine_position = Input([4, 8]) #, validator=Between(0, 60, msg="Engine position has to be between wing root and tip!"))
    engine_mass = Input(1000, validator=GE(0, msg="Engine mass cannot be smaller than " "{validator.limit}!"))


    @Part #Sicne the centerpiece depends fully on the geometry of the wing, it is a subclass of the wing
    def wing(self):
        return Parts.Wing_me(hide_mesh=self.hide_mesh, width_centerpiece=self.width_centerpiece, rib_pitch=self.rib_pitch, span=self.span,
                       leading_edge_sweep=self.leading_edge_sweep,
                    position=translate(self.position, 'x', -1, 'y', 0, 'z',
                                       0))  # Puts the origin at the trailing edge of the kink


    @Part
    def write_inp(self):
        return Parts.AbaqusINPwriter(path=self.wing,
                                     density=self.wing.material_properties[0],
                                     elastic_modulus=self.wing.material_properties[1],
                                     poisson_ratio=self.wing.material_properties[2],
                                     span=self.span,
                                     width_centerpiece=self.width_centerpiece,
                                     load_factor=self.load_factor,
                                     aircraft_mass = self.aircraft_mass,
                                     engine_position = self.engine_position,
                                     engine_mass = self.engine_mass,
                                     hidden=False)

    # @Part
    # def run_abaqus_interpreter(self):
    #     return Parts.output.ODBinterpreter
    @action()
    def INP_file_writer(self):
        self.write_inp.my_inp_writer.write('Parts//output//wing_box.inp')

    @action()
    def run_abaqus(self):
        import Parts.output.ODBinterpreter

#     @Part
#     def right_wing(self):
#         return Wing(side="right",width_centerpiece=self.width_centerpiece,
#                     span=self.wing_span,
#                     sweep=self.wing_sweep, position=translate(self.position, 'x', 0, 'y', -5, 'z',
#                                        0))
#
#     @Part
#     def left_wing(self):
#         return Wing(side="left",width_centerpiece=self.width_centerpiece,
#                     span=self.right_wing.span,
#                     sweep=self.right_wing.sweep,
#                     position=self.right_wing.position)
#
#     # @Part
#     # def my_centerpiece(self):
#     #     return Centerpiece(width_centerpiece=self.width_centerpiece)
#
#     # One could use MirroredShape to obtain the left wing, but GEOMETRY ONLY
#     # @Part
#     # def left_wing_alternative(self):
#     #     return MirroredShape(shape_in=self.right_wing.solid,
#     #                          reference_point=self.right_wing.position,
#     #                          vector1=self.position.Vx,
#     #                          vector2=self.position.Vz)
#
# class Wing(GeomBase):
#     """Position of Wing:
#
#     - location: trailing edge point of root wing airfoil
#     - orientation:
#         - x-direction: points from leading edge to trailing edge
#         - y-direction: spanwise direction of wing
#         - z-direction: local up direction for root airfoil
#     """
#
#     #: is this 'left' or 'right' hand side wing?
#     #: :type: str
#     side = Input(validator=val.OneOf(["left", "right"]))
#     kink_span = Input(6)
#     center_section_span = Input(5)
#     span = Input(35.8)
#     LE_sweep = Input(25.0)
#     TE_sweep = Input(0.0)
#     rib_pitch = Input(2)
#     leading_edge_sweep = Input(25)  # deg
#     root_chord = Input(5.9)
#     twist_angle = Input(0)
#     dihedral_angle = Input(0)
#     wing_material = Input(0)  # should somehow get the properties from this
#     kink_location = Input(6)  # measured from centerline of fuselage
#     tip_chord = Input(1.64)
#     width_centerpiece = Input()
#
#     @Attribute
#     def half_span(self):
#         return self.span / 2 + self.width_centerpiece/2
#
#     @Part
#     def skin(self):
#         return Skin(side=self.side, root_chord=self.root_chord, tip_chord=self.tip_chord, kink_span=self.kink_span,
#                     center_section_span=self.center_section_span, half_span=self.half_span, LE_sweep=self.LE_sweep,
#                     TE_sweep=self.TE_sweep)
#
#     @Part
#     def rib(self):
#         return Rib(rib_pitch=self.rib_pitch, root_chord=self.root_chord, LE_sweep=self.LE_sweep,
#                    width_centerpiece=self.width_centerpiece, half_span=self.half_span)

    # @Part
    # def subtracted_ribs(self):
    #     return Subtracted(shape_in=self.skin, tool=self.rib)


    @Part
    def step_writer(self):
        return STEPWriter(nodes=[Parts.Wing_me().my_skins.fused_inner_upperskin_and_flanges,
                             Parts.Wing_me().my_skins.fused_inner_lowerskin_and_flanges,
                             Parts.Wing_me().my_skins.fused_outer_upperskin_and_flanges,
                             Parts.Wing_me().my_skins.fused_outer_lowerskin_and_flanges,
                             Parts.Wing_me().my_spars.front_spar_inner,
                             Parts.Wing_me().my_spars.frontspar_outer,
                             Parts.Wing_me().my_spars.rearspar_inner,
                             Parts.Wing_me().my_spars.rearspar_outer],
                      default_directory=DIR,
                      unit='m',
                      filename="aircraft.step")





if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft(label="aircraft")
    display(obj)