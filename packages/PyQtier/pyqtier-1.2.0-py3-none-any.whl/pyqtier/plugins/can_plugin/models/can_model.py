import can
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from .data_processor import CanDataProcessor
from ..auxiliary import CanStatuses


class CanModel(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_lost = pyqtSignal()
    error_occurred = pyqtSignal(str)
    devices_list_updated = pyqtSignal(list)
    message_received = pyqtSignal(object)
    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._bus: Optional[can.Bus] = None
        self._interface: str = "systec"
        self._channel: int = 0
        self._device_id: int = 0
        self._bitrate: int = 500000
        self._is_connected: bool = False

        self._data_processor: Optional[CanDataProcessor] = None
        self._timer: Optional[QTimer] = None

        self._monitor_timer = QTimer(self)
        self._monitor_timer.timeout.connect(self._check_device_availability)
        self._monitor_timer.start(2000)
        self._last_device_available: Optional[bool] = None

    def set_can_interface(self, device_available: bool):
        """Встановити параметри для підключення"""
        self._device_id = 0  # Завжди використовуємо Device 0
        self._channel = 0  # Завжди канал 0
        self._interface = "systec"

    def set_channel(self, channel: int):
        """Встановити канал адаптера (0 або 1)"""
        self._channel = channel

    def set_bit_rate(self, bitrate: int):
        """Встановити битрейт"""
        self._bitrate = bitrate

    def set_data_processor(self, processor: CanDataProcessor):
        self._data_processor = processor

    def connect(self) -> str:
        """Підключитися до Systec CAN адаптера"""
        try:
            from can.interfaces.systec.ucanbus import UcanBus

            self._bus = UcanBus(
                device=self._device_id,
                channel=self._channel,
                bitrate=self._bitrate
            )
            self._is_connected = True

            self._monitor_timer.stop()

            self._start_listener()
            self.connected.emit()

            return CanStatuses.OK

        except Exception as e:
            self.error_occurred.emit(f"Systec CAN connection error: {str(e)}")
            return CanStatuses.ERROR

    def disconnect(self):
        """Відключитися від CAN шини"""
        if self._bus:
            self._stop_listener()
            self._bus.shutdown()
            self._bus = None

        self._is_connected = False

        self._monitor_timer.start(2000)
        self.disconnected.emit()

    def send_message(self, can_id: int, data: bytes, extended: bool = False):
        """Відправити CAN повідомлення"""
        if not self._is_connected or not self._bus:
            return False

        try:
            message = can.Message(
                arbitration_id=can_id,
                data=data,
                is_extended_id=extended
            )
            self._bus.send(message)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Send error: {str(e)}")
            return False

    def write(self, data: dict):
        """Відправити дані (альтернативний метод)"""
        can_id = data.get('id', 0)
        payload = data.get('data', b'')
        extended = data.get('extended', False)

        if isinstance(payload, (list, tuple)):
            payload = bytes(payload)
        elif isinstance(payload, str):
            payload = payload.encode()

        return self.send_message(can_id, payload, extended)

    def set_message_filter(self, can_id: int, mask: int = 0x7FF):
        """Встановити фільтр повідомлень"""
        if self._bus:
            try:
                self._bus.set_filters([{"can_id": can_id, "can_mask": mask}])
            except Exception as e:
                self.error_occurred.emit(f"Filter error: {str(e)}")

    def is_device_available(self) -> bool:
        """Перевірити чи є доступний Systec пристрій (Device 0)"""
        try:
            from can.interfaces.systec.ucanbus import UcanBus
            # Спробуємо підключитися до Device 0
            test_bus = UcanBus(device=0, channel=0, bitrate=500000)
            test_bus.shutdown()
            return True
        except:
            return False

    def get_device_status(self) -> str:
        """Отримати статус пристрою"""
        return "Device Available" if self.is_device_available() else "No Device Found"

    def get_adapter_info(self, device_id: int = 0) -> dict:
        """Отримати детальну інформацію про адаптер"""
        try:
            from can.interfaces.systec.ucanbus import UcanBus

            test_bus = UcanBus(device=device_id, channel=0, bitrate=500000)

            try:
                hw_info, ch0_info, ch1_info = test_bus.get_hardware_info()

                info = {
                    'device_id': device_id,
                    'product_name': getattr(hw_info, 'product_name', 'Unknown'),
                    'serial_number': getattr(hw_info, 'serial_number', 'Unknown'),
                    'firmware_version': getattr(hw_info, 'firmware_version', 'Unknown'),
                    'hardware_version': getattr(hw_info, 'hardware_version', 'Unknown'),
                    'channel_0_available': hasattr(ch0_info, 'can_type'),
                    'channel_1_available': hasattr(ch1_info, 'can_type'),
                    'status': 'Available'
                }

            except Exception as e:
                info = {
                    'device_id': device_id,
                    'status': 'Available (limited info)',
                    'error': str(e)
                }

            test_bus.shutdown()
            return info

        except Exception as e:
            return {
                'device_id': device_id,
                'status': 'Not Available',
                'error': str(e)
            }

    def _start_listener(self):
        """Запустити прослуховування повідомлень"""
        if self._bus:
            self._stop_listener()

            self._timer = QTimer(self)
            self._timer.timeout.connect(self._check_messages)
            self._timer.start(10)

    def _stop_listener(self):
        """Зупинити прослуховування"""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def _check_messages(self):
        """Перевірити нові повідомлення"""
        if not self._bus or not self._is_connected:
            return

        try:
            while True:
                message = self._bus.recv(timeout=0)
                if message is None:
                    break

                self.message_received.emit(message)

                if self._data_processor:
                    processed_data = self._data_processor.parse(message)
                    if processed_data:
                        self.data_ready.emit(processed_data)

        except Exception as e:
            if "disconnected" in str(e).lower():
                self._handle_connection_lost()
            else:
                self.error_occurred.emit(f"Receive error: {str(e)}")

    def _handle_connection_lost(self):
        """Обробка втрати з'єднання"""
        self._stop_listener()

        if self._bus:
            try:
                self._bus.shutdown()
            except:
                pass
            self._bus = None

        self._is_connected = False
        self._monitor_timer.start(2000)
        self.connection_lost.emit()

    def _check_device_availability(self):
        """Моніторинг доступності пристрою (працює тільки коли відключено)"""
        current_available = self.is_device_available()

        if self._last_device_available != current_available:
            self._last_device_available = current_available
            self.devices_list_updated.emit([current_available])

    @property
    def is_connected(self) -> bool:
        return self._is_connected
