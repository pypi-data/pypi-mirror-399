from playwright.sync_api import Page


class InputActions:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    def clear_input(self, *, selector: str | None = None, role: str | None = None, name: str | None = None):
        if selector:
            field = self.page.locator(selector)
        elif role and name:
            field = self.page.get_by_role(role, name=name)
        else:
            raise ValueError("clear_input(): provide selector OR (role & name)")
        field.wait_for(timeout=self.default_timeout)
        field.clear()

    def fill_input(
        self,
        value: str,
        *,
        selector: str | None = None,
        role: str | None = None,
        name: str | None = None,
        clear_first: bool = True,
    ):
        if selector:
            field = self.page.locator(selector)
        elif role and name:
            field = self.page.get_by_role(role, name=name)
        else:
            raise ValueError("fill_input(): provide selector OR (role & name)")

        field.wait_for(timeout=self.default_timeout)
        field.click()
        if clear_first:
            field.clear()
        field.fill(value)

    def clear_and_fill(
        self,
        value: str,
        *,
        selector: str | None = None,
        role: str | None = None,
        name: str | None = None,
    ):
        self.fill_input(value, selector=selector, role=role, name=name, clear_first=True)

    def fill(
        self,
        text: str,
        *,
        name: str | None = None,
        selector: str | None = None,
        role: str = "textbox",
    ):
        if selector:
            field = self.page.locator(selector)
        elif name:
            field = self.page.get_by_role(role, name=name)
            count = field.count()
            print(f"[DEBUG] fill('{text}', name='{name}'): Found {count} fields")
            if count == 0:
                print(f"[DEBUG] No textbox found with name='{name}'. Trying alternatives...")
                field = self.page.get_by_label(name).first
                print(f"[DEBUG] Label locator found {field.count()} fields")
        else:
            raise ValueError("fill(): provide selector OR name")

        if field.count() == 0:
            raise ValueError(f"Field not found for name='{name}' or selector='{selector}'")

        field.wait_for(timeout=self.default_timeout)
        field.click()
        field.clear()
        field.fill(text)
        print(f"[DEBUG] Successfully filled '{text}' in field")

    def fill_new_password(self, value: str):
        self.fill_input(value, selector="#new")

    def fill_confirm_password(self, value: str):
        self.fill_input(value, selector="#confirm")
