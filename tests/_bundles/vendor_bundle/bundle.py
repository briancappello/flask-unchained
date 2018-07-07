from flask_unchained import Bundle


class VendorBundle(Bundle):
    command_group_names = ['foo_group', 'goo_group']
    extensions_module_name = 'extension'
