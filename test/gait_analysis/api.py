import unittest

from gait_analysis.api import ConfigProvider

SETTINGS_FILE = "settings/hbm_pig.yaml"


class ConfigTests(unittest.TestCase):
    def test_read_config(self):
        configs = ConfigProvider()
        configs.read_configs(SETTINGS_FILE)
        self.assertEqual(configs.MARKER_MAPPING.left_heel.value, "LHEE")

    def test_get_translated_label(self):
        configs = ConfigProvider()
        configs.read_configs(SETTINGS_FILE)
        self.assertEqual(configs.MARKER_MAPPING.left_heel.value, "LHEE")


if __name__ == '__main__':
    unittest.main()
