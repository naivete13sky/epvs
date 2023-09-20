def f1():
    import subprocess

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
        "workon epcam_ui_test",  # 用实际的命令替换"command1"
        "python --version",  # 用实际的命令替换"command2"
        "ipconfig"   # 用实际的命令替换"command3"
    ]

    # 逐个执行命令并打印结果
    for command in commands:
        process.stdin.write(command + "\n")
        process.stdin.flush()

    # 读取并打印输出
    while True:
        output_line = process.stdout.readline()
        if output_line == '':
            break  # 没有更多输出了
        print(output_line.strip())

    # 关闭子进程的标准输入、输出和错误流
    process.stdin.close()
    process.stdout.close()
    process.stderr.close()

    # 等待子进程完成
    process.wait()


def f2():
    import subprocess

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
        "workon epcam_ui_test",  # 用实际的命令替换"command1"
        "python --version",  # 用实际的命令替换"command2"
        "ipconfig"  # 用实际的命令替换"command3"
    ]

    # # 逐个执行命令并打印结果
    # for command in commands:
    #     process.stdin.write(command + "\n")
    #     process.stdin.flush()

    process.stdin.write(commands[0] + "\n")
    process.stdin.flush()
    print(1,process.stdout.readline())
    print(2, process.stdout.readline())
    print(3, process.stdout.readline())
    print(4, process.stdout.readline())


    process.stdin.write(commands[1] + "\n")
    process.stdin.flush()
    print(5, process.stdout.readline())
    print(6, process.stdout.readline())



    # 关闭子进程的标准输入、输出和错误流
    process.stdin.close()
    process.stdout.close()
    process.stderr.close()

    # 等待子进程完成
    process.wait()


f2()