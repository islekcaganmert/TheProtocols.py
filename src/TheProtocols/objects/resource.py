class Resource:
    def __init__(self, d: dict):
        self.title = d['title']
        self.description = d['description']
        self.url = d['url']
