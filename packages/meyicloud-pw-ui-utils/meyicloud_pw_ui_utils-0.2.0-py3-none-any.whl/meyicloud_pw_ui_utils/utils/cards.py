from playwright.sync_api import Page


class CardUtils:
    def __init__(self, page: Page):
        self.page = page

    def get_card(self, name: str, element: str = "div"):
        """
        Universal card finder (Students/Projects/Teams).
        """
        return self.page.locator(element).filter(has_text=name).first
