

class Page:
    def __init__(self, objects, page, start_page=0, max_items=50):
        self.objects = objects
        self.page = page
        self.previous_page = self.get_previous(page, start_page)
        self.next_page = self.get_next(page, objects, max_items)
        self.start_page = start_page
        self.max_items = max_items

    @staticmethod
    def get_previous(page, start_page):
        if page > start_page:
            return page - 1
        else:
            return None

    @staticmethod
    def get_next(page, objects, max_items):
        if len(objects) > (page + 1) * max_items:
            return page + 1
        else:
            return None

