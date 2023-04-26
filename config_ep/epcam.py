import os
from epkernel import Configuration
from epkernel import Input

class EPCAM():
    def init(self):
        pass
        epcamPath = r"C:\cc\ep_local\product\EP-CAM\version\20230425\EP-CAM_release_1.1.3.18_jiami\Release"
        Configuration.init(epcamPath)
        Configuration.set_sysattr_path(os.path.join(epcamPath, r'config\attr_def\sysattr'))
        Configuration.set_userattr_path(os.path.join(epcamPath, r'config\attr_def\userattr'))

    def test1(self):
        pass
        result_each_file_identify = Input.file_identify(r"C:\Users\cheng.chen\Desktop\760\BOT_MASK.art")
        print(result_each_file_identify)


if __name__ == "__main__":
    pass
    epcam = EPCAM()
    epcam.init()
    epcam.test1()