import copy
from unittest import TestCase

from ezc3d import c3d

import file_utils


class TestC3dFileWrapper(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        path = "test/data/test.c3d"
        cls.c3d_file = c3d(path, extract_forceplat_data=True)

    def setUp(self):
        self.c3d_wrapper = file_utils.C3dFileWrapper(self.c3d_file)

    def test_c3d_file(self):
        self.assertEqual(self.c3d_wrapper.c3d_file, self.c3d_file)

    def test_set_c3d_file(self):
        # Load labels in wrapper-cache
        self.c3d_wrapper.get_platform_labels
        self.c3d_wrapper.get_point_labels

        # Create new c3d file copy to alternate for test
        c3d_file = copy.deepcopy(self.c3d_file)

        # Adapt  c3d file copy with new point labels
        test_points = {"TestPoint1": 0, "TestPoint2": 1, "TestPoint3": 2}
        c3d_file[file_utils.C3D_FIELD_PARAMETER][
            file_utils.C3D_FIELD_PARAMETER_POINT][file_utils.C3D_FIELD_PARAMETER_LABELS][
            file_utils.C3D_FIELD_VALUE] = list(test_points.keys())

        self.c3d_wrapper.c3d_file = c3d_file
        self.assertEqual(c3d_file, self.c3d_wrapper.c3d_file, "c3d file not allocated in C3dFileWrapper")
        self.assertEqual(self.c3d_wrapper.get_point_labels, test_points,
                         "point_labels not newly allocated in C3dFileWrapper")

    def test_get_points_good_case(self):
        marker_one_label = 'RASIS'
        marker_two_label = 'LPSIS'

        points_1 = self.c3d_wrapper.get_points([marker_one_label, marker_two_label])

        self.assertEqual(len(points_1.keys()), 2,
                         "Not %s, %s not extracted by default from C3dFileWrapper" % (
                         marker_one_label, marker_two_label))
        self.assertEqual(len(points_1[marker_one_label]), 3, "Not x y z extracted by default from C3dFileWrapper")
        self.assertEqual(len(points_1[marker_two_label]['x']), 18002,
                         "Not x y z extracted by default from C3dFileWrapper")
        self.assertTrue((points_1[marker_one_label]['x'] - points_1[marker_two_label]['x']).any())

        points_2 = self.c3d_wrapper.get_points([marker_two_label, marker_one_label], ["z", "x", "y"])
        self.assertEqual(len(points_2.keys()), 2,
                         "Not %s, %s not extracted by default from C3dFileWrapper" % (
                         marker_two_label, marker_one_label))

        self.assertEqual(len(points_2[marker_two_label]), 3, "Not z x y extracted by default from C3dFileWrapper")

        # Check if there is a different in the two extracted point dataFrame
        self.assertFalse((points_1[marker_one_label]['x'] - points_2[marker_one_label]['x']).any(),
                         "%s x not equal in two extractions from C3dFileWrapper" % marker_one_label)
        self.assertFalse((points_1[marker_two_label]['x'] - points_2[marker_two_label]['x']).any(),
                         "%s x not equal in two extractions from C3dFileWrapper" % marker_two_label)
        self.assertFalse((points_1[marker_one_label]['z'] - points_2[marker_one_label]['z']).any(),
                         "%s z not equal in two extractions from C3dFileWrapper" % marker_one_label)
        self.assertFalse((points_1[marker_two_label]['z'] - points_2[marker_two_label]['z']).any(),
                         "%s z not equal in two extractions from C3dFileWrapper" % marker_two_label)
        self.assertFalse((points_1[marker_one_label]['y'] - points_2[marker_one_label]['y']).any(),
                         "%s y not equal in two extractions from C3dFileWrapper" % marker_one_label)
        self.assertFalse((points_1[marker_two_label]['y'] - points_2[marker_two_label]['y']).any(),
                         "%s y not equal in two extractions from C3dFileWrapper" % marker_two_label)

    def test_get_platform_forces(self):
        platform1_label = "Motekforce Link Force Plate [1]"
        platform_labels = self.c3d_wrapper.get_platform_labels
        forces = self.c3d_wrapper.get_platform_forces(platform_labels)
        self.assertEqual(len(forces), 2, "More than two platforms!")
        self.assertEqual(len(forces[platform1_label]), 3, "More than three directions!")
        self.assertEqual(len(forces[platform1_label]['x']), 180020, "More expected frames!")

    def test_get_platform_forces(self):
        platform1_label = "Motekforce Link Force Plate [1]"
        platform_labels = self.c3d_wrapper.get_platform_labels
        moments = self.c3d_wrapper.get_platform_moments(platform_labels)
        self.assertEqual(len(moments), 2, "More than two platforms!")
        self.assertEqual(len(moments[platform1_label]), 3, "More than three directions!")
        self.assertEqual(len(moments[platform1_label]['x']), 180020, "More expected frames!")

    def test_get_platform_cop(self):
        platform1_label = "Motekforce Link Force Plate [1]"
        platform_labels = self.c3d_wrapper.get_platform_labels
        cops = self.c3d_wrapper.get_platform_cop(platform_labels)
        self.assertEqual(len(cops), 2, "More than two platforms!")
        self.assertEqual(len(cops[platform1_label]), 3, "More than three directions!")
        self.assertEqual(len(cops[platform1_label]['x']), 180020, "More expected frames!")
