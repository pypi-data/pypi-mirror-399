import yaconfig

import tempfile
import os

# A test metaconfig
metaconfig = yaconfig.MetaConfig(
    yaconfig.Variable("str", type=str, default="str", help="A string"),
    yaconfig.Variable(
        "bytes", type=bytes, default='_5#y2L"F4Q8z\n\xec]/', help="Bytes"
    ),
    yaconfig.Variable("int", type=int, default="5", help="A integer"),
    yaconfig.Variable("float", type=float, default="0.88622692545", help="A float"),
    yaconfig.Variable("bool", type=bool, default="false", help="A boolean"),
)

expected = {
    "str": "str",
    "bytes": bytes('_5#y2L"F4Q8z\n\xec]/', "utf8"),
    "int": 5,
    "float": 0.88622692545,
    "bool": False,
}

json_config = """{
    "str": "json",
    "bytes": "a",
    "int": "6",
    "float": "1.88622692545",
    "bool": "true"
}"""

json_expected = {
    "str": "json",
    "bytes": bytes("a", "utf8"),
    "int": 6,
    "float": 1.88622692545,
    "bool": True,
}


def test_default():
    """Test default configuration loading"""
    config = yaconfig.Config(metaconfig)
    for variable, value in config.items():
        assert value == expected[variable]


def test_json():
    """Test json configs"""
    with tempfile.NamedTemporaryFile(prefix="yaconfig-test-", suffix=".json") as f:
        with open(f.name, "wt") as fp:
            fp.write(json_config)

        config = yaconfig.Config(metaconfig)
        config.load_json(f.name)

        for variable, value in config.items():
            assert value == json_expected[variable]


env_vars = [
    ("YACONFIG_TEST_STR", "env"),
    ("YACONFIG_TEST_BYTES", "b"),
    ("YACONFIG_TEST_INT", "7"),
    ("YACONFIG_TEST_FLOAT", "2.88622692545"),
    ("YACONFIG_TEST_BOOL", "FalSE"),
]

env_expected = {
    "str": "env",
    "bytes": bytes("b", "utf8"),
    "int": 7,
    "float": 2.88622692545,
    "bool": False,
}


def test_environment():
    """Test loading form environment variables"""

    for var, value in env_vars:
        os.environ[var] = value

    config = yaconfig.Config(metaconfig)
    config.load_environment(prefix="YACONFIG_TEST_")

    for variable, value in config.items():
        assert value == env_expected[variable]
