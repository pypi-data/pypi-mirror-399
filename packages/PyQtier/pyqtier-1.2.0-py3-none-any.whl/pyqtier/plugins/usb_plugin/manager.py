from typing import List

from .auxiliary import *
from .models.data_processor import UsbDataProcessor
from .models.serial_model import SerialModel, Statuses
from ..plugins import PyQtierPlugin


class UsbPluginManager(PyQtierPlugin):
    def __init__(self, with_baudrate: bool = False, default_baudrate: int = 9600, custom_ui=None):
        super().__init__()

        if with_baudrate:
            from .views.usb_control_with_baudrate import Ui_UsbWidget
            self._default_baudrate: int = default_baudrate
        else:
            from .views.usb_control import Ui_UsbWidget
            self._default_baudrate: int = 0

        self._with_baudrate: bool = with_baudrate

        if custom_ui:
            self._ui = custom_ui()
        else:
            self._ui = Ui_UsbWidget()

        self._serial: SerialModel = SerialModel()

    def setup_view(self, *args, **kwargs):
        super().setup_view(*args, **kwargs)

        self._serial.devices_list_updated.connect(self._update_devices_list)
        self._update_devices_list()

        if self._with_baudrate:
            self._ui.cb_list_baud_rates.addItems(BAUDRATES_LIST)
            self._ui.cb_list_baud_rates.setCurrentIndex(BAUDRATES_LIST.index(str(self._default_baudrate)))

        self._serial.connect_signal.connect(self._on_connected)
        self._serial.disconnect_signal.connect(self._on_disconnected)
        self._serial.connection_lost.connect(self._on_connection_lost)

        self.create_behavior()

    def create_behavior(self):
        self._ui.bt_connect_disconnect.clicked.connect(self._connect_disconnect_callback)

    # ===== PUBLIC METHODS =====

    def send_data(self, data: dict):
        self._serial.write(data)

    def set_data_processor(self, data_processor: UsbDataProcessor):
        self._serial.set_data_processor(data_processor)

    # ===== INNER METHODS =====

    def _connect(self):
        self._serial.set_serial_port(self._ui.cb_list_usb_devices.currentText().split(" - ")[0])

        if self._with_baudrate:
            self._serial.set_baud_rate(int(self._ui.cb_list_baud_rates.currentText()))

        if self._serial.connect() != Statuses.OK:
            if self._statusbar:
                self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} connection failure!", 4000)
            self._update_devices_list()

    def _disconnect(self):
        if self._serial.is_connected:
            self._serial.disconnect()

    def _connect_disconnect_callback(self):
        if self._serial.is_connected:
            self._disconnect()
        else:
            self._connect()

    def _update_devices_list(self, devices: List[str] = None):
        current_device = self._ui.cb_list_usb_devices.currentText()
        available_devices = devices if devices else self._serial.get_available_ports()

        self._ui.cb_list_usb_devices.clear()
        self._ui.cb_list_usb_devices.addItems(available_devices)

        if current_device in available_devices:
            self._ui.cb_list_usb_devices.setCurrentIndex(available_devices.index(current_device))

    def _on_connected(self):
        self._ui.bt_connect_disconnect.setText("Disconnect")
        if self._statusbar:
            self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} connected!", 4000)

    def _on_disconnected(self):
        self._ui.bt_connect_disconnect.setText("Connect")
        if self._statusbar:
            self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} disconnected!", 4000)

    def _on_connection_lost(self):
        self._ui.bt_connect_disconnect.setText("Connect")
        if self._statusbar:
            self._statusbar.showMessage("USB: Connection lost!", 4000)

    # ===== INFORMATION =====

    @staticmethod
    def get_available_ports() -> List[str]:
        return SerialModel.get_available_ports()

    # ===== ACCESS TO SIGNALS =====

    @property
    def connected(self):
        return self._serial.connect_signal

    @property
    def disconnected(self):
        return self._serial.disconnect_signal

    @property
    def error_occurred(self):
        return self._serial.error_occurred

    @property
    def connection_lost(self):
        return self._serial.connection_lost

    @property
    def devices_list_updated(self):
        return self._serial.devices_list_updated

    @property
    def raw_data_received(self):
        return self._serial.raw_data_received

    @property
    def data_ready(self):
        return self._serial.data_ready
