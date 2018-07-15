from flask_unchained import Bundle


class VendorBundle(Bundle):
    blueprint_names = ['three', 'four']
