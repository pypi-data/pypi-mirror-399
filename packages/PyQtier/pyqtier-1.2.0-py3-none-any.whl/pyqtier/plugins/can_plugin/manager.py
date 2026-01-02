from typing import Optional

from .auxiliary import BITRATES_LIST, CanStatuses
from .models.data_processor import CanDataProcessor
from .models.can_model import CanModel
from ..plugins import PyQtierPlugin


class CanPluginManager(PyQtierPlugin):
    def __init__(self, with_bitrate: bool = False, default_bitrate: int = 500000, custom_ui=None):
        super().__init__()

        if with_bitrate:
            from .views.can_control_with_bitrate import Ui_CanWidget
            self._default_bitrate: int = default_bitrate
        else:
            from .views.can_control import Ui_CanWidget
            self._default_bitrate: int = 0

        self._with_bitrate: bool = with_bitrate

        if custom_ui:
            self._ui = custom_ui()
        else:
            self._ui = Ui_CanWidget()

        self._can: CanModel = CanModel()

    def setup_view(self, *args, **kwargs):
        super().setup_view(*args, **kwargs)

        self._can.devices_list_updated.connect(self._update_device_status)
        self._update_device_status()

        if self._with_bitrate:
            self._ui.cb_list_bit_rates.addItems(BITRATES_LIST)
            self._ui.cb_list_bit_rates.setCurrentIndex(BITRATES_LIST.index(str(self._default_bitrate)))

        self._can.connected.connect(self._on_connected)
        self._can.disconnected.connect(self._on_disconnected)
        self._can.connection_lost.connect(self._on_connection_lost)

        self.create_behavior()

    def create_behavior(self):
        self._ui.bt_connect_disconnect.clicked.connect(self._connect_disconnect_callback)

    # ===== PUBLIC METHODS =====

    def send_data(self, data: dict):
        self._can.write(data)

    def send_message(self, can_id: int, data: bytes, extended: bool = False) -> bool:
        """Відправити CAN повідомлення"""
        return self._can.send_message(can_id, data, extended)

    def set_message_filter(self, can_id: int, mask: int = 0x7FF):
        """Встановити фільтр повідомлень CAN"""
        self._can.set_message_filter(can_id, mask)

    def set_data_processor(self, data_processor: CanDataProcessor):
        self._can.set_data_processor(data_processor)

    # ===== INTERNAL METHODS =====
    def _connect(self):
        self._can.set_can_interface(True)

        if self._with_bitrate:
            bitrate = int(self._ui.cb_list_bit_rates.currentText())
            self._can.set_bit_rate(bitrate)

        self._can.connect()

    def _disconnect(self):
        if self._can.is_connected:
            self._can.disconnect()

    def _connect_disconnect_callback(self):
        if self._can.is_connected:
            self._disconnect()
        else:
            self._connect()

    def _update_device_status(self, device_list=None):
        """Оновити статус CAN пристрою"""
        if self._can.is_device_available():
            status = "CAN: Systec device available"
        else:
            status = "CAN: No Systec device found"

        if self._statusbar:
            self._statusbar.showMessage(status)

    def _on_connected(self):
        self._ui.bt_connect_disconnect.setText("Disconnect")
        if self._statusbar:
            if self._with_bitrate:
                bitrate = int(self._ui.cb_list_bit_rates.currentText())
                self._statusbar.showMessage(f"CAN: Connected to Systec device @ {bitrate} bps")
            else:
                self._statusbar.showMessage("CAN: Connected to Systec device")

    def _on_disconnected(self):
        self._ui.bt_connect_disconnect.setText("Connect")
        if self._statusbar:
            self._statusbar.showMessage("CAN: Disconnected")

    def _on_connection_lost(self):
        self._ui.bt_connect_disconnect.setText("Connect")
        if self._statusbar:
            self._statusbar.showMessage("CAN: Connection lost!")

    # ===== INFORMATION =====

    def is_device_available(self) -> bool:
        return self._can.is_device_available()

    def get_adapter_info(self, device_id: int = 0) -> dict:
        return self._can.get_adapter_info(device_id)

    # ===== ACCESS TO SIGNALS =====

    @property
    def connected(self):
        return self._can.connected

    @property
    def disconnected(self):
        return self._can.disconnected

    @property
    def error_occurred(self):
        return self._can.error_occurred

    @property
    def connection_lost(self):
        return self._can.connection_lost

    @property
    def devices_list_updated(self):
        return self._can.devices_list_updated

    @property
    def message_received(self):
        return self._can.message_received

    @property
    def data_ready(self):
        return self._can.data_ready
