# coding: utf-8
# Author: Ra93POL
# E-mail: kostyan_93@mail.ru
# -*- coding: utf-8 -*-
# Date: 25.07.2014 18.08.2015
import urllib, urllib2, json, hmac, hashlib, os, time

class API():
  __url = "https://api.exmo.com/api_v2/"
  def __init__(self, api_key, api_secret):
    self.__api_key = api_key
    self.__api_secret = api_secret

  def public_api(self, api_name, api_params={}):
    x = 1
    while x:
      try:
        req = urllib2.Request(self.__url + api_name+'?'+urllib.urlencode(api_params), headers={'Accept-Charset': 'utf-8' })
        x = 0
      except:
        print 'Error in public_api'
        time.sleep(0.1)
    answer_json = urllib2.urlopen(req).read()
    jd = json.JSONDecoder()
    return jd.decode(answer_json) 
 
  def auth_api(self, api_name, api_params={}):
    api_params["nonce"] = str(time.time()).split('.')[0]
    post_data = urllib.urlencode(api_params) 

    sign = hmac.new(key=self.__api_secret, msg=post_data, digestmod=hashlib.sha512).hexdigest()
    header = {"Key": self.__api_key, "Sign":sign}

    x = 1  # this part of code is funny and not deciding problem. Problem is about socket.
    while x:
      try:
        req = urllib2.Request(self.__url+api_name, post_data, headers=header)
        x = 0
      except:
        print 'Error in auth_api'
        time.sleep(0.1)
    answer_json = urllib2.urlopen(req).read()

    jd = json.JSONDecoder()
    return jd.decode(answer_json) 


  # ############## Базовые функции ################

  # public api

  def shell_public(self, api_name, api_params={}):
    '''Обёртка, чтобы не повторять код '''
    answer = self.public_api(api_name, api_params)
    if answer['success']: return answer['data']
    else: return answer['error']

  def MarketData(self, pair):
    ''' Список сделок по валютной паре '''
    api_params = {'pair': pair} 
    return self.shell_public('market_data', api_params)

  def OrdersBook(self, pair):
    ''' Книга текущих ордеров по валютной паре '''
    api_params = {'pair': pair} 
    return self.shell_public('orders_book', api_params)

  def Currencies(self):
    ''' Список валют ''' 
    return self.shell_public('currencies')
 
  def Pairs(self):
    ''' Список валютных пар '''
    return self.shell_public('pairs')

  # auth api

  def shell_auth(self, api_name, api_params={}):
    '''Обёртка, чтобы не повторять код '''
    answer = self.auth_api(api_name, api_params)
    if answer['success']: return answer['data']
    else: return answer['error']
 
  def GetInfo(self):
    ''' Получение информации об аккаунте (баланс) сервере '''
    return self.shell_auth('get_info') 

  def MyOrders(self, pair):
    ''' Получение списка активных ордеров '''
    api_params = {'pair': pair} 
    return self.shell_auth('my_orders', api_params)
 
  def MyHistory(self, pair):
    ''' Получение списка сделок '''
    api_params = {'pair': pair} 
    return self.shell_auth('my_history', api_params)
 
  def MyCanceled(self, pair):
    ''' Получение списка отменённых ордеров '''
    api_params = {'pair': pair} 
    return self.shell_auth('my_canceled', api_params)
 
  def MyCredits(self):
    ''' Получение списка активных кредитов ''' 
    return self.shell_auth('my_credits')
 
  def CancelOrder(self, order_id):
    ''' Отмена ордера '''
    api_params = {'order_id': order_id} 
    return self.shell_auth('cancel_order', api_params)
 
  def CreateOrder(self, pair, _type, amount, buy_price, stop_loss, take_profit, use_trailing, trailing_stop):
    ''' Создание ордера '''
    api_params = {'pair': pair, 'type': _type,
      'amount': amount, 'buy_price': buy_price,
      'stop_loss': stop_loss, 'take_profit': take_profit,
      'use_trailing': use_trailing,
      'trailing_stop': trailing_stop,
      'use_credit': 'false'} 
    return self.shell_auth('create_order', api_params)

  # ########## Высоуровневые функции ############
  def getPrice(self, pair, _type):
    answer = self.Pairs()
    for answ in answer:
      if answ['name'] == pair:
        return answ[_type]

  def BuySell(self, pair, _type, amount, price):
    if _type=='buy':
      buy_price = price
      take_profit = 0
    elif _type=='sell':
      buy_price = 0
      take_profit = price
      _type = 'complex_' + _type
    answer = self.CreateOrder(pair, _type, amount, buy_price, 0, take_profit, 'false', 0)
    return answer['order_id']
 
  def checkOrder(self, order_id, pair):
    active_orders = self.MyOrders(pair)
    #credit_orders = MyCredits(pair)
    #cancel_orders = MyCanceled(pair) 
    #for order in credit_orders:
    #  if order['order_id'] == order_id:
    #    return 0
    for order in active_orders:
      if order['order_id'] == order_id:
        return 0
    return 1
    #for order in cancel_orders:
    #  if order['order_id'] == order_id:
    #    return 2

  def getBalance(self, currency):
    return self.GetInfo()['balances_avialble'][currency]
