from dataclasses import fields

from PyQt5.QtWidgets import QComboBox

from app.view.dialog.product_history.utils import decimal_to_str_trimmed_for_quantity, decimal_to_str_trimmed_for_amount
from ..calculator.daily_statistic import DailyStatistic, get_statistic_fields




class TableStatiscticUIManager:
    def __init__(self, dialog):
        self.dialog = dialog

    def _update_panel_values(self, data: DailyStatistic,row_offset: int) -> None:
        def change_text_item(row: int, col: int, text: str) -> None:
            item = self.dialog.right_panel.item(row, col)

            if item is not None:
                item.setText(text)

        for i, statistic_field in enumerate(get_statistic_fields()):
            statistic = getattr(data, statistic_field.name)
            row = row_offset + i

            if statistic.quantity > 0:
                qty = decimal_to_str_trimmed_for_quantity(statistic.quantity)
                amount = decimal_to_str_trimmed_for_amount(statistic.sum)
            else:
                qty = amount = "-"

            change_text_item(row, 1, qty)
            change_text_item(row, 2, amount)

    def on_combo_day_change(self, index):
        try:
            value = self.dialog.combo_day.itemData(index)
            data = value.get("data")
            self._update_panel_values(data, row_offset=3)
        except Exception as e:
            print(e, "on_combo_day_change")

    def on_combo_month_change(self, index):
        try:
            data = self.dialog.combo_month.itemData(index)
            self._update_panel_values(data, row_offset=16)
        except Exception as e:
            print(e, "on_combo_month_change")

    def set_data_day_scroll(self, text):
        index = self.dialog.combo_day.findText(text)
        if index != -1:
            self.dialog.combo_day.setCurrentIndex(index)

    def set_data_month_scroll(self, text):
        russian_months = {
            "января": "Январь", "февраля": "Февраль", "марта": "Март",
            "апреля": "Апрель", "мая": "Май", "июня": "Июнь",
            "июля": "Июль", "августа": "Август", "сентября": "Сентябрь",
            "октября": "Октябрь", "ноября": "Ноябрь", "декабря": "Декабрь"
        }

        parts = text.split()
        if len(parts) < 3:
            return
        year = parts[2]
        month = russian_months.get(parts[1])
        if not month:
            return

        date_ = f"{month} {year}г."

        index = self.dialog.combo_month.findText(date_)
        if index != -1:
            self.dialog.combo_month.setCurrentIndex(index)

    def set_day_data_table(self, data, formatted_date, table):
        combo = table.cellWidget(1, 1)
        new_dict = {"date": formatted_date, "data": data}

        if combo.findText(formatted_date) == -1:
            combo.addItem(formatted_date, new_dict)

    def set_month_data_table(self,data: DailyStatistic,formatted_date: str,table) -> None:
        def get_formatted_date_key(formatted_date: str) -> str:
            russian_months = {
                "января": "Январь", "февраля": "Февраль","марта": "Март", "апреля": "Апрель","мая": "Май", "июня": "Июнь",
                "июля": "Июль", "августа": "Август","сентября": "Сентябрь", "октября": "Октябрь","ноября": "Ноябрь", "декабря": "Декабрь",
            }

            parts = formatted_date.split()
            month = russian_months[parts[1]]
            year = parts[2]

            return f"{month} {year}г."

        def sum_statistic(target: DailyStatistic,source: DailyStatistic) -> None:
            for field in fields(source):
                if field.name == "day":
                    continue

                target_value = getattr(target, field.name)
                source_value = getattr(source, field.name)

                target_value.sum += source_value.sum
                target_value.quantity += source_value.quantity

        date_key = get_formatted_date_key(formatted_date)
        combo = table.cellWidget(14, 1)

        index = combo.findText(date_key)

        if index == -1:
            month_data = DailyStatistic(day=data.day)
            sum_statistic(month_data, data)

            combo.addItem(date_key, month_data)
            index = combo.findText(date_key)
        else:
            month_data = combo.itemData(index)
            sum_statistic(month_data, data)
            combo.setItemData(index, month_data)

        combo.setCurrentIndex(index)
        self.on_combo_month_change(index)


    def _clear_combobox(self, combo: QComboBox):
        if combo and isinstance(combo, QComboBox):
            combo.blockSignals(True)
            combo.clear()
            combo.blockSignals(False)

    def clear_all_combobox(self):
        self._clear_combobox(self.dialog.combo_day)
        self._clear_combobox(self.dialog.combo_month)
        self.dialog.right_panel.viewport().update()
