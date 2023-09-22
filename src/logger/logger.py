from datetime import datetime


class LoggerObject:

    def __init__(self):
        self.logs = []

    def log(self, message:str, topic:str) -> None:
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        log_item = (current_date, current_time, topic, message)

        self.logs.append(log_item)
        print(f'{current_time}({topic}): {message}')

    def getLogs(self) -> list:
        return self.logs
    
    def getLog(self) -> tuple:
        return self.logs[-1]
    
logger = LoggerObject()