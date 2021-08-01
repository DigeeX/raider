from raider import Raider

raider = Raider("my_app")
raider.config.proxy = "http://localhost:8080"


def fuzz_inputs(value):
    return [value + str(i) for i in range(0, 10)]


raider.fuzz_authentication("authentication_stage", "access_token", fuzz_inputs)
