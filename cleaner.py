__author__ = 'caoyawen'
import yaml
import os
from pathlib import Path
import subprocess
import pyparsing


class ConfigYAML:
    def __init__(self, fn: str, debug=False):
        """
        初始化
        :param fn: 指定的配置文件，每个配置文件管理对应目录以及子目录，子配置文件在父配置文件中时，子配置文件的作用范围覆盖父配置文件，而非继承
        :param debug: 用于调试时查看内部状态
        :return:
        """
        self.fn = fn
        self.debug = debug
        if debug:
            self.handle_file_list = []
        self.config = self.load_config()
        self.name = self.config.get("name", "缺省配置文件")
        self.handle_config()

    def clean_git(self):
        branch = self.config.get("branch", "")
        old_branch = current_branch(self.pwd)
        if branch:
            cmd_line = "/usr/bin/git checkout {branch}".format(branch=branch)
            _, error = call_cmd_with_status(cmd_line, self.pwd)
            if error:
                print(cmd_line)
                print(error)
        for file in self.fit_file_list:
            cmd_line = "/usr/bin/git filter-branch -f --index-filter 'git rm --cached --ignore-unmatch {file}' HEAD".format(file=file)
            _, error = call_cmd_with_status(cmd_line, self.pwd)
            if error:
                print(cmd_line)
                print(error)
        for special_path in self.fit_dir:
            cmd_line = "/usr/bin/git filter-branch -f --index-filter 'git rm -r --cached --ignore-unmatch {path}' HEAD".format(path=special_path)
            _, error = call_cmd_with_status(cmd_line, self.pwd)
            if error:
                print(cmd_line)
                print(error)

        cmd_line = "/usr/bin/git checkout {old_branch}".format(old_branch=old_branch)
        _, error = call_cmd_with_status(cmd_line, self.pwd)
        if error:
            print(cmd_line)
            print(error)


    @property
    def pwd(self)->str:
        return self.config["pwd"]

    @property
    def base_exclude_path(self):
        """
        基础需要排除的目录和文件，包括自己，子配置文件的目录
        :return:
        """
        cp = CollectPwd()
        self.enum_config(cp)
        exclude_dir = cp.pwd_list
        exclude_dir.remove(self.pwd)
        exclude_dir.append(self.fn)
        return exclude_dir

    def load_config(self)->dict:
        """
        载入配置文件
        :param fn: 指定的目录
        :return: dict
        """
        config_p = Path(self.fn)
        content = config_p.read_bytes().decode()
        clean_config = yaml.load(content)
        if not clean_config:
            clean_config = {}
        # 解析得到工作路径
        pwd = str(config_p.parent)
        clean_config["pwd"] = pwd

        # 处理扩展file的问题
        append_config_fn_list = clean_config.get("append", [])
        append_config_list = []
        for append_config_fn in append_config_fn_list:
            new_append_config_fn = os.path.join(pwd, append_config_fn)
            append_config_list.append(ConfigYAML(new_append_config_fn, self.debug))
        clean_config["append_config_list"] = append_config_list

        return clean_config

    def handle_config(self)->[]:
        """
        处理配置文件
        :param config:
        :return:
        """
        fit_file_list = []
        fit_file_list += self.handle_file()
        # fit_file_list += self.handle_dir()
        fit_file_list += self.handle_characteristic()
        # git用的是相对路径，所以我们也要用相对路径
        fit_file_list = [item.replace(self.pwd+"/", "") for item in fit_file_list]
        self.fit_file_list = remove_dumplacat_item(fit_file_list)
        self.fit_dir = self.config.get("dir", [])

    def handle_dir(self)->[]:
        """
        把指定目录下的所有文件都包含进去
        :param config:
        :return: 符合清理的文件列表
        """
        # fit_file_list = []
        dirs = self.config.get("dir", [])
        caf = CollectAnyFile()
        for one_dir in dirs:
            self.enum_file(os.path.join(self.pwd, one_dir), self.base_exclude_path, caf)
        if self.debug:
            self.add_by_handle_dir = caf.file_list
        return caf.file_list

    def handle_file(self)->[]:
        """
        得到文件
        :param config:
        :return: 符合清理的文件列表
        """
        if self.debug:
            self.add_by_handle_file = [os.path.join(self.pwd, item) for item in self.config.get("file", [])]
        return [os.path.join(self.pwd, item) for item in self.config.get("file", [])]

    def handle_characteristic(self)->[]:
        """
        根据特征值得到符合的文件
        :param config:
        :return: []
        """
        characteristic_list = self.config.get("characteristic", [])
        exclude_dir = self.base_exclude_path

        cff = CollectFitFile(characteristic_list)
        self.enum_file(self.pwd, exclude_dir, cff)
        if self.debug:
            self.add_by_characteristic = cff.fit_file
        return cff.fit_file

    def __repr__(self):
        return "{name}: {content}".format(name = self.name, content = str(self.config))

    def enum_file(self, given_path: str, exclude_path:[], handler):
        """
        遍历除了exclude_path指定的目录以外的其他目录
        :param given_path: 要遍历的目录
        :param exclude_path: 排除的目录
        :param handler: 处理函数， handler(item:Path)
        :return: 没有需要返回的内容
        """
        p = Path(given_path)
        if given_path in exclude_path:
            # 如果指定目录本身就是被排除的目录，就直接返回
            return
        for item in p.iterdir():
            if item.is_dir():
                if str(item) not in exclude_path:
                    self.enum_file(str(item), exclude_path, handler)
            if item.is_file():
                if str(item) != self.fn:
                    # 防止自己被包括进去
                    if self.debug:
                        self.handle_file_list.append(str(item))
                    handler(item)

    def enum_config(self, handler):
        """
        遍历配置文件以及每一个子配置文件
        :param handler: function(data:ConfigYAML),这里的data就是ConfigYAML本身，方便调试
        :return:
        """
        for sub_config in self.config.get("append_config_list", []):
            sub_config.enum_config(handler)
        handler(self)

    def report(self, put=print):
        put(self.name)
        put("fit file")
        for file in self.fit_file_list:
            put(file)
        put("fit dir")
        for path in self.fit_dir:
            put(path)
        put("end")



class CollectAnyFile:
    """
    收集所有的特征值文件
    """
    def __init__(self):
        self.file_list = []

    def __call__(self, file: Path):
        self.file_list.append(str(file))


class CollectFitFile:
    """
    收集符合特征值的文件
    """
    def __init__(self, characteristic: []):
        self.characteristic = characteristic
        self.fit_file = []
        self.none_unicode_file = []
        self.exclude_file = []

    def __call__(self, file_item: Path):
        """
        Path必须是is_file() true
        """
        try:
            content = file_item.read_bytes().decode()
        except UnicodeDecodeError:
            # 不处理无法decode的代码
            self.none_unicode_file.append(str(file_item))
            return
        for one_char in self.characteristic:
            for exclude_file in one_char.get("exclude", []):
                if file_item.name == exclude_file:
                    #跳过需要排除的文件
                    self.exclude_file.append(exclude_file)
                    return
                # print("fit file {fn} by {exclude}".format(fn=file_item.name, exclude=exclude_file))
            if one_char["data"] in content:
                self.fit_file.append(str(file_item))
                break


class CollectPwd:
    """
    收集配置文件里的pwd
    """
    def __init__(self):
        self.pwd_list = []

    def __call__(self, config: ConfigYAML):
        self.pwd_list.append(config.config["pwd"])


def remove_dumplacat_item(data:list):
    """
    删除一个列表中重复的项目
    :param data:
    :return:
    """
    record = {}
    new_data = []
    for item in data:
        if record.get(item, 0) == 1:
            continue
        record[item] = 1
        new_data.append(item)
    return new_data


def call_cmd_with_status(cmd_line, work_dir):
    """
    处理函数
    :param cmd_line:
    :param work_dir:
    :return: 正常返回，错误返回
    """
    pr = subprocess.Popen(cmd_line, cwd=work_dir, shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, error) = pr.communicate()
    return out, error
    # print(cmd_line, work_dir)
    # return "", ""

def current_branch(target_path):
    out, error = call_cmd_with_status("/usr/bin/git branch", target_path)
    # print("get current branch")
    for one_line in out.split(b'\n'):
        if one_line:
            print(one_line)
            print(one_line[0])
            if 42 == one_line[0]:
                # 解析 b'* master'
                branch_des = one_line.decode('utf-8')
                print(branch_des)
                current_branch_parse = pyparsing.Literal("*") + pyparsing.Word(pyparsing.alphas+pyparsing.alphanums)("branch")
                result = current_branch_parse.parseString(branch_des)
                return result.branch
    return ""


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("根据指定的yaml定义的规则彻底删除掉git中符合的文件")
    parser.add_argument("config_file", metavar="配置yaml", help="需要删除文件的定义文件，用yaml格式")
    parser.add_argument("-write", action="store_true", help="执行清理操作，没有这个选项，只显示计划清理的文件，而不真正操作")
    ret = parser.parse_args()
    cy = ConfigYAML(ret.config_file)
    cy.enum_config(lambda config: config.report())
    if ret.write is True:
        cy.clean_git()
        print("clean git complete")
