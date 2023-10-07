import subprocess

disk_name = 'C'
postgresql_bin_path = r'C:\Program Files\PostgreSQL\13\bin'
# 创建一个子进程
process = subprocess.Popen(
    "cmd",  # 在Windows上使用cmd
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,  # 使用文本模式以处理字符串
    shell=True  # 启用shell模式
)

# 命令列表
commands = [
    'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
    f'{disk_name}:',
    f'cd {postgresql_bin_path}',
    'postgresql_bin_path',
    "exit"  # 添加一个退出命令以关闭cmd进程
]

# 执行所有命令
for command in commands:
    process.stdin.write(command + "\n")
    process.stdin.flush()

# 读取和打印输出
while True:
    output_line = process.stdout.readline()
    if process.poll() is not None:  # 检查子进程是否完成
        break
    if output_line:
        print(output_line.strip())



# 关闭子进程的标准输入、输出和错误流
process.stdin.close()
process.stdout.close()
process.stderr.close()

# 等待子进程完成
process.wait()

print("finish!")