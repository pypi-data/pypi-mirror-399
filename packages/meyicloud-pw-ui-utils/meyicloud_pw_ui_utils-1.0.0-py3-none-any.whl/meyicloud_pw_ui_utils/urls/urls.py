from playwright.sync_api import Page, expect


class UrlAssertions:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def expect_url(self, url: str, timeout: int | None = None):
        timeout = timeout or self.default_timeout
        expect(self.page).to_have_url(url, timeout=timeout)

    def wait_and_expect_url(self, url: str, timeout: int | None = None):
        timeout = timeout or self.default_timeout
        self.page.wait_for_url(url, timeout=timeout)
        expect(self.page).to_have_url(url, timeout=timeout)
