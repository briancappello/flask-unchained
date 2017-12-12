from collections import namedtuple


AdminTuple = namedtuple('AdminTuple', ('name', 'admin'))
BlueprintTuple = namedtuple('BlueprintTuple', ('name', 'blueprint'))
CommandTuple = namedtuple('CommandTuple', ('name', 'command'))
CommandGroupTuple = namedtuple('CommandGroupTuple', ('name', 'command_group'))
ExtensionTuple = namedtuple('ExtensionTuple', ('name', 'extension', 'dependencies'))
ModelTuple = namedtuple('ModelTuple', ('name', 'model'))
SerializerTuple = namedtuple('SerializerTuple', ('name', 'serializer'))
