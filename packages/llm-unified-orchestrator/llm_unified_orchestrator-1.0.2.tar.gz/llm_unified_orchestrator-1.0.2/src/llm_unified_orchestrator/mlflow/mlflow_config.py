class MlFlowConfig:

    def __init__(self, **kwargs):
        self.tracking_host = kwargs.get('tracking_host', "http://localhost:5050")

    tracking_host: str
    