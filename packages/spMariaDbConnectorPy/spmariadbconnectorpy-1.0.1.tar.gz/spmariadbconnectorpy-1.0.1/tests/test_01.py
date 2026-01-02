from spMariaDbConnectorPy import MariaDbConnector


def test_1():
    obj = MariaDbConnector()

    arg1 = "blabla"
    assert obj.for_test_only(arg1) == arg1

