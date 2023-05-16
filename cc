pyinstaller打包
pyinstaller --exclude "settings/*" main.py
然后把settings文件夹和config_g文件夹拷到main里。这样编辑好的程序在别的人电脑里也可以运行了。




psexec，需要在远程机器中开户管理员账户。
net user administrator /active:yes
设置密码为cc。


