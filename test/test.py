__author__ = 'caoyawen'

import unittest
from pathlib import Path
from git_cleaner.cleaner import ConfigYAML, CollectPwd
from pprint import pprint as pp


class CollectAllFitFile:
    def __init__(self):
        self.all_fit_file = []

    def __call__(self, config: ConfigYAML):
        self.all_fit_file += config.fit_file_list

class CollectAllFitDir:
    def __init__(self):
        self.all_fit_dir = []

    def __call__(self, config: ConfigYAML):
        self.all_fit_dir += config.fit_dir


class MyTestCase(unittest.TestCase):
    config_file = Path(__file__).parent.joinpath("cleaner.yaml")
    blank_config_file = Path(__file__).parent.joinpath("cleaner_blank.yaml")
    real_config = Path(__file__).parent.parent.joinpath("cleaner_test.yaml")

    def test_load_confgi(self):
        config_file_parent = self.config_file.parent
        cy = ConfigYAML(str(self.config_file), True)
        cp = CollectPwd()
        # pp(cy.config)
        cy.enum_config(cp)
        # pp("collect config file's pwd is {pwd_list}".format(pwd_list=cp.pwd_list))
        self.assertEqual([str(config_file_parent.joinpath("append")), str(config_file_parent)], cp.pwd_list)
        self.assertEqual(
            ['test.py',
             # 'special_dir/data.txt',
             # 'special_dir/sub_dir/data.txt',
             'contain_special_data.txt',
             ],
            cy.fit_file_list
        )
        self.assertEqual(["special_dir"], cy.fit_dir)
        caff = CollectAllFitFile()
        cy.enum_config(caff)
        # pp(caff.all_fit_file)
        self.assertEqual(caff.all_fit_file,
                         [
                             # 'special_dir/sub_dir/data.txt',
                             'contain_special_data.txt',
                             'test.py',
                             # 'special_dir/data.txt',
                             # 'special_dir/sub_dir/data.txt',
                             'contain_special_data.txt'
                         ])
        cafd = CollectAllFitDir()
        cy.enum_config(cafd)
        self.assertEqual(cafd.all_fit_dir,
                         [
                             "special_dir/sub_dir",
                             "special_dir",
                         ])
        # cy.enum_config(lambda config: print("{name}'s handle file list:{handle_file_list}".format(
        #     name=config.name, handle_file_list=config.handle_file_list)))
        # print("{name}'s add by handle dir:{abhd}".format(name=cy.name, abhd=cy.add_by_handle_dir))
        # print("{name}'s base exclude path:{exclude_path}".format(name=cy.name, exclude_path=cy.base_exclude_path))

    def test_blank_conig(self):
        cy = ConfigYAML(str(self.blank_config_file), True)
        print(cy.fit_dir)
        print(cy.fit_file_list)

    def test_real_git_cleaner(self):
        cy = ConfigYAML(str(self.real_config), True)
        # print(cy.fit_dir)
        cy.enum_config(lambda config:config.clean_git())
        # cy.clean_git()


if __name__ == '__main__':
    unittest.main()
