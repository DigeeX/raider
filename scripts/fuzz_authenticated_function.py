from raider import Raider

raider = Raider("my_app")
raider.config.proxy = "http://localhost:8080"
raider.authenticate()


def fuzz_inputs(value):
    return [value + str(i) for i in range(0, 10)]


raider.fuzz_function("my_function", "access_token", fuzz_inputs)
