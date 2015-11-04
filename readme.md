项目在开源前，用来清理项目中的敏感文件
从git中彻底删除

##使用方法
在项目根目录下创建一个yaml配置文件
例子文件
```yaml
#配置文件名称，用于输出辨识
name: resume工程下需要删除的文件
#包含这样特征值的代码
characteristic:
#  - data: special_data
  - data: -----BEGIN RSA PRIVATE KEY-----
#剔除这个文件本身
    exclude:
      - cleaner.yaml
#特别指定要处理的文件
#file:
#  - test.py
#特别指定处理的目录
#dir:
#  - special_dir

append:
  - git_cleaner/cleaner.yaml
  - libs/workshop/cleaner.yaml
  - public_resource/cleaner.yaml

branch: public
```
