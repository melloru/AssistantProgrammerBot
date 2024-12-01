import math


class Paginator:
    def __init__(self, items: list | tuple, per_page: int = 1):
        self.items = items
        self.per_page = per_page
        self.total_pages = math.ceil(len(self.items) / per_page)
        self.cur_page = 1

    def get_page(self):
        start = (self.cur_page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]
