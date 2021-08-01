from raider import Raider

raider = Raider("my_app")
raider.config.proxy = "http://localhost:8080"
raider.load_session()


def fuzz_inputs(value):
    for i in range(0, 10):
        yield value + str(i)


raider.fuzz_function("my_function", "session_id", fuzz_inputs)
