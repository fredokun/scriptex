"""
The main configuration for the latex generator.
"""

class LatexConfigError(Exception):
    pass

class LatexConfiguration:
    def __init__(self):
        self.document_class = None
        self.class_options = None

    def check_configuration(self):
        if not self.document_class:
            raise LatexConfigError("The document class is not set")

    def configured(self):
        try:
            self.check_configuration()
        except LatexConfigError:
            return False

        return True
