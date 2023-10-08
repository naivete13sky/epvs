from  ccMethod import CompressTool
# 用法示例
rar_file_path = r"D:\cc\software\ep\epvs\epdms.rar"  # 替换为你的RAR文件路径
output_dir = r'D:\cc\python\epwork'  # 替换为你要解压到的目录
CompressTool.uncompress_with_winrar(rar_file_path, output_dir)