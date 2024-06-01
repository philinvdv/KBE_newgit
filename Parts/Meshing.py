from parapy.geom import *
from math import radians
from parapy.core import Input, Attribute, Part, full_path
from parapy.geom import (Box, Cylinder, FusedSolid, GeomBase)
from parapy.mesh import FaceGroups, FaceGroup
from parapy.mesh.salome import Mesh, Tetra, Quad, TriSimple
from parapy.mesh.core.groups import FaceGroup
from parapy.mesh.salome import FixedLength, Mesh, Quad, Tri, Tetra
from parapy.core import *
from parapy.mesh import Controls, Groups
from parapy.mesh.salome import Mesh

from parapy.mesh.salome.controls import (ProjectedFace, TriMefisto, Hexa,
                                         Arithmic, FixedStartEndLength,
                                         FixedNumber, FixedPoints,
                                         MaxDeflection, MaxLength)
from parapy.mesh.salome.netgen import (TriSimple, Tetra, TetraSimple)


class MeshingFunc(Base):
    part_class = Input()
    n_mesh_points = Input(30)
    mesh_element_length = Input(0.5)
    hide_mesh = Input(False)
    groups=Input([])
    @Attribute
    def path_to_part(self):
        return self.part_class

    @Attribute
    def face_groups(self):
        return self.groups

    # @Attribute
    # def shape_faces_sorted(self):
    #     return sorted(self.shape.faces, key=lambda f: f.uv_center_point.z)
    #
    # @Part
    # def inlet(self):
    #     return FaceGroup(self.shape_faces_sorted, 'skin_surface')

    @Part
    def controls(self):
        return MyControls(path_to_part=self.path_to_part,
                          n_mesh_points=self.n_mesh_points,
                          mesh_element_length=self.mesh_element_length)

    # @Part
    # def groups(self):
    #     return MyGroups(shape=self.shape)
    #
    @Part
    def mesh(self):
        return Mesh(shape_to_mesh=self.path_to_part,
                    controls=self.controls,
                    groups=self.face_groups)


class MyControls(Controls):
    path_to_part = Input()
    n_mesh_points = Input()
    mesh_element_length = Input()
    hide_mesh = Input()
    # @Part
    # def control_1d(self):
    #     return FixedNumber(shape=self.path_to_part,
    #                        no=self.n_mesh_points)

    @Part
    def control_1d(self):
        return FixedLength(shape=self.path_to_part,
                           length=self.mesh_element_length)

    # @Part
    # def control_1d_edge(self):
    #     return MaxLength(shape=self.path_to_part,
    #                      length=0.1)

    # @Part
    # def control_1d_side_edge(self):
    #     return MaxDeflection(shape=self.path_to_part,
    #                          deflection=0.1)

    # @Part
    # def control_2d(self):
    #     return Tri(shape=self.path_to_part)

    @Part
    def control_2d(self):
        return Quad(shape=self.path_to_part)

    # @Part
    # def control_1d_edges(self):
    #     return FixedNumber(shape=self.path_to_part.edges,
    #                        no=self.n_mesh_points)

class MyGroups(Groups):
    path_to_part = Input()

    # @Part
    # def wing_faces(self):
    #     """Side faces of the box"""
    #     return FaceGroup(shape=self.shape.skin_face,
    #                      label="sides")



if __name__ == '__main__':
    from parapy.gui import display
    obj = MeshingFunc()
    display(obj)
