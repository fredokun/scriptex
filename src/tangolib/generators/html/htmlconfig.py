"""
The main configuration for the HTML generator.
"""

class HTMLConfigError(Exception):
    pass

class HTMLConfiguration:
    def __init__(self):
        self.document_class = None
        self.class_options = None

    def check_configuration(self):
        return
        if not self.document_class:
            raise HTMLConfigError("The document class is not set")

    def configured(self):
        return
        try:
            self.check_configuration()
        except HTMLConfigError:
            return False
        return True
