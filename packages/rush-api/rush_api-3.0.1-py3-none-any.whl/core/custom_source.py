class CustomSource:
    def __init__(self, name):
        self.name = name

    def fetch(self):
        """
        Override this method to implement custom data fetching logic.
        Must return a dictionary or list.
        """
        raise NotImplementedError("You must implement the fetch() method.")
