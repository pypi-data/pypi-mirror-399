"""yaconfig - Python package to assist configuration"""

__version__ = "0.6.1"
__author__ = "Dih5 <dihedralfive@gmail.com>"

import json
import os
from collections import OrderedDict
from shlex import quote


def _quote_sh(s):
    return quote(
        s.replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
        .replace("\0", "\\0")
    )


class Variable:
    """Abstraction for a variable in the configuration"""

    def __init__(self, name, type=str, default=None, help=None):
        """

        Args:
            name (str): A name identifying the variable.
            type (type): A python type to transform the value to.
            default (str): A default value, always as a string.
            help (str): A text describing what the value does.
        """
        self.name = name
        self.type = type
        self.default = default
        self.help = help

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def get(self, key, default=None):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            return default

    def _get_bash(self, prefix="", value=None):
        if self.help:
            text = "# %s\n" % self.help
        else:
            text = ""

        modified_name = prefix + self.name.upper()
        if value or self.default:
            text += "export %s=%s" % (
                modified_name,
                _quote_sh(self.default if value is None else value),
            )
        else:
            text += "# export %s=<value>" % modified_name
        return text


class MetaConfig:
    """An abstraction defining what is expected in a configuration"""

    def __init__(self, *variables):
        """

        Args:
            *variables (Variable): Ordered sequence of variables. Their names should be unique.

        """
        self.variables = OrderedDict()
        for variable in variables:
            name = variable["name"]
            if name in self.variables:
                raise ValueError("Variable %s defined multiple times" % name)
            self.variables[name] = variable

    def __getitem__(self, key):
        return self.variables[key]

    def __contains__(self, key):
        return key in self.variables

    def items(self):
        return self.variables.items()

    def prompt(self, new_defaults=None):
        """
        Prompt the user in the command line to generate configuration values.

        Args:
            new_defaults (dict, optional): A dictionary specifying possibly
                different defaults to present to the user instead of the variable's
                built-in default. Keys must match variable names.
        """
        if new_defaults is None:
            new_defaults = {}

        output_values = {}
        for key, var in self.items():
            # Use the new_defaults if available, otherwise the variable's declared default
            default = new_defaults.get(key, var.get("default", ""))
            help_text = var.get("help", "")

            if help_text:
                print(help_text)

            print(f"{key} [{default if default else '<not set>'}]: ", end="\n")
            value = input().strip()
            output_values[key] = value if value else default

        return output_values

    def generate_json_example(self, path="config.example.json", utf8=True):
        """Generate an example json configuration file"""
        values = {key: var.get("default", "") for key, var in self.items()}
        json_string = json.dumps(values, ensure_ascii=not utf8, indent=4)

        if path is not None:
            with open(path, "w") as f:
                f.write(json_string)
        else:
            return json_string

    def interactive_json(self, path="config.json", utf8=True):
        """
        Interactively generate a json configuration file.
        If the file already exists, use existing values as default.
        """
        new_defaults = {}
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    new_defaults = json.load(f)
                    print(
                        "Previoulsy existing configuration file will be used to provide default values."
                    )
            except Exception:
                # If there's any problem reading/parsing the file, just skip it
                new_defaults = {}
                print(
                    "Ignoring a previously existing configuration file which couldn't be read."
                )

        values = self.prompt(new_defaults=new_defaults)
        json_string = json.dumps(values, ensure_ascii=not utf8, indent=4)

        if path is not None:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_string)
        else:
            return json_string

    def generate_environment_example(self, path="environment.example.sh", prefix=""):
        """Generate an example bash configuration file"""
        text = "#!/bin/bash\n"
        text += "# Example configuration file\n\n"
        text += "\n\n".join(
            variable._get_bash(prefix=prefix) for _, variable in self.items()
        )
        text += "\n"
        if path is None:
            return text
        else:
            with open(path, "w") as f:
                f.write(text)

    def generate_environment_md(self, prefix=""):
        """Generate a description Markdown table for a environment-based configuration"""

        names = [prefix + name.upper() for name, variable in self.items()]
        descriptions = [
            variable.help if variable.help else "" for _, variable in self.items()
        ]

        # Max widths for more aesthetic code
        name_width = max([len(name) for name in names]) if names else 10
        desc_width = max([len(desc) for desc in descriptions]) if descriptions else 10

        header = (
            f"| {'Name':<{name_width}} | {'Description':<{desc_width}} |\n"
            f"| {'-' * name_width} | {'-' * desc_width} |\n"
        )
        rows = "\n".join(
            [
                f"| {name:<{name_width}} | {desc:<{desc_width}} |"
                for name, desc in zip(names, descriptions)
            ]
        )

        return header + rows

    def interactive_environment(self, path="environment.sh", prefix=""):
        values = self.prompt()
        text = "#!/bin/bash\n"
        text += "\n\n".join(
            variable._get_bash(prefix=prefix, value=values[var_name])
            for var_name, variable in self.items()
        )
        text += "\n"
        if path is None:
            return text
        else:
            with open(path, "w") as f:
                f.write(text)


class Config:
    """A configuration"""

    def __init__(self, metaconfig):
        """

        Args:
            metaconfig (MetaConfig): The description of what is expected in this configuration

        """
        self.metaconfig = metaconfig
        self.config = {}

        self._load_defaults()

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.load_variable(key, value)

    def __contains__(self, key):
        return key in self.config

    def get(self, key, value=None):
        """Get the value of the selected parameter, returning a default value if not found"""
        try:
            return self.config[key]
        except KeyError:
            return value

    def items(self):
        return self.config.items()

    def load_variable(self, variable, value):
        """
        Store a value for a variable in the configuration.

        Args:
            variable (str): The variable name.
            value (str): Its value represented as a string.

        """
        if not isinstance(value, str):
            raise ValueError("A string representation of the value must be provided")

        if variable in self.metaconfig:
            t = self.metaconfig[variable].get("type", str)
            if t is bytes:
                value = bytes(value, "utf8")
            elif t is bool:
                value = value.lower()
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                else:
                    raise ValueError(
                        "Expected boolean value, found instead: %s" % value
                    )
            else:
                value = t(value)
            self.config[variable] = value

    def _load_defaults(self):
        """Generate the default configuration"""
        for variable, settings in self.metaconfig.items():
            value = settings.get("default")
            if value is not None:
                self.load_variable(variable, value)

    def load_json(self, path):
        """
        Load the configuration from a json file

        Args:
            path (str): Path to the json file.

        """
        with open(path, "r", encoding="utf-8") as f:
            file_data = json.load(f)
        for variable, value in file_data.items():
            self.load_variable(variable, value)

    def load_environment(self, prefix=""):
        """
        Load the configuration from environment variables

        Args:
            prefix (str): A prefix for the environment variables.

        """
        for variable, settings in self.metaconfig.items():
            env_val = os.getenv(prefix + variable.upper())
            if env_val is not None:
                self.load_variable(variable, env_val)
