# auxiliary.py для Systec CAN плагіна

# Стандартні битрейти для CAN
BITRATES_LIST = [
    "10000",    # 10 kbit/s
    "20000",    # 20 kbit/s
    "50000",    # 50 kbit/s
    "100000",   # 100 kbit/s
    "125000",   # 125 kbit/s
    "250000",   # 250 kbit/s
    "500000",   # 500 kbit/s (найпоширеніший)
    "800000",   # 800 kbit/s
    "1000000",  # 1 Mbit/s
]

# Systec CAN канали
SYSTEC_CHANNELS = [
    "Channel 0",
    "Channel 1",
    "Channel 2",
    "Channel 3"
]

# Статуси підключення
class CanStatuses:
    OK = "OK"
    ERROR = "ERROR"
    DISCONNECTED = "DISCONNECTED"
    TIMEOUT = "TIMEOUT"
    INVALID_CHANNEL = "INVALID_CHANNEL"