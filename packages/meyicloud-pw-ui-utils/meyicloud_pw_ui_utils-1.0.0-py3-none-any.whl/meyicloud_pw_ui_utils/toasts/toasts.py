from playwright.sync_api import Page, expect


class Toasts:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def expect_toast(
        self,
        message: str,
        title: str | None = None,
        container_selector: str = "li[data-state='open']",
    ):
        toast = self.page.locator(container_selector).first
        expect(toast).to_be_visible(timeout=self.default_timeout)
        if title:
            expect(toast.get_by_text(title)).to_be_visible(timeout=self.default_timeout)
        expect(toast.get_by_text(message)).to_be_visible(timeout=self.default_timeout)
        return toast

    def close_toast(
        self,
        container_selector: str = "li[data-state='open']",
        close_selector: str = "[toast-close], button:has(svg.lucide-x)",
    ):
        toast = self.page.locator(container_selector).first
        close_btn = toast.locator(close_selector)
        try:
            close_btn.wait_for(timeout=2000)
            close_btn.click()
        except Exception:
            print("[Warning] No close button for toast")

    def expect_assert_text_visible(self, message: str, title: str | None = None):
        toast = self.expect_toast(message=message, title=title)
        self.close_toast()
