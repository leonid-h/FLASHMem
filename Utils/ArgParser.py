import argparse
import sys


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        msg = (
            f"{self.format_usage()}"
            f"{self.prog}: error: {message}\n"
            "See examples in PatternConfigs/InputConfigs\n"
        )
        self.exit(2, msg)
