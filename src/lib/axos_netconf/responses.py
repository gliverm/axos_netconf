import re


class NetconfResponse:
    """Model for all session returns."""

    def __init__(self, ok=True, err=None, data=None, xml=None):
        self.ok = ok
        if err is not None:
            # Remove marking present
            err = re.sub(r"\s*\^\n", "", err)
        self.err = err
        self.data = data
        self.xml = xml
