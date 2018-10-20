import requests
from twilio.rest import Client
import time


class StockInformation:
    """
    Stock information API service,
    gives the abillity to retrieve stock prices
    """
    class AlphaVantageApi:
        """
        The registered API key
        for an API key, please signup at: https://www.alphavantage.co/
        """
        API_KEY = 'Update your API key'

    @staticmethod
    def get_stock_price(stock_symbol):
        """
        Given the stock symbol, retrieves its price.
        For stock symbols: https://www.nasdaq.com/symbol/
        :param stock_symbol: the stock symbol
        :return: stock price
        """
        paramters = {
            'symbol': stock_symbol,
            'function': 'GLOBAL_QUOTE',
            'apikey': StockInformation.AlphaVantageApi.API_KEY
        }
        reply = requests.get('https://www.alphavantage.co/query', params=paramters)
        reply.raise_for_status()
        stock_price = float(reply.json()['Global Quote']['05. price'])
        return stock_price


class WhatsAppNotifier:
    """
    Sends whatsapp notifications using the Twillio API service
    """
    class TwilloWhatsupApi:
        """
        The twillio API service access tokens,
        register a token here:
        https://www.twilio.com/whatsapp
        """
        ACCOUNT_SID = 'Update your account SID'
        AUTH_TOKEN = 'Update your authentication token'
        API_NUMBER = 'Update your api number : whatsapp:.....'

    def __init__(self):
        self.twillo_client = Client(WhatsAppNotifier.TwilloWhatsupApi.ACCOUNT_SID, WhatsAppNotifier.TwilloWhatsupApi.AUTH_TOKEN)

    def send_whatsup_notification(self, message_to_send, destination_number):
        """
        Sends the given message to the given destination number as a whatsapp notification
        :param message_to_send: an string message
        :param destination_number: a phone number (with an internation prefix '+')
        :return: The message sent sid
        """
        # Send the message
        message = self.twillo_client.messages.create(
            body=message_to_send,
            from_=WhatsAppNotifier.TwilloWhatsupApi.API_NUMBER,
            to='whatsapp:{}'.format(destination_number)
        )
        return message.sid


class StockNotifier:
    """
    Notifies about the registered stock price changes using whatsapp notifications
    """

    # Monitor interval in seconds
    MONITOR_INTERVAL = 3*60*60

    def __init__(self, destination_number, stock_symbol, stock_buy_price, stock_profit_per_notif=1.5, stock_loss_per_notif=-2, ):
        self.stock_symbol = stock_symbol
        self.stock_buy_price = stock_buy_price
        self.stock_profit_per_notif = stock_profit_per_notif
        self.stock_loss_per_notif = stock_loss_per_notif
        self.destination_number = destination_number
        self.whatsup_notifier = WhatsAppNotifier()

    def monitor_and_notify(self):
        """
        Monitoring the stock price
        :return:
        """
        while True:
            stock_current_price = StockInformation.get_stock_price(self.stock_symbol)
            # Calculate the change percentage
            stock_change_percent = self._stock_difference(stock_current_price)
            # Send a whatsup notification if the percentage change met the barrier
            if stock_change_percent >= self.stock_profit_per_notif or stock_change_percent <= self.stock_loss_per_notif:
                message_to_send = 'Stock {} with buy price {} is now {} which is change in {} percent'.format(self.stock_symbol, self.stock_buy_price, stock_current_price, stock_change_percent)
                self.whatsup_notifier.send_whatsup_notification(message_to_send, self.destination_number)
                print('Sent update about {} stock to {}'.format(self.stock_symbol, self.destination_number))
            # Sleep until the next cycle
            time.sleep(StockNotifier.MONITOR_INTERVAL)

    def _stock_difference(self, stock_now):
        return (stock_now - self.stock_buy_price) / self.stock_buy_price * 100



def main():
    # Set stock initial details
    stock_symbol = 'AMZN'
    stock_buy_price = 1900
    # Set the notification borders
    stock_profit_percent = 1.5
    stock_lose_percent = -2
    # destination number
    destination_number = 'Enter the destination phone number (with internation prefix)'
    # Set the stock notifier
    stock_notifier = StockNotifier(destination_number, stock_symbol, stock_buy_price, stock_profit_percent, stock_lose_percent)
    # Monitor and notify
    stock_notifier.monitor_and_notify()


if __name__ == '__main__':
    main()
