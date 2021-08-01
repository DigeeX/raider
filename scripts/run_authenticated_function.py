from raider import Raider

raider = Raider("my_app")
raider.config.proxy = "http://localhost:8080"
raider.authenticate()
raider.run_function("my_function")
