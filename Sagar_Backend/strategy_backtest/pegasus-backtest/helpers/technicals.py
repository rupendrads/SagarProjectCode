import pandas_ta as ta

class TechnicalIndicators:
    def __init__(self, data):
        self.data = data
        self.calculation_functions = {
            'sma': self.calculate_sma,
            'ema': self.calculate_ema,
            'dema': self.calculate_dema,
            'tema': self.calculate_tema,
            'kama': self.calculate_kama,
            'rsi': self.calculate_rsi,
            'bbands': self.calculate_bollinger_bands,
            'macd': self.calculate_macd,
            'dmi': self.calculate_dmi,
            'obv': self.calculate_obv,
            'mfi': self.calculate_mfi
        }

    def calculate_indicator(self, indicator_type, **kwargs):
        if indicator_type not in self.calculation_functions:
            raise ValueError("Invalid indicator type. Supported types are: sma, ema, dema, tema, kama, rsi, bbands, macd, dmi, obv, mfi")
        
        calculation_function = self.calculation_functions[indicator_type]
        return calculation_function(**kwargs)

    def calculate_sma(self, **kwargs):
        window = kwargs.get('window', 20)
        return ta.sma(self.data['close'], length=window)

    def calculate_ema(self, **kwargs):
        window = kwargs.get('window', 20)
        return ta.ema(self.data['close'], length=window)

    def calculate_dema(self, **kwargs):
        window = kwargs.get('window', 20)
        return ta.dema(self.data['close'], length=window)

    def calculate_tema(self, **kwargs):
        window = kwargs.get('window', 20)
        return ta.tema(self.data['close'], length=window)

    def calculate_kama(self, **kwargs):
        window = kwargs.get('window', None)
        fast = kwargs.get('fast', None)
        slow = kwargs.get('slow', None)
        return ta.kama(self.data['close'], length=window, fast=fast, slow=slow)

    def calculate_rsi(self, **kwargs):
        window = kwargs.get('window', 14)
        return ta.rsi(self.data['close'], length=window)

    def calculate_bollinger_bands(self, **kwargs):
        window = kwargs.get('window', 20)
        return ta.bbands(self.data['close'], length=window)

    def calculate_macd(self, **kwargs):
        return ta.macd(self.data['close'])

    def calculate_dmi(self, **kwargs):
        window = kwargs.get('window', 14)
        return ta.dmi(self.data['high'], self.data['low'], self.data['close'], length=window)

    def calculate_obv(self, **kwargs):
        return ta.on_balance_volume(self.data['close'], self.data['volume'])

    def calculate_mfi(self, **kwargs):
        window = kwargs.get('window', 14)
        return ta.mfi(self.data['high'], self.data['low'], self.data['close'], self.data['volume'], length=window)

