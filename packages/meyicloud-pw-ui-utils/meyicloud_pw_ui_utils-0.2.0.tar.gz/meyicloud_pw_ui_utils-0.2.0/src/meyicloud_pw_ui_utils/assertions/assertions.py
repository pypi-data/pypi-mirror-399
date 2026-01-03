from playwright.sync_api import Page, expect


class Assertions:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def expect_text_visible(self, text: str, exact: bool = False, timeout: int | None = None):
        timeout = timeout or self.default_timeout
        if exact:
            locator = self.page.get_by_text(text, exact=True)
            expect(locator).to_be_visible(timeout=timeout)
        else:
            expect(self.page.locator("body")).to_contain_text(text, timeout=timeout)

    def expect_role_visible(self, role: str, name: str, timeout: int | None = None):
        timeout = timeout or self.default_timeout
        locator = self.page.get_by_role(role, name=name)
        expect(locator).to_be_visible(timeout=timeout)

    def wait_for_text_to_disappear(self, text: str):
        locator = self.page.locator(f"text={text}").first
        locator.wait_for(state="detached")
