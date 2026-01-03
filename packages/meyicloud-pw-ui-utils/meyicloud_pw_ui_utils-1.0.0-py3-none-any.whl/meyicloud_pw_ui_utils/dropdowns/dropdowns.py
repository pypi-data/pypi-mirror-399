from playwright.sync_api import Page, expect


class Dropdowns:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def open_combobox(self, text_contains: str | None = None, selector: str | None = None):
        if selector:
            box = self.page.locator(selector)
        elif text_contains:
            box = self.page.get_by_role("combobox").filter(has_text=text_contains).first
        else:
            raise ValueError("open_combobox(): provide selector OR text_contains")
        box.click()
        return box

    def select_option_by_role_option(self, name: str):
        self.page.get_by_role("option", name=name).click()

    def select_checkbox_by_name(self, name: str):
        self.page.get_by_role("checkbox", name=name).click()

    def select_student_status(self, status: str):
        menu = self.page.get_by_role("menu").nth(0)
        expect(menu).to_be_visible()
        item = menu.get_by_role("menuitem", name=status, exact=True)
        expect(item).to_be_visible()
        item.click()
