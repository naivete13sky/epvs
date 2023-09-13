import configparser
import json
import os
from epkernel import Configuration
from epkernel import Input
from pathlib import Path

class EPCAM():
    def init(self):
        # 参数
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.epcamPath = json.load(cfg)['epcam']['bin_path']  # (json格式数据)字符串 转化 为字典

        # epcamPath = r"C:\cc\ep_local\product\EP-CAM\version\20230425\EP-CAM_release_1.1.3.18_jiami\Release"
        Configuration.init(self.epcamPath)
        Configuration.set_sysattr_path(os.path.join(self.epcamPath, r'config\attr_def\sysattr'))
        Configuration.set_userattr_path(os.path.join(self.epcamPath, r'config\attr_def\userattr'))

    def test1(self):
        with open(r'../settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.epcamPath = json.load(cfg)['epcam']['bin_path']  # (json格式数据)字符串 转化 为字典

        # epcamPath = r"C:\cc\ep_local\product\EP-CAM\version\20230425\EP-CAM_release_1.1.3.18_jiami\Release"
        res = Configuration.init(self.epcamPath)

        Configuration.set_sysattr_path(os.path.join(self.epcamPath, r'config\attr_def\sysattr'))
        Configuration.set_userattr_path(os.path.join(self.epcamPath, r'config\attr_def\userattr'))

        result_each_file_identify = Input.file_identify(r"C:\Users\cheng.chen\Desktop\760\BOT_MASK.art")



if __name__ == "__main__":
    pass
    epcam = EPCAM()

    epcam.test1()