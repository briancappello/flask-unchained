from collections import defaultdict
from typing import *

from ..route import Route
from .register_blueprints_hook import RegisterBlueprintsHook
from .register_routes_hook import RegisterRoutesHook
from .register_bundle_blueprints_hook import RegisterBundleBlueprintsHook

EndpointName = str
BundleName = str


class Store:
    def __init__(self):
        self.endpoints: Dict[EndpointName, Route] = {}
        self.bundle_routes: Dict[BundleName, List[Route]] = defaultdict(list)
        self.other_routes: List[Route] = []
