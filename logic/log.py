class MyLog():
    @staticmethod
    def log_init():
        pass
        import logging
        # 创建一个日志记录器
        logger = logging.getLogger('epvs_logger')
        logger.setLevel(logging.DEBUG)
        # 创建一个文件处理器
        file_handler = logging.FileHandler('log/epvs.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        # 创建一个格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        # 检查是否已经存在相同的处理器
        if not any(
                isinstance(handler, logging.FileHandler) and handler.baseFilename == file_handler.baseFilename for handler
                in logger.handlers):
            # 添加文件处理器到日志记录器
            logger.addHandler(file_handler)
        return logger