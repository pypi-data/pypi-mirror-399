class ModbusDataProcessor(object):
    def __init__(self):
        pass

    def parse_registers(self, registers: list, address: int = 0) -> dict:
        """
        Парсинг прочитаних регістрів

        :param registers: Список значень регістрів
        :param address: Початкова адреса регістрів
        :return: Словник з обробленими даними
        """
        return {'registers': registers, 'address': address}

    def parse_coils(self, coils: list, address: int = 0) -> dict:
        """
        Парсинг прочитаних coils

        :param coils: Список булевих значень
        :param address: Початкова адреса
        :return: Словник з обробленими даними
        """
        return {'coils': coils, 'address': address}

    def serialize_register(self, value) -> int:
        """
        Серіалізація значення для запису в регістр

        :param value: Значення для запису
        :return: Ціле число для регістру
        """
        return int(value)

    def serialize_registers(self, values: list) -> list:
        """
        Серіалізація списку значень для запису

        :param values: Список значень
        :return: Список цілих чисел
        """
        return [int(v) for v in values]

    @staticmethod
    def to_signed(value: int, bits: int = 16) -> int:
        """
        Конвертація unsigned в signed

        :param value: Unsigned значення
        :param bits: Кількість біт (16 або 32)
        :return: Signed значення
        """
        if value >= (1 << (bits - 1)):
            value -= (1 << bits)
        return value

    @staticmethod
    def to_unsigned(value: int, bits: int = 16) -> int:
        """
        Конвертація signed в unsigned

        :param value: Signed значення
        :param bits: Кількість біт (16 або 32)
        :return: Unsigned значення
        """
        if value < 0:
            value += (1 << bits)
        return value

    @staticmethod
    def registers_to_float(reg_high: int, reg_low: int) -> float:
        """
        Конвертація двох регістрів у float (32-bit)

        :param reg_high: Старший регістр
        :param reg_low: Молодший регістр
        :return: Float значення
        """
        import struct
        raw = (reg_high << 16) | reg_low
        return struct.unpack('>f', struct.pack('>I', raw))[0]

    @staticmethod
    def float_to_registers(value: float) -> tuple:
        """
        Конвертація float у два регістри

        :param value: Float значення
        :return: Кортеж (reg_high, reg_low)
        """
        import struct
        raw = struct.unpack('>I', struct.pack('>f', value))[0]
        return (raw >> 16) & 0xFFFF, raw & 0xFFFF

    @staticmethod
    def registers_to_int32(reg_high: int, reg_low: int) -> int:
        """
        Конвертація двох регістрів у int32

        :param reg_high: Старший регістр
        :param reg_low: Молодший регістр
        :return: Int32 значення
        """
        value = (reg_high << 16) | reg_low
        if value >= 0x80000000:
            value -= 0x100000000
        return value

    @staticmethod
    def int32_to_registers(value: int) -> tuple:
        """
        Конвертація int32 у два регістри

        :param value: Int32 значення
        :return: Кортеж (reg_high, reg_low)
        """
        if value < 0:
            value += 0x100000000
        return (value >> 16) & 0xFFFF, value & 0xFFFF
