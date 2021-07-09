from raider.application import Application


class Raider:
    def __init__(self, name: str) -> None:
        self.application = Application(name)
        self.config = self.application.config
        self.user = self.application.active_user
        self.functions = self.application.functions

    def authenticate(self, username: str = None) -> None:
        self.application.authenticate(username)

    def run_function(self, function: str) -> None:
        self.functions.run(function, self.user, self.config)
