from yuantao_fmk.impl.run_pkg_installer.cann_community_installer import CANNCommunityInstaller
import unittest

class TestCANNCommunityInstaller(unittest.TestCase):
    def test_get_latest_version(self):
        installer = CANNCommunityInstaller(None, "910b", ["toolkit"])
        print(installer.get_latest_version())

    def test_get_default_resource_tags(self):
        installer = CANNCommunityInstaller(None, "910b", ["toolkit"])
        print(installer.get_default_resource_tags())
    
    def test_install_resource(self):
        installer = CANNCommunityInstaller(None, "910b", ["toolkit"])
        installer.download_and_install_all_resource("/home/yuantao/Ascend/"+installer.version)

if __name__ == "__main__":
    unittest.main()