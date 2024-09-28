import requests
from dataclasses import dataclass

# Information from API
API_Key = '0135ee9e025eaf7c21f154adebb2ec03'
BASE = 'EUR'
SUPPORTED_CURRENCIES = ['USD', 'PLN', 'GBP']


available_currencies = requests.get(f"http://api.exchangeratesapi.io/v1/latest?access_key={API_Key}&base={BASE}").json()
base_of_rates = available_currencies['rates']
print(base_of_rates)


# List with currency rates for available currencies
db_rates = []


@dataclass
class CurrencyRate:
    source_currency: str
    target_currency: str
    rate: float


class ExchangeRate:

    @staticmethod
    def check_if_currency_conversion_is_available(to_currency: str) -> bool:
        if to_currency in base_of_rates:
            return True
        else:
            return False

    @staticmethod
    def read_and_save_exchange_rate_from_api(to_currency: str) -> None:
        if ExchangeRate.check_if_currency_conversion_is_available(to_currency):
            db_rates.append(
                CurrencyRate(source_currency=BASE, target_currency=to_currency, rate=base_of_rates[to_currency]))


class ReadRateFromDB:

    @staticmethod
    def read_rate(from_currency: str, to_currency: str) -> float | str:
        try:
            if from_currency == to_currency:
                return 1
            if from_currency == BASE:
                return ReadRateFromDB.convert_eur_to_supported_currency(to_currency)
            if to_currency == BASE:
                return ReadRateFromDB.convert_supported_currency_to_eur(from_currency)
            if (from_currency in SUPPORTED_CURRENCIES) and (to_currency in SUPPORTED_CURRENCIES or to_currency == BASE):
                return ReadRateFromDB.convert_supported_currency_to_another_supported_currency(
                    from_currency, to_currency)

            raise RateNotAvailableException

        except RateNotAvailableException:
            print('Exchange rate is not available')
            return 'not available'

    @staticmethod
    def get_the_from_currency_rate(from_currency):
        for from_currency_in_list in range(len(db_rates)):
            if from_currency == db_rates[from_currency_in_list].target_currency:
                return db_rates[from_currency_in_list].rate

    @staticmethod
    def get_the_to_currency_rate(to_currency):
        for to_currency_in_list in range(len(db_rates)):
            if to_currency == db_rates[to_currency_in_list].target_currency:
                return db_rates[to_currency_in_list].rate

    @staticmethod
    def convert_eur_to_supported_currency(to_currency):
        for currency in range(len(db_rates)):
            if to_currency == db_rates[currency].target_currency:
                return db_rates[currency].rate

    @staticmethod
    def convert_supported_currency_to_eur(from_currency):
        for from_currency_in_list in range(len(db_rates)):
            if from_currency == db_rates[from_currency_in_list].target_currency:
                from_currency_rate = db_rates[from_currency_in_list].rate
            return 1 / from_currency_rate

    @staticmethod
    def convert_supported_currency_to_another_supported_currency(from_currency, to_currency):
        from_currency_rate = ReadRateFromDB.get_the_from_currency_rate(from_currency)
        to_currency_rate = ReadRateFromDB.get_the_to_currency_rate(to_currency)
        return to_currency_rate/from_currency_rate


class RateNotAvailableException(Exception):
    pass


def main():
    currency_to_convert_from = 'PLN'
    currency_to_convert_to = 'USD'

    for currency in SUPPORTED_CURRENCIES:
        ExchangeRate.read_and_save_exchange_rate_from_api(currency)

    currency_conversion_available = ExchangeRate.check_if_currency_conversion_is_available(currency_to_convert_to)

    if currency_conversion_available:
        rate = ReadRateFromDB.read_rate(currency_to_convert_from, currency_to_convert_to)
        print(f'Rate for {currency_to_convert_from} -> {currency_to_convert_to} is {rate}')
    else:
        print('Conversion not available')


main()
