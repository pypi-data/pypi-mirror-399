class InvalidURLException(Exception):
    def __init__(self, message: str = 'URL is not valid', url: str = ''):
        self.message = message
        if url:
            self.message += f": {url}"
        super().__init__(self.message)
