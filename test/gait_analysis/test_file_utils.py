import copy
import numpy
from unittest import TestCase
from gait_analysis import file_utils


class TestC3dFileWrapper(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls.factory = file_utils.FileHandlerFactory()
        cls.c3d_wrapper = cls.factory.get_c3d_file_handler(cls.path)

    def test_set_c3d_file(self):
        # Create new c3d file copy to alternate for test
        c3d_file = copy.deepcopy(self.c3d_wrapper.file)

        # Adapt  c3d file copy with new point labels
        test_points = ["TestPoint1", "TestPoint2", "TestPoint3"]
        c3d_file[file_utils.C3D_FIELD_PARAMETER][
            file_utils.C3D_FIELD_PARAMETER_POINT][file_utils.C3D_FIELD_PARAMETER_LABELS][
            file_utils.C3D_FIELD_VALUE] = test_points

        self.c3d_wrapper.file = c3d_file
        self.assertEqual(c3d_file, self.c3d_wrapper.file, "c3d file not allocated in C3dFileWrapper")
        self.assertEqual(test_points, self.c3d_wrapper.get_point_labels(),
                         "point_labels not newly allocated in C3dFileWrapper")

    def test_get_points_good_case(self):
        marker_one_label = 'RASIS'
        marker_two_label = 'LPSIS'

        points_1 = self.c3d_wrapper.get_points([marker_one_label, marker_two_label])

        self.assertEqual(2, len(points_1.keys()),
                         "Not %s, %s not extracted by default from C3dFileWrapper" % (
                         marker_one_label, marker_two_label))
        self.assertEqual(3, len(points_1[marker_one_label]), "Not x y z extracted by default from C3dFileWrapper")
        self.assertEqual(18002, len(points_1[marker_two_label]['x']),
                         "Not x y z extracted by default from C3dFileWrapper")
        self.assertTrue((points_1[marker_one_label]['x'] - points_1[marker_two_label]['x']).any())

        points_2 = self.c3d_wrapper.get_points([marker_two_label, marker_one_label], ["z", "x", "y"])
        self.assertEqual(2, len(points_2.keys()),
                         "Not %s, %s not extracted by default from C3dFileWrapper" % (
                         marker_two_label, marker_one_label))

        self.assertEqual(3, len(points_2[marker_two_label]), "Not z x y extracted by default from C3dFileWrapper")

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
        platform_labels = self.c3d_wrapper.get_platform_labels()
        forces = self.c3d_wrapper.get_platform_forces(platform_labels)
        self.assertEqual(2, len(forces.keys()), "More than two platforms!")
        self.assertEqual(3, len(forces[platform1_label].keys()), "More than three directions!")
        self.assertEqual(180020, len(forces[platform1_label]['x']), "More expected frames!")

    def test_get_platform_moments(self):
        platform1_label = "Motekforce Link Force Plate [1]"
        platform_labels = self.c3d_wrapper.get_platform_labels()
        moments = self.c3d_wrapper.get_platform_moments(platform_labels)
        self.assertEqual(2, len(moments.keys()), "More than two platforms!")
        self.assertEqual(3, len(moments[platform1_label].keys()), "More than three directions!")
        self.assertEqual(180020, len(moments[platform1_label]['x']), "More expected frames!")

    def test_get_platform_cop(self):
        platform1_label = "Motekforce Link Force Plate [1]"
        platform_labels = self.c3d_wrapper.get_platform_labels()
        cops = self.c3d_wrapper.get_platform_cop(platform_labels)
        self.assertEqual(2, len(cops.keys()), "More than two platforms!")
        self.assertEqual(3, len(cops[platform1_label].keys()),  "More than three directions!")
        self.assertEqual(180020, len(cops[platform1_label]['x']), "More expected frames!")

    def test_get_camera_frame_rate(self):
        self.assertEqual(100, self.c3d_wrapper.get_camera_frame_rate(),)
        self.assertEqual(numpy.float64, type(self.c3d_wrapper.get_camera_frame_rate()), )

    def test_get_subject(self):
        self.assertEqual(self.c3d_wrapper.get_subject(), "Stest001")
        self.assertEqual(str, type(self.c3d_wrapper.get_subject()),)

    def test_get_platform_frame_rate(self):
        self.assertEqual(1000, self.c3d_wrapper.get_platform_frame_rate(),)
        self.assertEqual(numpy.float64, type(self.c3d_wrapper.get_platform_frame_rate()))

    def test_get_events(self):
        events = self.c3d_wrapper.get_events()


