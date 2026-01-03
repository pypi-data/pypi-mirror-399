from playwright.sync_api import Page


class Locators:
    def __init__(self, page: Page):
        self.page = page

    def by_role(self, role: str, name: str | None = None):
        if name:
            return self.page.get_by_role(role, name=name)
        return self.page.get_by_role(role)

    def by_text(self, text: str, exact: bool = False):
        return self.page.get_by_text(text, exact=exact)

    def by_selector(self, selector: str):
        return self.page.locator(selector)
