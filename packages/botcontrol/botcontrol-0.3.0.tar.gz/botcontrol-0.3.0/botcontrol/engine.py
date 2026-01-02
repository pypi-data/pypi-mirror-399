class BotEngine:
    def __init__(self):
        self.commands = {}
        self.plugins = []
        self.engine_initialized = True

    def add_command(self, name, func):
        """ثبت دستور جدید"""
        self.commands[name] = func

    def execute(self, name, context):
        """اجرای دستور بر اساس پیام"""
        if name in self.commands:
            return self.commands[name](context)
        return f"دستور '{name}' یافت نشد."

    def load_plugin(self, plugin):
        """بارگذاری پلاگین"""
        self.plugins.append(plugin)
        plugin.setup(self)
