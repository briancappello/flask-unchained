class Store:
    def __init__(self):
        self.resources_by_model = {}

        self.serializers = {}
        self.create_by_model = {}
        self.many_by_model = {}
        self.serializers_by_model = {}
