
"""
General Notes:
    - project will be a 'forgetful' bot, meaning that it only stores enough data for it to calculate the indicators it uses
    - forgetful also means that it will not need a database
    - future intention is that it is not forgetful and stores everything
    - there is an indicator library called 'ta' which can be used for most of the technical analysis

Project structure:
    - Bybit Client (downloaded)
    - Kline data
        - download from coinbase api - as data is better than the bybit API
        - do technical analysis on the data
        - define different states based on the technical analysis
    - Logic for the client
        - different actions based on different states
        - stake size / risk management
        - etc.

"""


import sched, time, bybit

api_key = ''
private_key = ''
commission = 0.075

def event_action(scheduler):
    print('hello im doing an action')
    scheduler.enterabs(int(time.time()) + 1, 0, event_action, (scheduler))

def setup_client(client):
    """ Does initial setup tasks for a new client """
    print('Doing setup tasks')
    print('Getting leverage')
    resp = client.Positions.Positions_userLeverage().result()
    leverage = resp[0].get('result').get('BTCUSD').get('leverage')

    if leverage != 5:
        print('Setting leverage to 5x')
        print(client.Positions.Positions_saveLeverage(symbol="BTCUSD", leverage="5").result())
    else:
        print('Leverage is 5x')

    kwargs = {"symbol": "BTCUSD", "interval": "5", "from": (int(time.time()) - 200*300)}
    print(client.Kline.Kline_get(**kwargs).result())


    

def main():
    # init new scheduler - more on this once the rest is working
    # EventScheduler = sched.scheduler(time.time, time.sleep)
    # EventScheduler.run()

    # init bybit client
    client = bybit.bybit(test=True, api_key=api_key, api_secret=private_key)
    setup_client(client)
    


if __name__ == '__main__':
    print('initialising')
    main()
