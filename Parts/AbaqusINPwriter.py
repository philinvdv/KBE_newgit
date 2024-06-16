from parapy.lib.abaqus.primitive.feature import SurfaceInteraction
from parapy.mesh.core.groups import FaceGroup, EdgeGroup
from parapy.mesh.salome.controls import FixedNumber, Quad
from parapy.mesh.salome.main import Mesh
from parapy.lib.abaqus.primitive.load import CLoad, DLoad, Dsload
from parapy.lib.abaqus.adaptor import Adaptor
from parapy.lib.abaqus.primitive.component import Dynamic, Step, Static
from parapy.lib.abaqus.primitive.material import \
    Density, ElasticIsotropic, Material
from parapy.lib.abaqus.primitive.output import FieldOutput, HistoryOutput, Output
from parapy.lib.abaqus.primitive.section import ShellSectionProperties
from parapy.lib.abaqus.writer import Writer
from parapy.mesh import Controls, Groups
from parapy.core import *
from parapy.geom import *
import numpy as np
from parapy.core.validate import *


#import MyAssinmnetV2
from Parts.Meshing import MeshingFunc


class AbaqusINPwriter(GeomBase):
    """This file writes an inp file using the parapy abaqus adapter. Since the geometry consists of surfaces, the
    thicknesses are added here."""
    # n_mesh_points = Input(30)
    path = Input()
    mesh_element_length = Input(0.2, validator=GT(0, msg="Mesh element length cannot be smaller than " "{validator.limit}!"))
    density = Input(1000., validator=GT(0, msg="Material density cannot be smaller than " "{validator.limit}!"))
    elastic_modulus = Input(1e9, validator=GT(0, msg="Elastic modulus cannot be smaller than " "{validator.limit}!"))
    poisson_ratio = Input()
    skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    upper_inner_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    upper_outer_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    lower_inner_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    lower_outer_skin_thickness = Input(0.003, validator=GT(0, msg="Skin thickness cannot be smaller than " "{validator.limit}!"))
    spar_thickness = Input(0.01, validator=GT(0, msg="Spar thickness cannot be smaller than " "{validator.limit}!"))
    upper_stringers_thickness = Input(0.005, validator=GT(0, msg="Spar thickness cannot be smaller than " "{validator.limit}!"))
    lower_stringers_thickness =  Input(0.005, validator=GT(0, msg="Spar thickness cannot be smaller than " "{validator.limit}!"))
    rib_thickness = Input(0.005, validator=GT(0, msg="Rib thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_skin_thickness = Input(0.003, validator=GT(0, msg="Centre section skin thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_spar_thickness = Input(0.01, validator=GT(0, msg="Centre section spar thickness cannot be smaller than " "{validator.limit}!"))
    centre_section_rib_thickness = Input(0.005, validator=GT(0, msg="Centre section rib thickness cannot be smaller than " "{validator.limit}!"))

    load_factor = Input(2.5)
    aircraft_mass = Input(10000, validator=GT(0, msg="Aircraft mass cannot be smaller than " "{validator.limit}!"))
    # number_of_engines = Input(1)
    engine_position = Input()
    engine_mass = Input(1000, validator=GE(0, msg="Engine cannot be smaller than " "{validator.limit}!"))
    Gravity = 9.81

    # Importing the wing instance
    @Attribute
    def aircraft(self):
        return self.path

    # Defining the material for the shell sections
    @Attribute
    def material(self):
        material_behaviours = [Density(self.density), ElasticIsotropic(self.elastic_modulus, self.poisson_ratio)]
        material_properties = Material(name="user-chosen_material",
                        behaviours=material_behaviours)
        return material_properties


# below are all the parts that make up the wing box

    #All the skins:
    @Part
    def upper_skin(self):
        return Fused(shape_in=self.aircraft.my_wingbox.fused_inner_upperskin_and_flanges,
                     tool=self.aircraft.my_wingbox.fused_outer_upperskin_and_flanges,
                             hidden=False)

    @Part
    def lower_skin(self):
        return Fused(shape_in=self.aircraft.my_wingbox.fused_inner_lowerskin_and_flanges,
                     tool=self.aircraft.my_wingbox.fused_outer_lowerskin_and_flanges,
                             hidden=False)

    # All the spars:
    @Part
    def front_spar(self):
        return Fused(shape_in=self.aircraft.my_wingbox.my_spars.front_spar_inner,
                     tool=self.aircraft.my_wingbox.my_spars.frontspar_outer,
                             hidden=False)

    @Part
    def rear_spar(self):
        return Fused(shape_in=self.aircraft.my_wingbox.my_spars.rearspar_inner,
                     tool=self.aircraft.my_wingbox.my_spars.rearspar_outer,
                             hidden=False)

    @Attribute
    def wing_stringer_path(self):
        upper_inner_stringers = []
        upper_outer_stringers = []
        lower_inner_stringers = []
        lower_outer_stringers = []
        for i in range(len(self.aircraft.my_wingbox.my_stringers.stringer_upper_inner)):
            upper_inner_stringers.append(self.aircraft.my_wingbox.my_stringers.stringer_upper_inner[i].lofted_stringer)
        for i in range(len(self.aircraft.my_wingbox.my_stringers.stringer_upper_outer)):
            upper_outer_stringers.append(self.aircraft.my_wingbox.my_stringers.stringer_upper_outer[i].lofted_stringer)
        for i in range(len(self.aircraft.my_wingbox.my_stringers.stringer_lower_inner)):
            lower_inner_stringers.append(self.aircraft.my_wingbox.my_stringers.stringer_lower_inner[i].lofted_stringer)
        for i in range(len(self.aircraft.my_wingbox.my_stringers.stringer_lower_outer)):
            lower_outer_stringers.append(self.aircraft.my_wingbox.my_stringers.stringer_lower_outer[i].lofted_stringer)
        return [upper_inner_stringers + upper_outer_stringers, lower_inner_stringers + lower_outer_stringers]

    @Part
    def upper_stringers(self):
        return Fused(shape_in=self.wing_stringer_path[0][0], tool=self.wing_stringer_path[0][:])

    @Part
    def lower_stringers(self):
        return Fused(shape_in=self.wing_stringer_path[1][0], tool=self.wing_stringer_path[1][:])

    # @Part
    # def ribs(self):
    #     # return ModifiedShape(self.aircraft.my_wingbox.ribs_cut, keep=self.aircraft.my_wingbox.ribs_cut[0])
    #     return Fused(shape_in=self.aircraft.my_wingbox.my_ribs.ribs_cut[1],
    #                  tool=self.aircraft.my_wingbox.my_ribs.ribs_cut[2:-1],
    #                          hidden=False)



    @Part
    def ribs_cp(self):
        # return ModifiedShape(self.aircraft.my_wingbox.ribs_cut, keep=self.aircraft.my_wingbox.ribs_cut[0])
        return Fused(shape_in=self.aircraft.my_centerpiece.ribs_cp[0],
                     tool=self.aircraft.my_centerpiece.ribs_cp[1:-1],
                             hidden=False)

    @Part
    def upper_skin_cp(self):
        return Fused(shape_in=self.aircraft.my_centerpiece.upperskin_centerpiece_loft,
                     tool=self.aircraft.my_centerpiece.upperskin_centerpiece_loft)

    @Part
    def lower_skin_cp(self):
        return Fused(shape_in=self.aircraft.my_centerpiece.lowerskin_centerpiece_loft,
                     tool=self.aircraft.my_centerpiece.lowerskin_centerpiece_loft)

    @Part
    def front_spar_cp(self):
        return Fused(shape_in=self.aircraft.my_centerpiece.frontspar_surf_centerpiece,
                     tool=self.aircraft.my_centerpiece.frontspar_surf_centerpiece)

    @Part
    def rear_spar_cp(self):
        return Fused(shape_in=self.aircraft.my_centerpiece.rearspar_loft_centerpiece,
                     tool=self.aircraft.my_centerpiece.rearspar_loft_centerpiece)


    @Attribute
    def stringer_cp_path(self):
        cp_upper_stringers = []
        cp_lower_stringers = []
        for i in range(len(self.aircraft.my_centerpiece.stringer_upper_CP)):
            cp_upper_stringers.append(self.aircraft.my_centerpiece.stringer_upper_CP[i].lofted_stringer)
        for i in range(len(self.aircraft.my_centerpiece.stringer_lower_CP)):
            cp_lower_stringers.append(self.aircraft.my_centerpiece.stringer_lower_CP[i].lofted_stringer)
        return [cp_upper_stringers, cp_lower_stringers]

    @Part
    def upper_stringers_cp(self):
        return Fused(shape_in=self.stringer_cp_path[0][0], tool=self.stringer_cp_path[0][:])

    @Part
    def lower_stringers_cp(self):
        return Fused(shape_in=self.stringer_cp_path[1][0], tool=self.stringer_cp_path[1][:])

    # Meshing the parts and creating groups which are later used for application of forces and boundary conditions
    @Part
    def meshed_upper_skin(self):
        return MeshingFunc(part_class=self.upper_skin,
                           groups=[FaceGroup(shape=self.upper_skin.faces)] +
                                  [EdgeGroup(shape=self.upper_skin.edges)] +
                                  [FaceGroup(shape=[self.upper_skin.faces[0], self.upper_skin.faces[3]])] +
                                  [FaceGroup(shape=self.upper_skin.faces[idx]) for idx in range(len(self.upper_skin.faces))] +
                                  [EdgeGroup(shape=self.upper_skin.edges[idy]) for idy in range(len(self.upper_skin.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_lower_skin(self):
        return MeshingFunc(part_class=self.lower_skin,
                           groups=[FaceGroup(shape=self.lower_skin.faces)] +
                                  [EdgeGroup(shape=self.lower_skin.edges)] +
                                  [FaceGroup(shape=[self.lower_skin.faces[0], self.lower_skin.faces[3]])] +
                                  [FaceGroup(shape=self.lower_skin.faces[idx]) for idx in range(len(self.lower_skin.faces))] +
                                  [EdgeGroup(shape=self.lower_skin.edges[idy]) for idy in range(len(self.lower_skin.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_front_spar(self):
        return MeshingFunc(part_class=self.front_spar,
                           groups=[FaceGroup(shape=self.front_spar.faces)] +
                                  [EdgeGroup(shape=self.front_spar.edges)] +
                                  [FaceGroup(shape=self.front_spar.faces[idx]) for idx in range(len(self.front_spar.faces))] +
                                  [EdgeGroup(shape=self.front_spar.edges[idy]) for idy in range(len(self.front_spar.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_rear_spar(self):
        return MeshingFunc(part_class=self.rear_spar,
                           groups=[FaceGroup(shape=self.rear_spar.faces)] +
                                  [EdgeGroup(shape=self.rear_spar.edges)] +
                                  [FaceGroup(shape=self.rear_spar.faces[idx]) for idx in range(len(self.rear_spar.faces))] +
                                  [EdgeGroup(shape=self.rear_spar.edges[idy]) for idy in range(len(self.rear_spar.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Part
    def meshed_upper_stringers(self):
        return MeshingFunc(part_class=self.upper_stringers,
                           groups=[FaceGroup(shape=self.upper_stringers.faces)] +
                                  [EdgeGroup(shape=self.upper_stringers.edges)] +
                                  [FaceGroup(shape=self.upper_stringers.faces[idx]) for idx in range(len(self.upper_stringers.faces))] +
                                  [EdgeGroup(shape=self.upper_stringers.edges[idy]) for idy in range(len(self.upper_stringers.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_lower_stringers(self):
        return MeshingFunc(part_class=self.lower_stringers,
                           groups=[FaceGroup(shape=self.lower_stringers.faces)] +
                                  [EdgeGroup(shape=self.lower_stringers.edges)] +
                                  [FaceGroup(shape=self.lower_stringers.faces[idx]) for idx in range(len(self.lower_stringers.faces))] +
                                  [EdgeGroup(shape=self.lower_stringers.edges[idy]) for idy in range(len(self.lower_stringers.edges))],
                           mesh_element_length=self.mesh_element_length)



    @Part
    def meshed_ribs_cp(self):
        return MeshingFunc(part_class=self.ribs_cp,
                           groups=[FaceGroup(shape=self.ribs_cp.faces)] +
                                  [EdgeGroup(shape=self.ribs_cp.edges)] +
                                  [FaceGroup(shape=self.ribs_cp.faces[idx]) for idx in range(len(self.ribs_cp.faces))] +
                                  [EdgeGroup(shape=self.ribs_cp.edges[idy]) for idy in range(len(self.ribs_cp.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Part
    def meshed_upper_skin_cp(self):
        return MeshingFunc(part_class=self.upper_skin_cp,
                           groups=[FaceGroup(shape=self.upper_skin_cp.faces)] +
                                  [EdgeGroup(shape=self.upper_skin_cp.edges)] +
                                  [FaceGroup(shape=self.upper_skin_cp.faces[idx]) for idx in range(len(self.upper_skin_cp.faces))] +
                                  [EdgeGroup(shape=self.upper_skin_cp.edges[idy]) for idy in range(len(self.upper_skin_cp.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Part
    def meshed_lower_skin_cp(self):
        return MeshingFunc(part_class=self.lower_skin_cp,
                           groups=[FaceGroup(shape=self.lower_skin_cp.faces)] +
                                  [EdgeGroup(shape=self.lower_skin_cp.edges)] +
                                  [FaceGroup(shape=self.lower_skin_cp.faces[idx]) for idx in range(len(self.lower_skin_cp.faces))] +
                                  [EdgeGroup(shape=self.lower_skin_cp.edges[idy]) for idy in range(len(self.lower_skin_cp.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Part
    def meshed_front_spar_cp(self):
        return MeshingFunc(part_class=self.front_spar_cp,
                           groups=[FaceGroup(shape=self.front_spar_cp.faces)] +
                                  [EdgeGroup(shape=self.front_spar_cp.edges)] +
                                  [FaceGroup(shape=self.front_spar_cp.faces[idx]) for idx in range(len(self.front_spar_cp.faces))] +
                                  [EdgeGroup(shape=self.front_spar_cp.edges[idy]) for idy in range(len(self.front_spar_cp.edges))],
                           mesh_element_length=self.mesh_element_length)

    @Part
    def meshed_rear_spar_cp(self):
        return MeshingFunc(part_class=self.rear_spar_cp,
                           groups=[FaceGroup(shape=self.rear_spar_cp.faces)] +
                                  [EdgeGroup(shape=self.rear_spar_cp.edges)] +
                                  [FaceGroup(shape=self.rear_spar_cp.faces[idx]) for idx in range(len(self.rear_spar_cp.faces))] +
                                  [EdgeGroup(shape=self.rear_spar_cp.edges[idy]) for idy in range(len(self.rear_spar_cp.edges))],
                           mesh_element_length=self.mesh_element_length)


    @Part
    def meshed_upper_stringers_cp(self):
        return MeshingFunc(part_class=self.upper_stringers_cp,
                           groups=[FaceGroup(shape=self.upper_stringers_cp.faces)] +
                                  [EdgeGroup(shape=self.upper_stringers_cp.edges)] +
                                  [FaceGroup(shape=self.upper_stringers_cp.faces[idx]) for idx in range(len(self.upper_stringers_cp.faces))] +
                                  [EdgeGroup(shape=self.upper_stringers_cp.edges[idy]) for idy in range(len(self.upper_stringers_cp.edges))],
                           mesh_element_length=self.mesh_element_length)
    @Part
    def meshed_lower_stringers_cp(self):
        return MeshingFunc(part_class=self.lower_stringers_cp,
                           groups=[FaceGroup(shape=self.lower_stringers_cp.faces)] +
                                  [EdgeGroup(shape=self.lower_stringers_cp.edges)] +
                                  [FaceGroup(shape=self.lower_stringers_cp.faces[idx]) for idx in range(len(self.lower_stringers_cp.faces))] +
                                  [EdgeGroup(shape=self.lower_stringers_cp.edges[idy]) for idy in range(len(self.lower_stringers_cp.edges))],
                           mesh_element_length=self.mesh_element_length)

    # Shell sections which assign material properties to different parts
    @Attribute
    def upper_inner_skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.upper_inner_skin_thickness)

    @Attribute
    def upper_outer_skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.upper_outer_skin_thickness)

    @Attribute
    def lower_inner_skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.lower_inner_skin_thickness)

    @Attribute
    def lower_outer_skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.lower_outer_skin_thickness)

    @Attribute
    def spar_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.spar_thickness)

    @Attribute
    def upper_stringers_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.upper_stringers_thickness)

    @Attribute
    def lower_stringers_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.lower_stringers_thickness)
    @Attribute
    def rib_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.rib_thickness)

    @Attribute
    def cp_skin_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.centre_section_skin_thickness)

    @Attribute
    def cp_rib_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.centre_section_rib_thickness)

    @Attribute
    def cp_spar_material_properties(self):
        return ShellSectionProperties(material=self.material, thickness=self.centre_section_spar_thickness)




# Adaptor to write the inp file

    @Attribute
    def my_abaqus_adaptor(self):
        my_obj = Adaptor()

        # Abaqus part: upper skin
        my_obj.process_2d_part(self.upper_skin,
        "S{n}R",  # the type of 2d surface
       [(self.meshed_upper_skin.mesh.subgrid[0], self.upper_inner_skin_material_properties)],
                    # (self.meshed_upper_skin.mesh.subgrid[3], self.upper_inner_skin_material_properties),
                    # (self.meshed_upper_skin.mesh.subgrid[6], self.upper_outer_skin_material_properties)],
        preferred_name=f"Upper_Skin"
        )
        # Abaqus part: lower skin
        my_obj.process_2d_part(self.lower_skin,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_lower_skin.mesh.subgrid[0], self.lower_inner_skin_material_properties)],
        #           [(self.meshed_lower_skin.mesh.subgrid[3], self.lower_inner_skin_material_properties),
        #           (self.meshed_lower_skin.mesh.subgrid[6], self.lower_outer_skin_material_properties)],
        preferred_name=f"Lower_Skin"
        )
        # Abaqus part:  front spar
        my_obj.process_2d_part(self.front_spar,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_front_spar.mesh.subgrid[0], self.spar_material_properties)],
        preferred_name=f"Front_spar"
        )
        # Abaqus part: rear spars
        my_obj.process_2d_part(self.rear_spar,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_rear_spar.mesh.subgrid[0], self.spar_material_properties)],
        preferred_name=f"Rear_spar"
        )
        # Abaqus part: upper_stringers
        # for i in range(len(self.upper_stringers.faces)):
        my_obj.process_2d_part(self.upper_stringers,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_upper_stringers.mesh.subgrid[0], self.upper_stringers_material_properties)],
        preferred_name=f"Upper_stringers"
        )
        # Abaqus part: lower stringers
        my_obj.process_2d_part(self.lower_stringers,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_lower_stringers.mesh.subgrid[0], self.lower_stringers_material_properties)],
        preferred_name=f"Lower_stringers"
        )
        # Abaqus part: ribs
        # my_obj.process_2d_part(self.ribs,
        # "S{n}R",  # the type of 2d surface
        # [(self.meshed_ribs.mesh.subgrid[0], self.rib_material_properties)],
        # preferred_name=f"Ribs_centre_section"
        # )

        # Abaqus part: centre section upper skin
        my_obj.process_2d_part(self.upper_skin_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_upper_skin_cp.mesh.subgrid[0], self.cp_skin_material_properties)],
        preferred_name=f"Upper_Skin_centre_section"
        )
        # Abaqus part: centre section lower skin
        my_obj.process_2d_part(self.lower_skin_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_lower_skin_cp.mesh.subgrid[0], self.cp_skin_material_properties)],
        preferred_name=f"Lower_Skin_centre_section"
        )
        # Abaqus part: centre section front spar
        my_obj.process_2d_part(self.front_spar_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_front_spar_cp.mesh.subgrid[0], self.cp_spar_material_properties)],
        preferred_name=f"Front_spar_centre_section"
        )
        # Abaqus part: centre section rear spar
        my_obj.process_2d_part(self.rear_spar_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_rear_spar_cp.mesh.subgrid[0], self.cp_spar_material_properties)],
        preferred_name=f"Rear_spar_centre_section"
        )
        # Abaqus part: centre section ribs
        my_obj.process_2d_part(self.ribs_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_ribs_cp.mesh.subgrid[0], self.cp_rib_material_properties)],
        preferred_name=f"Ribs_centre_section"
        )
        my_obj.process_2d_part(self.upper_stringers_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_upper_stringers_cp.mesh.subgrid[0], self.upper_stringers_material_properties)],
        preferred_name=f"Upper_stringers_centre_section"
        )
        # Abaqus part: lower stringers
        my_obj.process_2d_part(self.lower_stringers_cp,
        "S{n}R",  # the type of 2d surface
        [(self.meshed_lower_stringers_cp.mesh.subgrid[0], self.lower_stringers_material_properties)],
        preferred_name=f"Lower_stringers_centre_section"
        )
        #U=upper
        #L=lower
        #I=inner
        #O=outer
        #F=front
        #R=rear
        #cp=centrepiece

        # Connection between upper skin flange and inner rear spar
        UIR_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[1]),
                                                               "SPOS")

        UIF_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[2]),
                                                               "SPOS")

        L_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[2]),
                                                               "SPOS")
        UOR_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[4]),
                                                               "SPOS")

        UOF_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[5]),
                                                               "SPOS")

        LIR_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[1]),
                                                               "SPOS")

        LIF_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[2]),
                                                               "SPOS")

        LOR_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[4]),
                                                               "SPOS")

        LOF_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[5]),
                                                               "SPOS")

        UIR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[0]))

        IR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[1]))

        LIR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[0].edges[2]))

        UOR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1].edges[0]))

        LOR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar,
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1]),
                                                    self.meshed_rear_spar.mesh.get_subgrid(self.rear_spar.faces[1].edges[2]))

        UIF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[0]))

        IF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[1]))

        LIF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[0].edges[2]))

        UOF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1].edges[0]))

        LOF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar,
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1]),
                                                    self.meshed_front_spar.mesh.get_subgrid(self.front_spar.faces[1].edges[2]))


        cp_UF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar_cp,
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0]),
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0].edges[0]))

        cp_LF_spar_tie = my_obj.process_face_surface_with_edges(self.front_spar_cp,
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0]),
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0].edges[2]))

        cp_UR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar_cp,
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0]),
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0].edges[0]))

        cp_LR_spar_tie = my_obj.process_face_surface_with_edges(self.rear_spar_cp,
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0]),
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0].edges[2]))

        cp_UF_skin_tie = my_obj.process_face_surface_with_edges(self.upper_skin_cp,
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0]),
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0].edges[0]))

        cp_UR_skin_tie = my_obj.process_face_surface_with_edges(self.upper_skin_cp,
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0]),
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0].edges[2]))

        cp_LF_skin_tie = my_obj.process_face_surface_with_edges(self.lower_skin_cp,
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0]),
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0].edges[0]))

        cp_LR_skin_tie = my_obj.process_face_surface_with_edges(self.lower_skin_cp,
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0]),
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0].edges[2]))

        cp_upper_skin_tie = my_obj.process_element_based_surface(self.upper_skin_cp,
                                                          self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0]),
                                                               "SPOS")

        cp_lower_skin_tie = my_obj.process_element_based_surface(self.lower_skin_cp,
                                                          self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0]),
                                                               "SPOS")

        cp_front_spar_tie = my_obj.process_element_based_surface(self.front_spar_cp,
                                                          self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0]),
                                                               "SPOS")

        cp_rear_spar_tie = my_obj.process_element_based_surface(self.rear_spar_cp,
                                                          self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0]),
                                                               "SPOS")

        cp_UI_skin_edge_tie = my_obj.process_face_surface_with_edges(self.upper_skin_cp,
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0]),
                                                    self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0].edges[1]))

        cp_LI_skin_edge_tie = my_obj.process_face_surface_with_edges(self.lower_skin_cp,
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0]),
                                                    self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0].edges[1]))

        cp_RI_spar_edge_tie = my_obj.process_face_surface_with_edges(self.rear_spar_cp,
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0]),
                                                    self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0].edges[1]))

        cp_FI_spar_edge_tie = my_obj.process_face_surface_with_edges(self.front_spar_cp,
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0]),
                                                    self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0].edges[1]))

        UI_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[0]),
                                                               "SPOS")

        UO_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[3]),
                                                               "SPOS")

        U_skin_tie = my_obj.process_element_based_surface(self.upper_skin,
                                                          self.meshed_upper_skin.mesh.subgrid[2],
                                                               "SPOS")

        L_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.subgrid[2],
                                                               "SPOS")

        LI_skin_tie = my_obj.process_element_based_surface(self.lower_skin,
                                                          self.meshed_lower_skin.mesh.get_subgrid(self.lower_skin.faces[0]),
                                                               "SPOS")

        upper_stringers_tie = []
        lower_stringers_tie = []

        for i in range(int(len(self.upper_stringers.faces) / 2)):
            upper_stringers_tie.append(my_obj.process_element_based_surface(self.upper_stringers,
                                                    self.meshed_upper_stringers.mesh.get_subgrid(self.upper_stringers.faces[2*i])))
        for i in range(int(len(self.lower_stringers.faces) / 2)):
            lower_stringers_tie.append(my_obj.process_element_based_surface(self.lower_stringers,
                                                    self.meshed_lower_stringers.mesh.get_subgrid(self.lower_stringers.faces[2*i])))

        upper_stringers_cp_tie = []
        lower_stringers_cp_tie = []

        for i in range(int(len(self.upper_stringers_cp.faces) / 2)):
            upper_stringers_cp_tie.append(my_obj.process_element_based_surface(self.upper_stringers_cp,
                                                    self.meshed_upper_stringers_cp.mesh.get_subgrid(self.upper_stringers_cp.faces[2*i])))
        for i in range(int(len(self.lower_stringers_cp.faces) / 2)):
            lower_stringers_cp_tie.append(my_obj.process_element_based_surface(self.lower_stringers_cp,
                                                    self.meshed_lower_stringers_cp.mesh.get_subgrid(self.lower_stringers_cp.faces[2*i])))


        cp_U_ribs_tie = []
        cp_L_ribs_tie = []
        cp_F_ribs_tie = []
        cp_R_ribs_tie = []
        for i in range(len(self.ribs_cp.faces)):
            cp_U_ribs_tie.append(my_obj.process_face_surface_with_edges(self.ribs_cp,
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i]),
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i].edges[0])))
            cp_L_ribs_tie.append(my_obj.process_face_surface_with_edges(self.ribs_cp,
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i]),
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i].edges[3])))
            cp_F_ribs_tie.append(my_obj.process_face_surface_with_edges(self.ribs_cp,
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i]),
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i].edges[2])))
            cp_R_ribs_tie.append(my_obj.process_face_surface_with_edges(self.ribs_cp,
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i]),
                                                    self.meshed_ribs_cp.mesh.get_subgrid(self.ribs_cp.faces[i].edges[1])))


        # Wing upper connections
        my_obj.process_tie(UIR_skin_tie, UIR_spar_tie, "Surface to Surface")
        my_obj.process_tie(UOR_skin_tie, UOR_spar_tie, "Surface to Surface")
        my_obj.process_tie(UIF_skin_tie, UIF_spar_tie, "Surface to Surface")
        my_obj.process_tie(UOF_skin_tie, UOF_spar_tie, "Surface to Surface")
        # Wing lower connections
        my_obj.process_tie(LIR_skin_tie, LIR_spar_tie, "Surface to Surface")
        my_obj.process_tie(LOR_skin_tie, LOR_spar_tie, "Surface to Surface")
        my_obj.process_tie(LIF_skin_tie, LIF_spar_tie, "Surface to Surface")
        my_obj.process_tie(LOF_skin_tie, LOF_spar_tie, "Surface to Surface")
        # Centre section connections
        my_obj.process_tie(cp_UF_skin_tie, cp_UF_spar_tie, "Surface to Surface")
        my_obj.process_tie(cp_LF_skin_tie, cp_LF_spar_tie, "Surface to Surface")
        my_obj.process_tie(cp_UR_skin_tie, cp_UR_spar_tie, "Surface to Surface")
        my_obj.process_tie(cp_LR_skin_tie, cp_LR_spar_tie, "Surface to Surface")
        # Wing to centre section connections
        my_obj.process_tie(UI_skin_tie, cp_UI_skin_edge_tie, "Surface to Surface")
        my_obj.process_tie(LI_skin_tie, cp_LI_skin_edge_tie, "Surface to Surface")
        # my_obj.process_tie(cp_front_spar_tie, IF_spar_tie, "Surface to Surface")
        # my_obj.process_tie(cp_rear_spar_tie, IR_spar_tie, "Surface to Surface")

        # Stringer ties to upper and lower skins
        for i in range(int(len(self.upper_stringers.faces) / 2)):
            my_obj.process_tie(upper_stringers_tie[i], U_skin_tie, "Surface to Surface")
        for i in range(int(len(self.lower_stringers.faces) / 2)):
            my_obj.process_tie(lower_stringers_tie[i], L_skin_tie, "Surface to Surface")



        # Boundary conditions:
        # At the centreline of the (full) centre section
        # And, at the nodes of the upper surface, at the interface between the root chord and the centre section.

        my_obj.process_boundary_condition(self.upper_skin, self.meshed_upper_skin.mesh.get_subgrid(self.upper_skin.faces[0].edges[1]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.upper_skin_cp, self.meshed_upper_skin_cp.mesh.get_subgrid(self.upper_skin_cp.faces[0].edges[3]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.lower_skin_cp, self.meshed_lower_skin_cp.mesh.get_subgrid(self.lower_skin_cp.faces[0].edges[3]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.front_spar_cp, self.meshed_front_spar_cp.mesh.get_subgrid(self.front_spar_cp.faces[0].edges[3]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)
        my_obj.process_boundary_condition(self.rear_spar_cp, self.meshed_rear_spar_cp.mesh.get_subgrid(self.rear_spar_cp.faces[0].edges[3]).nodes,
                                    U1=0, U2=0, U3=0, UR1=0, UR2=0, UR3=0)


        return my_obj

    # Filtering of mesh nodes based on where the engine is
    @Attribute
    def engine_mass_nodes(self):
        nodes_per_engine = []
        nodes_of_all_engines = []
        for n in range(len(self.engine_position)):
            for i in range(len(self.spanwise_nodes[1])):
                if abs(self.engine_position[n] - self.spanwise_nodes[1][i][1]) <= self.mesh_element_length:
                    nodes_per_engine.append(self.spanwise_nodes[1][i])
                else:
                    continue
            nodes_of_all_engines.append(nodes_per_engine)
            nodes_per_engine = []
        return nodes_of_all_engines

    # Filtering mesh nodes based on their Y coordinate.
    # Nodes are arranged based in rows with the same Y coordinates.
    @Attribute
    def spanwise_nodes(self):
        upper_surface_nodes_y_coord = []
        lower_surface_nodes_y_coord = []

        for i in range(len(self.meshed_upper_skin.mesh.subgrid[2].nodes)):
            upper_surface_nodes_y_coord.append(self.meshed_upper_skin.mesh.subgrid[2].nodes[i])
            lower_surface_nodes_y_coord.append(self.meshed_lower_skin.mesh.subgrid[2].nodes[i])
        upper_surface_nodes_y_coord.sort(key=lambda x: x[1])
        lower_surface_nodes_y_coord.sort(key=lambda x: x[1])
        return [upper_surface_nodes_y_coord, lower_surface_nodes_y_coord]

    # Here the loads on the wing are defined.
    # The lift distribution is triangular and is calculated based on the total force.
    # F_total is the load factor * aircraft mass * gravity.
    # Then force is applied to each row of nodes. At the root force is the highest, at the tip it is zero
    @Attribute
    def loads(self):

        n_sections = round((0.5*self.parent.my_wing.span- self.parent.my_wing.width_centerpiece)/self.mesh_element_length)
        span_sections = np.linspace(self.spanwise_nodes[0][0][1],
                                    self.spanwise_nodes[0][-1][1],
                                    n_sections)
        node_sets = []
        node_per_section = []
        for s in range(len(span_sections)-1):
            for i in range(len(self.spanwise_nodes[0])):
                if self.spanwise_nodes[0][i][1] <= span_sections[s+1] and self.spanwise_nodes[0][i][1] >= span_sections[s]:
                    node_per_section.append(self.spanwise_nodes[0][i])
                else:
                    continue
            node_sets.append(node_per_section)
            node_per_section = []

        F_total = 0.5 * self.aircraft_mass * self.load_factor * self.Gravity
        F_y = []
        F_num = 0
        n_x_nodes = []
        n_y_nodes = []
        for i in range(len(span_sections)):
            F_num = F_num + (1 - (span_sections[i] / span_sections[-1]))
        F_0 = F_total / F_num
        for i in range(len(span_sections)):
            F_y.append(F_0 * (1 - (span_sections[i] / span_sections[-1])))

        for i in range(len(node_sets)):
            n_x_nodes.append(len(node_sets[i]))

        F_x = [m/n for m, n in zip(F_y, n_x_nodes)]

        node_lift_load = []
        for i in range(len(node_sets)):
            node_set = self.my_abaqus_adaptor.add_set(node_sets[i], part=self.upper_skin, preferred_name="loadpoints")
            # cload.append(CLoad(nodes=[], node_sets=[node_set], F3=F_x[i]))
            node_lift_load.append(CLoad(nodes=[], node_sets=[node_set], F3=F_y[i]))
            # element_load.append(DLoad(elements=[], element_sets=[node_set], load_type='P', magnitude=F_y[i]))

        node_engine_load = []
        for n in range(len(self.engine_position)):
            engine_node_set = self.my_abaqus_adaptor.add_set(self.engine_mass_nodes[n], part=self.lower_skin, preferred_name=f"engine_{n}_mass")
            node_engine_load.append(CLoad(nodes=[], node_sets=[engine_node_set], F3=-self.engine_mass*self.Gravity))

        return [node_lift_load, node_engine_load], [span_sections, node_per_section, node_sets, n_x_nodes, F_total, F_0, F_y, F_x, F_num]



    # Defining output field for abaqus
    @property
    def my_outputs(self):
        return [FieldOutput(name="field-output"), HistoryOutput(name="history-output")]

    # Defining a static analysis
    @property
    def my_step(self):
        return Step(name="analysis1",
                    linear=True,
                    step_options=[Static(time_period=1.,
                                         minimum_time_increment=1e-15,
                                         maximum_time_increment=0.1,
                                         initial_time_increment=0.01)],
                    loads=self.loads[0][0] + self.loads[0][1], #load from lift distribution and from engine(s) mass
                    boundary_conditions=[],
                    outputs=self.my_outputs,
                    interactions=[])

    # Write inp file
    @Attribute
    def my_inp_writer(self):
        return Writer(adaptor=self.my_abaqus_adaptor, steps=[self.my_step])

if __name__ == '__main__':
    from parapy.gui import display

    my_obj = AbaqusINPwriter()
    my_obj.my_inp_writer.write('output//wing_box.inp')
    display(my_obj)

