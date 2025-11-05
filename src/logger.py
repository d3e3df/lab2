def log(func):
    def wrapper(self, args: list[str]) -> None:
        # логгируем команду
        command = f"{func.__name__} {' '.join(args)}"
        self.logger.info(command)

        try:
            # вызываем оригинальную функцию
            result = func(self, args)
            self.logger.info("SUCCESS")
            return result
        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("["):
                error_msg = error_msg.split("] ", 1)[1]
            self.logger.error(f"ERROR: {error_msg}")
            raise

    return wrapper
