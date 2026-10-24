from app.search_global import update_results, POSITION_CONFIG, select_current_item, get_product_and_handle
from app.utils.decorators import debug_decorator


class SearchHandler:
    def __init__(self, dialog):
        self.dialog = dialog
        self.set_style_btn_dialog()

    def set_style_btn_dialog(self):
        self.set_style(False)
        self.dialog.clear_button.setStyleSheet(self.set_style_btn(True))
        self.dialog.search_button.setStyleSheet(self.set_style_btn(False))

    def on_search_text_changed(self):
        # self.dialog.hide_details()
        self.set_style(False)
        update_results(self.dialog.db, self.dialog.search_input, self.dialog.list_search, **POSITION_CONFIG.get("history"))

    def select_product_from_search_list(self, item):
        self.dialog.tab_changes.scrollToTop()
        select_current_item(self.dialog.list_search, self.load_product_and_handle)
        self.button_set_style(False)

    @debug_decorator
    def load_product_and_handle(self, product_value=False, tab_enter_product=False):
        self.dialog.tab_changes.scrollToTop()
        if self.dialog.tabs.currentIndex() == 1:
            tab_enter_product = True

        succes = lambda pr: self.on_succes_load_product(pr, tab_enter_product)
        fail = self.on_fail_load_product
        get_product_and_handle(product_value, self.dialog.search_input, self.dialog.db, succes, fail)

    def refresh_table_list_on_search(self, barcode=None, tab_enter_product=None):
        if tab_enter_product:
            self.dialog.products_tab.load_products(barcode=barcode)
        else:
            self.dialog.history_loader.load_changes(barcode=barcode)

    def on_succes_load_product(self, product, tab_enter_product):
        barcode = product[0].split(";")[0]
        name = f"{product[1]} {product[3]} ₽"

        self.refresh_table_list_on_search(barcode, tab_enter_product)

        self.dialog.search_input.setText("")
        self.set_style(False, True)
        self.dialog.search_input.setPlaceholderText(name)

    def on_fail_load_product(self):
        self.dialog.search_input.setPlaceholderText("Продукт с такими данными не найден!")
        self.set_style(True)

    @debug_decorator
    def entered_false_search_input_key(self, item, button_enter=True):
        text = "Введите название товара..."
        self.dialog.tab_changes.scrollToTop()
        if (self.dialog.search_input.placeholderText()) != text:
            self.dialog.search_input.setPlaceholderText(text)
            self.set_style(False)

            active_index = self.dialog.tabs.currentIndex()

            self.refresh_table_list_on_search(tab_enter_product=active_index)

            self.button_set_style(True)
            if button_enter:
                self.dialog.search_input.setFocus()

    def entered_enter_key_input(self):
        if len(self.dialog.search_input.text()) > 0:
            self.load_product_and_handle(False)
            self.button_set_style(False)

    def button_set_style(self, is_off=False):
        s_set, c_set = not is_off, is_off
        self.dialog.search_button.setStyleSheet(self.set_style_btn(s_set))
        self.dialog.clear_button.setStyleSheet(self.set_style_btn(c_set))


    def set_style(self, is_false, is_enter=False):
        if not is_enter:
            insert_style = "color:red; border: 2px solid red;" if is_false else "border: 1px solid black;"
        else:
            insert_style = "color: #73B5E7; border: 2px solid blue;"
        style = f"font-size: 22px; padding: 5px; border-radius:10px;{insert_style}"
        self.dialog.search_input.setStyleSheet(style)

    def set_style_btn(self, is_enter):
        add_style = "background-color:#73B5E7" if is_enter else ""
        base_style = f"font-size: 18px; padding: 5px; border-radius: 7px; border: 1px solid #ADADAD;{add_style}"
        return base_style

