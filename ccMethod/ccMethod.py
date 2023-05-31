import os


import rarfile as rarfile


class RemoteCMD():
    import subprocess


    def __init__(self,psexec_path,computer,username,password):
        # 获取当前PATH的值
        current_path = os.environ.get('PATH', '')
        # 将要添加的路径加入PATH变量
        os.environ['PATH'] = f"{psexec_path};{current_path}"


        self.computer = computer  # 远程计算机名
        self.username = username  # 远程计算机用户名
        self.password = password  # 远程计算机密码




        # 通过net use命令进行身份验证，使得subprocess能够执行远程命令
        self.net_use_command = f'net use \\\\{self.computer} /user:{self.username} {self.password}'
        self.subprocess.call(self.net_use_command, shell=True)



    def run_cmd(self,command):
        pass
        self.command = command  # 远程cmd命令

        # 执行远程命令
        self.remote_command = f'psexec \\\\{self.computer} {self.command}'
        self.subprocess.call(self.remote_command, shell=True)


class CompressTool():
    @staticmethod
    def untgz(ifn, untgz_path):
        """解压tgz文件到指定目录
        :param     ifn(str):解压导入路径
        :param     untgz_path(str):解压后存放路径
        :returns   :None
        :raises    error:
        """
        try:
            ifn = ifn.split(sep='"')[1]
        except:
            pass
        ofn = untgz_path
        # with tf.open(ifn, 'r:gz') as tar:
        import tarfile as tf
        tar = tf.open(ifn)
        for tarinfo in tar:
            if os.path.exists(os.path.join(ofn, tarinfo.name)):
                for root, dirs, files in os.walk(os.path.join(ofn, tarinfo.name), topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
            tar.extract(tarinfo.name, ofn)
        print('uncompress success!')
        return os.path.dirname(tarinfo.name)
        # os.system('pause')
        return

    @staticmethod
    def is_rar_file(file_path):
        try:
            with rarfile.RarFile(file_path) as rf:
                return True
        except rarfile.RarCannotExec as e:
            return False

    @staticmethod
    def compress_with_winrar(file_path):
        '''压缩到当前路径，压缩文件名称根据被压缩对象取的'''
        file_name = os.path.basename(file_path)  # 获取文件名
        output_path = os.path.dirname(file_path)  # 获取文件所在目录
        output_file = os.path.join(output_path, f"{file_name}.rar")  # 构建压缩文件的完整路径
        command = f'winrar a -ep1 "{output_file}" "{file_path}"'  # 构建WinRAR命令
        import subprocess
        subprocess.run(command, shell=True)




if __name__ == '__main__':
    psexec_path = 'C:\cc\python\epwork\epvs\ccMethod'
    computer = '192.168.1.3'
    username = 'administrator'
    password = 'cc'

    myRemoteCMD = RemoteCMD(psexec_path,computer,username,password)

    command_operator = 'rd /s /q'
    command_folder_path = r"\\vmware-host\Shared Folders\share\epvs\gerber\nca60led_add1_b_g"

    command = r'cmd /c {} "{}"'.format(command_operator,command_folder_path)

    myRemoteCMD.run_cmd(command)