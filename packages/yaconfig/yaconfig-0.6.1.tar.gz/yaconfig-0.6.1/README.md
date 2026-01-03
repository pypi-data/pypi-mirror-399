# yaconfig

[![Github release](https://img.shields.io/github/release/dih5/yaconfig.svg)](https://github.com/dih5/yaconfig/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/yaconfig.svg)](https://pypi.python.org/pypi/yaconfig)

[![license MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/Dih5/yaconfig/master/LICENSE.txt)

[![Build Status](https://travis-ci.org/Dih5/yaconfig.svg?branch=master)](https://travis-ci.org/Dih5/yaconfig)

Python package to assist configuration of Python software.


## Installation
To install the latest release:
```bash
pip3 install yaconfig
```

## Usage
This package is intended to be used by other packages to assist in their configuration. The recommended workflow follows:
- **Add a config module**. Its purpose should be to define the configuration variables (the metaconfig) and to provide a
single instance of the actual configuration (the values) for your application. Simple example:
```python
"""File config.py"""
import yaconfig

metaconfig = yaconfig.MetaConfig(
    yaconfig.Variable("text", type=str, default="Hello world", help="Text to output")
)


# Get a default configuration...
config = yaconfig.Config(metaconfig)

# ... and override it with that in the config file
try:
    config.load_json("config.json")
except FileNotFoundError:
    pass

# You can also write initialization code if running the module
def main():
    metaconfig.interactive_json("config.json")


if __name__ == "__main__":
    main()

```

- To **access the variables**, just use the config instance. Example:
```python
"""File main.py"""
from config import config  #from .config import config if running in a package

print(config["text"])
```

- **In-code modification of the variables** is also possible, as in ```config["text"]="howdy!"```, but bear in mind that initialization code that used the previous value is not reloaded. Also, you have to provide a **string representation** of the value, as in ```config["number"]="5"```. This is intended to enforce the same behavior as when loading from text files.

- To **document the configuration**, you can use the methods of the metaconfig variable you have defined. This can be done
manually from the interpreter or automated by writing a script, as in the main method in the config module example. The methods available include:
```python
from config import metaconfig # Or wherever the config was placed

metaconfig.generate_json_example()  # Generate a config.example.json file
metaconfig.generate_environment_example()  # Generate a environment.example.sh file
metaconfig.interactive_json()  # Prompt the user to generate a config.json file
metaconfig.interactive_environment()  # Prompt the user to generate a environment.sh file
```
