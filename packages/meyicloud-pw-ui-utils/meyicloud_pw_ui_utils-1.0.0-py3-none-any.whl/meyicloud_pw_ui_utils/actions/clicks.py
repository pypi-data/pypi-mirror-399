from playwright.sync_api import Page


class ClickActions:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    # Generic click

    def click(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        selector: str | None = None,
        exact_text: bool = False,
        text: str | None = None,
    ):
        if role and name:
            self.page.get_by_role(role, name=name).click()
            return
        if selector:
            self.page.locator(selector).click()
            return
        if text:
            self.page.get_by_text(text, exact=exact_text).click()
            return
        raise ValueError("click(): provide (role & name) OR selector OR text")

    # Buttons

    def click_button(self, name: str):
        self.page.get_by_role("button", name=name).click()

    def click_button_by_title(self, title: str):
        self.page.get_by_title(title).click()

    # Locators

    def click_locator(self, locator):
        locator.wait_for(timeout=self.default_timeout)
        locator.click()

    # Menus

    def click_menuitem(self, name: str):
        self.page.get_by_role("menuitem", name=name).click()

    def click_menu_item_text(self, text: str, exact: bool = True):
        locator = self.page.get_by_text(text, exact=exact)
        locator.wait_for(timeout=self.default_timeout)
        locator.click()

    # Text / title

    def click_by_role(self, name: str, role: str = "button"):
        self.page.get_by_role(role, name=name).click()

    def click_by_text(self, text: str, exact: bool = True):
        self.page.get_by_text(text, exact=exact).click()

    def click_by_title(self, title: str):
        self.page.get_by_title(title).click()

    # Radio / checkbox

    def click_by_radio(self, name: str, role: str = "radio"):
        self.page.get_by_role(role, name=name).click()

    def select_checkbox_by_name(self, name: str):
        self.page.get_by_role("checkbox", name=name).click()

    # Keyboard

    def press_enter(self, locator):
        locator.wait_for(timeout=self.default_timeout)
        locator.press("Enter")
