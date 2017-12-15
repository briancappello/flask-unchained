from flask import Flask

from .unchained import Unchained


class FlaskUnchained(Flask):
    unchained = None  # type: Unchained
