from parapy.geom import *
from parapy.core import *

from parapy.core.validate import *
from Parts import *
import Parts.output
from parapy.exchange import STEPWriter
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from parapy.core.widgets import (
    Button, CheckBox, ColorPicker, Dropdown, FilePicker, MultiCheckBox,
    ObjectPicker, SingleSelection, TextField)
import math
import numpy as np
from csv import DictReader
import operator
import csv
import glob
from parapy.core.widgets import FilePicker
#from Parts.Wing_Class import *

DIR = os.path.dirname(__file__)


# partial_filename = "configuration"
#
# configuration_files = glob.glob(f"*{partial_filename}*.csv")
#
# material_library = pd.read_excel(io='Parts/output.xlsx')
# material_names=[]
# for name in range(len(material_library.iloc[:, 0])):
#     material_names.append(material_library.iloc[name, 0])

class Aircraft(GeomBase):
    """This is the Superclass. It only contains the Wing class."""
    aircraft_name = Input("my_aircraft_name")
    saved_aircraft_configuration = Input('Parts/output/my_aircraft_name_configuration.csv',
                                         widget=FilePicker(wildcard="*.csv", default_dir="Parts/output"))

    span = Input(35.8, validator=GT(0, msg="Wing span cannot be smaller than " "{validator.limit}!"))
    leading_edge_sweep = Input(25,  validator=Between(-60, 60, msg="Leading edge sweep angle cannot be greater than +-{60}!"))
    width_centerpiece = Input(2.5, validator=GT(0, msg="Centre section width cannot be smaller than " "{validator.limit}!")) #This is the width of half the centerpiece
    # leading_edge_sweep = Input(25, validator=Between(-60, 60, msg="Leading edge sweep angle cannot be greater than +-{60}!"))
    # width_centerpiece = Input(2.5, validator=GT(0, msg="Centre section width cannot be smaller than " "{validator.limit}!"))
    rib_pitch = Input(2, validator=GT(0, msg="Rib pitch cannot be smaller than " "{validator.limit}!"))
    load_factor = Input(2.5, validator=GT(0, msg="Load factor cannot be smaller than " "{validator.limit}!"))
    aircraft_mass = Input(10000, validator=GT(0, msg="Aircraft mass cannot be smaller than " "{validator.limit}!"))
    engine_position = Input([4])  # , validator=Between(0, 60, msg="Engine position has to be between wing root and tip!"))
    engine_mass = Input(1000, validator=GE(0, msg="Engine mass cannot be smaller than " "{validator.limit}!"))
    root_chord = Input(5.9, validator=GT(0, msg="Root chord cannot be smaller than " "{validator.limit}!"))
    tip_chord = Input(1.64, validator=GT(0, msg="{value} cannot be greater than " "{validator.limit}!"))
    kink_location = Input(6, validator=Parts.Wing_me.smaller_than_span) #measured from centerline of fuselage
    # twist_angle = Input(0)
    # dihedral_angle = Input(0)
    material = Input(Parts.Wing_Class.material_names[0], widget=Dropdown(Parts.Wing_Class.material_names, autocompute=False))
    skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    upper_inner_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    upper_outer_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    lower_inner_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    lower_outer_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    spar_thickness = Input(0.05, validator=GT(0, msg="Spar thickness cannot be smaller than " "{validator.limit}!"))
    rib_thickness = Input(0.005, validator=GT(0, msg="Rib thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_skin_thickness = Input(0.003, validator=GT(0, msg="Centre section skin thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_spar_thickness = Input(0.01, validator=GT(0, msg="Centre section spar thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_rib_thickness = Input(0.005, validator=GT(0, msg="Centre section rib thickness cannot be smaller than " "{validator.limit}!"))

    @Part  # Sicne the centerpiece depends fully on the geometry of the wing, it is a subclass of the wing
    def wing(self):
        return Parts.Wing_me(span=self.span,
                             leading_edge_sweep=self.leading_edge_sweep,
                             width_centerpiece=self.width_centerpiece,
                             rib_pitch=self.rib_pitch,
                             # load_factor=self.load_factor,
                             # aircraft_mass=self.aircraft_mass,
                             # engine_position=self.engine_position,
                             # engine_mass=self.engine_mass,
                             root_chord=self.root_chord,
                             material=self.material,
                             skin_thickness=self.skin_thickness,
                             upper_inner_skin_thickness=self.upper_inner_skin_thickness,
                             upper_outer_skin_thickness=self.upper_outer_skin_thickness,
                             lower_inner_skin_thickness=self.lower_inner_skin_thickness,
                             lower_outer_skin_thickness=self.lower_outer_skin_thickness,
                             spar_thickness=self.spar_thickness,
                             rib_thickness=self.rib_thickness,
                             centre_section_skin_thickness=self.centre_section_skin_thickness,
                             centre_section_spar_thickness=self.centre_section_spar_thickness,
                             centre_section_rib_thickness=self.centre_section_rib_thickness,
                             position=translate(self.position, 'x', -1, 'y', 0, 'z',
                                                0))  # Puts the origin at the trailing edge of the kink

    @Part
    def write_inp(self):
        return Parts.AbaqusINPwriter(path=self.wing,
                                     density=self.wing.material_properties[0],
                                     elastic_modulus=self.wing.material_properties[1],
                                     poisson_ratio=self.wing.material_properties[2],
                                     skin_thickness=self.wing.skin_thickness,
                                     upper_inner_skin_thickness=self.wing.upper_inner_skin_thickness,
                                     upper_outer_skin_thickness=self.wing.upper_outer_skin_thickness,
                                     lower_inner_skin_thickness=self.wing.lower_inner_skin_thickness,
                                     lower_outer_skin_thickness=self.wing.lower_outer_skin_thickness,
                                     spar_thickness=self.wing.spar_thickness,
                                     rib_thickness=self.wing.rib_thickness,
                                     centre_section_skin_thickness=self.wing.centre_section_skin_thickness,
                                     centre_section_spar_thickness=self.wing.centre_section_spar_thickness,
                                     centre_section_rib_thickness=self.wing.centre_section_rib_thickness,
                                     span=self.span,
                                     width_centerpiece=self.width_centerpiece,
                                     load_factor=self.load_factor,
                                     aircraft_mass=self.aircraft_mass,
                                     engine_position=self.engine_position,
                                     engine_mass=self.engine_mass,
                                     hidden=False)

    @action()
    def INP_file_writer(self):
        os.chdir(os.getcwd())
        self.write_inp.my_inp_writer.write('Parts//output//wing_box.inp')
        print('INP file was written successfully')

    @action()
    def run_abaqus(self):
        os.chdir('Parts/output')
        subprocess.run('python ODBinterpreter.py')
        # os.chdir(os.getcwd())
        print('Done running abaqus. Check directory for results')
        os.chdir(DIR)

    @action()
    def process_results(self):
        # os.chdir(DIR)
        # print(os.getcwd())
        stresses = pd.read_csv('Parts/output/mises_stress.csv', delimiter=",", dtype=object)
        U3 = pd.read_csv('Parts/output/U3.csv', delimiter=",", dtype=object)
        print('processing files, please wait')
        def check_if_float(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        mises = []
        X = []
        Y = []
        Z = []
        # check_if_float(stresses.iloc[i, -1])
        for i in range(len(stresses.iloc[:, ])):
            # print(i, (type(item) in item for item in stresses.iloc[i, :]))
            # print(i, any("SPOS" in item for item in stresses.iloc[i, :]))
            if check_if_float(stresses.iloc[i, -1]) and any("SPOS" in item for item in stresses.iloc[i, :]):
                mises.append(float(stresses.iloc[i, -1]))
                X.append(float(stresses.iloc[i, :].get('X')))
                Y.append(float(stresses.iloc[i, :].get('Y')))
                Z.append(float(stresses.iloc[i, :].get('Z')))
            else:
                continue

        yield_exceeded = []
        Y_for_yield_exceeded = []
        for i in range(len(mises)):
            if mises[i] > self.wing.material_properties[3]:
                yield_exceeded.append(mises[i])
                Y_for_yield_exceeded.append(Y[i])
            else:
                continue
                # yield_exceeded.append(0)

        print('Plotting results, please wait')
        # for i in range(len(yield_exceeded)):
        #     if yield_exceeded[i] > 5.05e8:
        #         print(yield_exceeded[i])

        # index = mises.index(max_mises_stress)
        # fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        # ax.scatter(X, Y, Z, color='green', s=10)
        # ax.quiver(X, Y, Z, X, Y, mises, length=0.1, normalize=True)
        # # plt.axis('equal')
        # plt.show()

        # fig = plt.figure()
        # ax = fig.add_subplot()
        plt.scatter(Y, mises)
        plt.scatter(Y_for_yield_exceeded, yield_exceeded, color='red', s=5)
        plt.xlabel('Spanwise direction [m]')
        plt.ylabel('Mises stress [Pa]')
        plt.title('Mises stress along wingspan')
        plt.legend(['Mises stress', 'Mises stress > yield strength'])
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        plt.savefig('Parts/output/mises_stress_distribution.png')
        plt.show()

        U3_magnitude = []
        U3_X = []
        U3_Y = []
        U3_Z = []
        # check_if_float(stresses.iloc[i, -1])
        for i in range(len(U3.iloc[:, ])):
            if check_if_float(U3.iloc[i, -1]):
                U3_magnitude.append(float(U3.iloc[i, -1]))
                U3_X.append(float(U3.iloc[i, :].get('X')))
                U3_Y.append(float(U3.iloc[i, :].get('Y')))
                U3_Z.append(float(U3.iloc[i, :].get('Z')))

        print(len(U3.iloc[:, ]), len(U3_magnitude), len(U3_Y))
        # plt.ion()
        plt.scatter(Y, Z)
        plt.scatter(U3_Y, U3_magnitude, color='red', s=5)
        plt.xlabel('Spanwise direction [m]')
        plt.ylabel('U3 Deformation [m]')
        plt.title('Deformation along wingspan')
        plt.legend(['Undeformed', 'Deformed'])
        plt.axis('equal')
        plt.savefig('Parts/output/defomred_wing.png')
        plt.show()

        print('Results were processed successfully')
        print('max U3 displacement is: ', max(U3_magnitude), '[m]', 'and max mises stress is: ', max(mises), '[Pa]')



    @action()
    def save_aircraft_configuration(self):
        os.chdir(DIR)
        # os.chdir('Parts/output')
        # spamwriter = csv.DictWriter(csvfile, delimiter=',',
        #                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
        user_input_list = {"Parameter": "Value",
                           "aircraft_name": self.aircraft_name,
                           "span": self.wing.span,
                           "leading_edge_sweep": self.wing.leading_edge_sweep,
                           "root_chord": self.wing.root_chord,
                           # "twist_angle": self.wing.twist_angle,
                           # "dihedral_angle": self.wing.dihedral_angle,
                           "material_name": self.wing.material,
                           "material_density": self.wing.material_properties[0],
                           "material_elastic_modulus": self.wing.material_properties[1],
                           "material_poisson_ratio": self.wing.material_properties[2],
                           "skin_thickness": self.wing.skin_thickness,
                           "upper_inner_skin_thickness": self.wing.upper_inner_skin_thickness,
                           "upper_outer_skin_thickness": self.wing.upper_outer_skin_thickness,
                           "lower_inner_skin_thickness": self.wing.lower_inner_skin_thickness,
                           "lower_outer_skin_thickness": self.wing.lower_outer_skin_thickness,
                           "spar_thickness": self.wing.spar_thickness,
                           "rib_thickness": self.wing.rib_thickness,
                           "centre_section_skin_thickness": self.wing.centre_section_skin_thickness,
                           "centre_section_spar_thickness": self.wing.centre_section_spar_thickness,
                           "centre_section_rib_thickness": self.wing.centre_section_rib_thickness}

        filename = f"Parts/output/{user_input_list['aircraft_name']}_configuration.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in user_input_list.items():
                writer.writerow([key, value])
        print('Custom aircraft configuration was saved successfully')

        # os.chdir(DIR)

    @action()
    def open_saved_aircraft_configuration(self):

        class SavedAircraft(Aircraft):
            os.chdir(DIR)

            read_csv = pd.read_csv(self.saved_aircraft_configuration, delimiter=",")
            wing_param = []
            for i in range(len(read_csv) - 1):
                wing_param.append(read_csv.iloc[i + 1, 1])

            @Part
            def wing_from_file(self):
                return Aircraft(span=float(self.wing_param[0]),
                                leading_edge_sweep=float(self.wing_param[1]),
                                root_chord=float(self.wing_param[2]),
                                # twist_angle=float(self.wing_param[3]),
                                # dihedral_angle=float(self.wing_param[4]),
                                material=self.wing_param[5],
                                skin_thickness=float(self.wing_param[9]),
                                upper_inner_skin_thickness=float(self.wing_param[10]),
                                upper_outer_skin_thickness=float(self.wing_param[11]),
                                lower_inner_skin_thickness=float(self.wing_param[12]),
                                lower_outer_skin_thickness=float(self.wing_param[13]),
                                spar_thickness=float(self.wing_param[14]),
                                rib_thickness=float(self.wing_param[15]),
                                centre_section_skin_thickness=float(self.wing_param[16]),
                                centre_section_spar_thickness=float(self.wing_param[17]),
                                centre_section_rib_thickness=float(self.wing_param[18]))
                # position=translate(self.position, 'x', -1, 'y', 0, 'z',
                #                0))  # Puts the origin at the trailing edge of the kink

        if __name__ == '__main__':
            from parapy.gui import display

            obj = SavedAircraft()
            display(obj)

    # @Part
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

    from parapy.gui.data import DataPanel

    # DataPanel.POPUP_EXCEPTIONS = False
    # DataPanel.LOG_EXCEPTIONS = False
    obj = Aircraft(label="aircraft")
    display(obj)
