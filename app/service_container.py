class Container:
    _instance = None

    def __init__(self):
        if Container._instance is not None:
            raise Exception("This class is a singleton!")
        self._services = {}
        Container._instance = self

    @staticmethod
    def get_instance():
        if Container._instance is None:
            Container()
        return Container._instance

    def register(self, key, service):
        """サービスを登録"""
        self._services[key] = service

    def get(self, key):
        """サービスを取得"""
        service = self._services.get(key)
        if not service:
            raise KeyError(f"Service '{key}' not found in container")
        return service
