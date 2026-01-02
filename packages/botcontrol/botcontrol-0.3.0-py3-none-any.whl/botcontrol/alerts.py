class Alerts:
    def __init__(self, spy):
        self.spy = spy

    def send(self, message):
        """ارسال هشدار"""
        self.spy.alert(message)
