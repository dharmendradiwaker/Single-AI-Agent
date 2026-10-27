from langchain.tools import tool
import requests



# Custom Tool
@tool
def currency_converter(amount: float, from_currency: str, to_currency: str):
    """
    Convert an amount from one currency to another using the latest exchange rates.

    Use this whenever the user asks to convert money or asks for an exchange rate.

    Args:
        amount: the amount of money to convert (use 1 to just get the exchange rate)
        from_currency: 3-letter ISO currency code to convert from (e.g., 'USD', 'EUR', 'INR')
        to_currency: 3-letter ISO currency code to convert to (e.g., 'USD', 'EUR', 'INR')
    """

    url = "https://api.frankfurter.dev/v1/latest"
    params = {"amount": amount,
              "from": from_currency.upper(),
              "to": to_currency.upper()}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return f"Currency conversion failed: {resp.json().get('message', resp.text)}"

        data = resp.json()
        converted = data['rates'][to_currency.upper()]

        return {"amount": data['amount'],
                "from": data['base'],
                "to": to_currency.upper(),
                "converted_amount": converted,
                "rate": round(converted / data['amount'], 6) if data['amount'] else None,
                "rate_date": data['date']}
    except Exception:
        return "Currency converter tool unable to fetch the exchange rate"
