from playwright.sync_api import Page


class Navigation:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def goto(self, url: str, wait_for_networkidle: bool = True):
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        if wait_for_networkidle:
            self.page.wait_for_load_state("networkidle")
