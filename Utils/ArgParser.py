import argparse


class ArgParser(argparse.ArgumentParser):
    """
    Custom argument parser for the FLASHMem Memory System Simulator.

    Overrides the default error behavior to provide and a pointer to example/test input files.
    """
    def error(self, message):
        """
        Prints a custom error message and usage, then exit.

        Args:
            message (str): The error message describing the argument parsing issue.
        """
        msg = (
            f"{self.format_usage()}"
            f"{self.prog}: error: {message}\n"
            "See examples in PatternConfigs/InputConfigs\n"
        )
        self.exit(2, msg)
