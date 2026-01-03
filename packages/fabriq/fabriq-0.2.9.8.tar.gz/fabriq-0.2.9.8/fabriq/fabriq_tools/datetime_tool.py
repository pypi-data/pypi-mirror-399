import datetime

class DateTimeTool:
    def __init__(self):
        """Initialize the Date Time tool."""
        self.description = "A tool for getting the current date and time. You can specify 'date', 'time', or 'datetime' as input to get the respective information."

    def run(self, query="date"):
        now = datetime.datetime.now()
        if query == "date":
            return now.strftime("%d-%m-%Y")
        elif query == "time":
            return now.strftime("%H:%M:%S")
        elif query == "datetime":
            return now.strftime("%d-%m-%Y %H:%M:%S")