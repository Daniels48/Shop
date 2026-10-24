from datetime import datetime, timedelta

from app.view.dialog.product_history.tabs.history_tab.calculator.enums import ActionType, PaymentMethod, InventoryChangeStatistic
from app.db.repositories.inventory_repository import InventoryRepository
from app.utils.times import to_local_time
from app.view.dialog.product_history.tabs.history_tab import create_tree_item, create_date_three_item
from typing import Tuple
from app.view.dialog.product_history.utils import decimal_to_str_trimmed_for_amount, decimal_to_str_trimmed_for_quantity
from app.utils.decorators import debug_decorator
from PyQt5.QtCore import QModelIndex, QPoint, Qt
from dataclasses import replace

from ..calculator.statistic import Statistic


class HistoryLoader:
    def __init__(self, dialog, barcode: str | None = None):
        self.dialog = dialog
        self.barcode = barcode
        self.row_idx = 0
        self.month_pointer = 0
        self.finished_load = False
        self.daily_summary = {}
        self.top_date = None
        self.previous_date = None
        self.available_months = self.get_available_months(barcode)
        self.calculator = Statistic()

    def get_available_months(self, barcode):
        self.barcode = barcode
        months = self.dialog.db.get_available_months(barcode_product=self.barcode)
        if not months:
            self.finished_load = True
        return months

    def get_formatting_month_range(self, month_str: str) -> Tuple[str, str]:
        formatting_date = "%Y-%m-%d"
        start_date = datetime.strptime(month_str + "-01", formatting_date)
        next_month = (start_date + timedelta(days=32)).replace(day=1)
        return start_date.strftime(formatting_date), next_month.strftime(formatting_date)

    def get_next_month_range(self):
        formatting_range = ()

        if not self.finished_load:
            current_month_str = self.available_months[self.month_pointer]
            self.month_pointer += 1

            if self.month_pointer >= len(self.available_months):
                self.finished_load = True

            formatting_range = self.get_formatting_month_range(current_month_str)
        return formatting_range

    def load_next_chunk(self):
        raw_history = []
        while len(raw_history) < 29 and not self.finished_load:
            month_range = self.get_next_month_range()
            if not month_range:
                break

            new_data = InventoryRepository.get_inventory_changes(
                barcode_product=self.barcode,
                date_range=month_range
            )

            raw_history.extend(new_data)
        return raw_history


    @debug_decorator
    def load_changes(self, barcode: str | None = None, next_chunk=False):
        if next_chunk:
            raw_history = self.load_next_chunk()
        else:
            self.reset(barcode)
            raw_history = self.load_next_chunk()

        self.insert_changes_into_table(raw_history)
        self.update_ui_from_top_row()
        self.dialog.date_widget_first_line.raise_()
        self.dialog.date_label_first_line.raise_()

    def reset(self, barcode):
        self.dialog.tab_changes.clear()
        self.previous_date = None
        self.month_pointer = 0
        self.finished_load = False
        self.daily_summary = {}
        self.dialog.table_statistic_manager.clear_all_combobox()
        self.available_months = self.get_available_months(barcode)


    def insert_row_data(self, model:InventoryChangeStatistic):
        view_data = model.type_action,model.payment_method,model.amount,model.quantity,model.change_date
        data_dict = {"sale_id":model.sale_id,"change_id":model.change_id,"day":model.change_date}

        tree_row = create_tree_item(view_data, data_dict)

        child_item = create_tree_item()
        tree_row.addChild(child_item)

        self.dialog.tab_changes.addTopLevelItem(tree_row)

    def insert_new_header_day(self, formatted_date:str):
        if formatted_date == self.previous_date:
            return

        self.previous_date = formatted_date
        header_item = create_date_three_item(formatted_date)
        self.dialog.tab_changes.addTopLevelItem(header_item)
        # Вставляем в дерево
        self.dialog.tab_changes.addTopLevelItem(header_item)
        idx = self.dialog.tab_changes.indexOfTopLevelItem(header_item)
        self.dialog.tab_changes.setFirstColumnSpanned(idx, QModelIndex(), True)


    @staticmethod
    def get_formatting_day(dt:datetime) -> str:
        russian_months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        format = f"%d {russian_months[dt.month - 1]} %Y г."
        return dt.strftime(format)

    def get_formatting_params_for_ui(self,row: InventoryChangeStatistic) -> InventoryChangeStatistic:
        return replace(
            row,
            type_action=ActionType.get_label(row.type_action),
            payment_method=PaymentMethod.get_label(row.payment_method, row.card_amount_combine, row.cash_amount_combine),
            amount=decimal_to_str_trimmed_for_amount(row.amount),
            quantity=decimal_to_str_trimmed_for_quantity(row.quantity),
            change_date=row.change_date.strftime("%H:%M:%S"),
            lunch_amount=decimal_to_str_trimmed_for_amount(row.lunch_amount),
        )

    @staticmethod
    def is_duplicate_sale(i, history, sale_id):
        if i == 0 or not sale_id:
            return False

        old_sale_id = history[i - 1].sale_id
        return sale_id == old_sale_id

    def insert_changes_into_table(self, raw_query: list[InventoryChangeStatistic]):
        for i, row in enumerate(raw_query):
            row = replace(row, change_date=to_local_time(row.change_date))

            if self.is_duplicate_sale(i, raw_query, row.sale_id):
                continue

            self.calculator.add_statistic(row)
            formatted_day = self.get_formatting_day(row.change_date)

            self.add_last_day_statistic(formatted_day)
            self.insert_new_header_day(formatted_day)
            self.insert_row_data(self.get_formatting_params_for_ui(row))
            self.daily_summary[formatted_day] = self.calculator.get_daily_summary(row.change_date)

        if self.previous_date:
            self.add_daily_summary(self.daily_summary, self.previous_date, self.dialog.right_panel)


    def add_last_day_statistic(self, formatted_day: str):
        if formatted_day != self.previous_date and self.previous_date is not None:
            self.dialog.history_loader.add_daily_summary(self.daily_summary, self.previous_date,self.dialog.right_panel)
            self.daily_summary = {}

    @staticmethod
    def get_dict_values_in_item(item, key) -> str:
        dict_values = item.data(0, Qt.UserRole)
        if dict_values:
            return dict_values.get(key)

    @staticmethod
    def get_top_visible_item(tab):
        index = tab.indexAt(QPoint(0, 0))
        if index.isValid():
            return tab.itemFromIndex(index)


    def get_top_visible_date_text(self) -> str | None:
        tab = self.dialog.tab_changes
        top_item = self.get_top_visible_item(tab)
        data_text = self.get_dict_values_in_item(top_item, "day")

        if data_text:
            self.top_date = data_text
        return self.top_date

    def update_header_date_label(self, text: str):
        self.dialog.date_label_first_line.setText(text)
        self.dialog.date_widget_first_line.show()

    def sync_comboboxes_with_date(self, text):
        self.dialog.table_statistic_manager.set_data_day_scroll(text)
        self.dialog.table_statistic_manager.set_data_month_scroll(text)

    def update_ui_from_top_row(self):
        date = self.get_top_visible_date_text()
        self.update_header_date_label(date)
        self.sync_comboboxes_with_date(date)
        self.dialog.update_table()

    def add_daily_summary(self, summary, formatted_date, table):
        data = summary.get(formatted_date, {})

        self.dialog.table_statistic_manager.set_day_data_table(data, formatted_date, table)
        self.dialog.table_statistic_manager.set_month_data_table(data, formatted_date, table)

        self.dialog.combo_day.update()
        self.dialog.right_panel.viewport().update()