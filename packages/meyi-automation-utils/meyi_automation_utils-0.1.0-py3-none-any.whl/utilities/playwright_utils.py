from datetime import datetime
from pydoc import text
from playwright.sync_api import Page, expect
import time 



def date_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def get_accessible_date(date: datetime) -> str:
    return f"Choose {date.strftime('%A')}, {date.strftime('%B')} {date.day}{date_suffix(date.day)}"


class PlaywrightUtils:
    def __init__(self, page: Page, default_timeout: int = 5000):
        self.page = page
        self.default_timeout = default_timeout

    # ---------- Navigation ----------

    def goto(self, url: str, wait_for_networkidle: bool = True):
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        if wait_for_networkidle:
            self.page.wait_for_load_state("networkidle")

    # ---------- Locators ----------

    def by_role(self, role: str, name: str = None):
        if name:
            return self.page.get_by_role(role, name=name)
        return self.page.get_by_role(role)

    def by_text(self, text: str, exact: bool = False):
        return self.page.get_by_text(text, exact=exact)

    def by_selector(self, selector: str):
        return self.page.locator(selector)

    # ---------- Click helpers ----------

    def click(
        self,
        *,
        role: str = None,
        name: str = None,
        selector: str = None,
        exact_text: bool = False,
        text: str = None,
    ):
        """
        One entrypoint for click:
        - click(role="button", name="Save")
        - click(selector="button:has(svg.lucide-plus)")
        - click(text="My Labs")
        """
        if role and name:
            self.by_role(role, name).click()
            return
        if selector:
            self.by_selector(selector).click()
            return
        if text:
            self.by_text(text, exact=exact_text).click()
            return
        raise ValueError("click(): provide (role & name) OR selector OR text")

    def click_button(self, name: str):
        self.by_role("button", name).click()


    def click_button_by_title(self, title: str):
        self.page.get_by_title(title).click()

    # ---------- Text / assertion helpers ----------

    def expect_text_visible(self, text: str, exact: bool = False, timeout: int = None):
        timeout = timeout or self.default_timeout

        if exact:
            locator = self.by_text(text, exact=True)
            expect(locator).to_be_visible(timeout=timeout)
        else:
            expect(
                self.page.locator("body")
            ).to_contain_text(text, timeout=timeout)



    def expect_role_visible(self, role: str, name: str, timeout: int = None):
        timeout = timeout or self.default_timeout
        locator = self.by_role(role, name)
        expect(locator).to_be_visible(timeout=timeout)

    # ---------- Input helpers (clear, fill, clear+fill) ----------

    def clear_input(self, *, selector: str = None, role: str = None, name: str = None):
        """
        Uses locator.clear() which is part of Playwright. [web:21]
        """
        if selector:
            field = self.by_selector(selector)
        elif role and name:
            field = self.by_role(role, name)
        else:
            raise ValueError("clear_input(): provide selector OR (role & name)")
        field.wait_for(timeout=self.default_timeout)
        field.clear()

    def fill_input(
        self,
        value: str,
        *,
        selector: str = None,
        role: str = None,
        name: str = None,
        clear_first: bool = True,
    ):
        if selector:
            field = self.by_selector(selector)
        elif role and name:
            field = self.by_role(role, name)
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
        selector: str = None,
        role: str = None,
        name: str = None,
    ):
        self.fill_input(value, selector=selector, role=role, name=name, clear_first=True)


    def fill(
        self,
        text: str,
        *,
        name: str = None,
        selector: str = None, 
        role: str = "textbox",  
    ):
        """
        Usage:
        - fill("New Name", name="Full Name *")  # Uses role="textbox" + name
        - fill("pass", selector="#new")         # Direct selector
        - fill("test", name="Description *")    # Works with any role+name combo
        """
        field = None
        if selector:
            field = self.by_selector(selector)
        elif name:
            field = self.by_role(role, name=name)  

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





    # ---------- Dropdown helpers ----------

    def open_combobox(self, text_contains: str = None, selector: str = None):
        """
        Open a combobox either by selector or by visible text fragment. [web:15]
        """
        if selector:
            box = self.by_selector(selector)
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

    # ---------- Toast / snackbar helpers ----------

    def expect_toast(
        self,
        message: str,
        title: str = None,
        container_selector: str = "li[data-state='open']",
    ):
        """
        Radix-like toast: validates container, title, and message, then returns the toast locator. [web:23]
        """
        toast = self.by_selector(container_selector).first
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
        toast = self.by_selector(container_selector).first
        close_btn = toast.locator(close_selector)
        try:
            close_btn.wait_for(timeout=2000)
            close_btn.click()
        except Exception:
            print("[Warning] No close button for toast")

    def expect_assert_text_visible(self, message: str, title: str = None):
        toast = self.expect_toast(message=message, title=title)
        self.close_toast()

    # ---------- URL helpers ----------

    def expect_url(self, url: str, timeout: int | None = None):
        """
        Wait for and assert that the current URL equals `url`. [web:60][web:68]
        """
        timeout = timeout or self.default_timeout
        expect(self.page).to_have_url(url, timeout=timeout)

    def wait_and_expect_url(self, url: str, timeout: int | None = None):
        """
        First wait for navigation to `url`, then assert. [web:77]
        """
        timeout = timeout or self.default_timeout
        self.page.wait_for_url(url, timeout=timeout)
        expect(self.page).to_have_url(url, timeout=timeout)

    # ---------- Optional specific helpers for password IDs ----------

    def fill_new_password(self, value: str):
        self.fill_input(value, selector="#new")

    def fill_confirm_password(self, value: str):
        self.fill_input(value, selector="#confirm")


    def click_locator(self, locator):
        """
        Generic: wait for a locator, then click it.
        """
        locator.wait_for(timeout=self.default_timeout)
        locator.click()

    def click_menuitem(self, name: str):
        """
        Click a menuitem by its accessible name.
        """
        self.by_role("menuitem", name).click()

    def press_enter(self, locator):
        """
        Focus the given locator and press Enter.
        """
        locator.wait_for(timeout=self.default_timeout)
        locator.press("Enter")


    def click_menu_item_text(self, text: str, exact: bool = True):
        locator = self.by_text(text, exact=exact)
        locator.wait_for(timeout=self.default_timeout)
        locator.click()


    def get_card(self, name: str, element: str = "div"):
        """
        Universal card finder (Students/Projects/Teams)
        Usage: 
        - utils.get_card("san") → Member card
        - utils.get_card("Project Name") → Project card  
        - utils.get_card("Student Name") → Student card
        """
        return self.page.locator(element).filter(has_text=name).first

    def open_combobox(self, text_contains: str = None, selector: str = None):
        if selector:
            box = self.by_selector(selector)
        elif text_contains:
            box = self.page.get_by_role("combobox").filter(has_text=text_contains).first
        else:
            raise ValueError("open_combobox(): provide selector OR text_contains")
        box.click()
        return box

    def select_option_by_role_option(self, name: str):
        self.page.get_by_role("option", name=name).click()


    def select_student_status(self, status: str):
        """Selects a status (All / Active / Inactive) from the opened students dropdown."""
        menu = self.page.get_by_role("menu").nth(0)
        expect(menu).to_be_visible()
        item = menu.get_by_role("menuitem", name=status, exact=True)
        expect(item).to_be_visible()
        item.click()

    def click_by_role(self, name):
        """Click element by role and name"""
        self.page.get_by_role("button", name=name).click()

    def click_by_text(self, text):
        """Click element by exact text"""
        self.page.get_by_text(text, exact=True).click()

    def click_by_title(self, title):
        """Click element by title attribute"""
        self.page.get_by_title(title).click()


    def click_by_radio(self, name, role="radio"):
        """Click element by role and name (default: radio)"""
        self.page.get_by_role(role, name=name).click()

    def select_checkbox_by_name(self, name: str):
        """Select checkbox by name"""
        self.page.get_by_role("checkbox", name=name).click()

    def wait_for_text_to_disappear(self, text: str):
        """Wait indefinitely until text disappears from page."""
        locator = self.page.locator(f"text={text}").first
        locator.wait_for(state="detached")

    def click_text_if_exists(self, text: str, exact: bool = True, timeout: int | None = None):
        """
        Click an element by text only if it exists.
        Does NOT fail when the text is not present.
        """
        locator = self.page.get_by_text(text, exact=exact)
        count = locator.count()  
        if count > 0:
            locator.first.click()
            if timeout:
                self.page.wait_for_timeout(timeout)

    