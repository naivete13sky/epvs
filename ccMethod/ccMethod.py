import os


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