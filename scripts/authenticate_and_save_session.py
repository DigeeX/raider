from raider import Raider

raider = Raider("test")
raider.config.proxy = "http://localhost:8080"
raider.authenticate()
raider.run_function("test")
raider.save_session()
