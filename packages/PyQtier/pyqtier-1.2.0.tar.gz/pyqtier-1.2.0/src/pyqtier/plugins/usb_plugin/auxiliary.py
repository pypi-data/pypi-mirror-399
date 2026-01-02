BAUDRATES_LIST = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]
DEFAULT_BAUDRATE = 9600

THEME_SETTINGS = {
    "with_labels": True
}

HELP_TEXT = """For setting up current plugin you need to do a few steps:
1. Create your own data processor which inherits from UsbDataProcessor
    from pyqtier.plugins import UsbDataProcessor

    class MyDataProcessor(UsbDataProcessor):
        def parse(self, data):
            return {'raw': data.decode()}

        def serialize(self, data):
            return data.encode()

2. Create a UsbPluginManager 
    self.usb_manager = UsbPluginManager(with_baudrate=True)

3. Setup view
    self.usb_manager.setup_view(self.main_window.ui.widget, self.main_window.ui.statusbar)

4. Set data processor:
    self.usb_manager.set_data_processor(MyDataProcessor())  

5. Connect signals for receiving data and events:
    self.usb_manager.data_ready.connect(self.on_data_received)
    self.usb_manager.connected.connect(self.on_connected)
    self.usb_manager.disconnected.connect(self.on_disconnected)
    self.usb_manager.error_occurred.connect(self.on_error)
    self.usb_manager.connection_lost.connect(self.on_connection_lost)

6. For sending data use send_data method:
    self.usb_manager.send_data({'message': 'Hello'})
"""