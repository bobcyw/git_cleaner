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


class MyTestCase(unittest.TestCase):
    config_file = Path(__file__).parent.joinpath("clean.yaml")

    def test_load_confgi(self):
        config_file_parent = self.config_file.parent
        cy = ConfigYAML(str(self.config_file), True)
        cp = CollectPwd()
        # pp(cy.config)
        cy.enum_config(cp)
        # pp("collect config file's pwd is {pwd_list}".format(pwd_list=cp.pwd_list))
        self.assertEqual([str(config_file_parent.joinpath("append")), str(config_file_parent)], cp.pwd_list)
        self.assertEqual(
            [str(config_file_parent.joinpath('test.py')),
             str(config_file_parent.joinpath('special_dir/data.txt')),
             str(config_file_parent.joinpath('special_dir/sub_dir/data.txt')),
             str(config_file_parent.joinpath('contain_special_data.txt')),
             # str(config_file_parent.joinpath('test.py'))
             ],
            cy.fit_file_list
        )
        # print(cy.add_by_handle_file)
        # print(cy.add_by_handle_dir)
        # print(cy.add_by_characteristic)
        all_fit_file_list = []
        caff = CollectAllFitFile()
        cy.enum_config(caff)
        # pp(caff.all_fit_file)
        self.assertEqual(caff.all_fit_file,
                         [
                             str(config_file_parent.joinpath('append/special_dir/sub_dir/data.txt')),
                             str(config_file_parent.joinpath('append/contain_special_data.txt')),
                             str(config_file_parent.joinpath('test.py')),
                             str(config_file_parent.joinpath('special_dir/data.txt')),
                             str(config_file_parent.joinpath('special_dir/sub_dir/data.txt')),
                             str(config_file_parent.joinpath('contain_special_data.txt'))
                         ])
        # cy.enum_config(lambda config: print("{name}'s handle file list:{handle_file_list}".format(
        #     name=config.name, handle_file_list=config.handle_file_list)))
        # print("{name}'s add by handle dir:{abhd}".format(name=cy.name, abhd=cy.add_by_handle_dir))
        # print("{name}'s base exclude path:{exclude_path}".format(name=cy.name, exclude_path=cy.base_exclude_path))

    def test_exclude_dir(self):
        cy = ConfigYAML(str(self.config_file), True)
        # enum_config()


if __name__ == '__main__':
    unittest.main()
