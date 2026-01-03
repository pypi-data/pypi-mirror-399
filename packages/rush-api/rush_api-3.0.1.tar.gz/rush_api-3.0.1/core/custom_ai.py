class CustomAI:
    def __init__(self, name, logic_function=None):
        self.name = name
        self.logic_function = logic_function

    def process(self, input_data):
        """
        Process input data using the custom logic.
        """
        if self.logic_function:
            try:
                return self.logic_function(input_data)
            except Exception as e:
                return {"error": f"Custom AI Error: {str(e)}"}
        return {"message": f"Hello from {self.name}. No logic defined."}

    def fetch_data(self):
        """
        Simulate fetching data (e.g., internal state or heartbeat).
        """
        return {"status": "active", "name": self.name}
