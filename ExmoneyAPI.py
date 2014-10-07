# coding: utf-8
# Author: Ra93POL
# E-mail: kostyan_93@mail.ru
# VK.com: http://vk.com/ra93pol
# Date: 25.07.2014
import urllib, urllib2, json, hmac, hashlib, os, time

api_key = None
api_secret = None
url = "http://api.exmoney.com/api_v2/"
"""
def get_nonce():
  name="nonce.txt"
  if os.path.exists(name)==0:
    f = open(name, "w")
    f.write("7")
    f.close()
 
  f = open(name, "r")
  nonce = f.read()
  f.close()

  f = open(name, "w")
  f.write(str(int(nonce)+1))
  f.close()

  return nonce 
"""
def public_api(api_name, api_params={}):
  global url
  x = 1
  while x:
    try:
      req = urllib2.Request(url+api_name+'?'+urllib.urlencode(api_params), headers={'Accept-Charset': 'utf-8' })
      x = 0
    except:
      print 'Error in public_api'
      time.sleep(0.1)
  answer_json = urllib2.urlopen(req).read()
  jd = json.JSONDecoder()
  return jd.decode(answer_json) 
 
def auth_api(api_name, api_params={}):
  global url
  api_params["nonce"] = str(time.time()).split('.')[0]#get_nonce() 
  post_data = urllib.urlencode(api_params) 

  sign = hmac.new(key=api_secret, msg=post_data, digestmod=hashlib.sha512).hexdigest()
  header = {"Key": api_key, "Sign":sign}

  x = 1  # this part of code is funny and not deciding problem. Problem is about socket.
  while x:
    try:
      req = urllib2.Request(url+api_name, post_data, headers=header)
      x = 0
    except:
      print 'Error in auth_api'
      time.sleep(0.1)
  answer_json = urllib2.urlopen(req).read()

  jd = json.JSONDecoder()
  return jd.decode(answer_json) 


# ############## Базовые функции ################

# public api

def shell_public(api_name, api_params={}):
  '''Обёртка, чтобы не повторять код '''
  answer = public_api(api_name, api_params)
  if answer['success']: return answer['data']
  else: return answer['error']

def MarketData(pair):
  ''' Список сделок по валютной паре '''
  api_params = {'pair': pair} 
  return shell_public('market_data', api_params)

def OrdersBook(pair):
  ''' Книга текущих ордеров по валютной паре '''
  api_params = {'pair': pair} 
  return shell_public('orders_book', api_params)

def Currencies():
  ''' Список валют ''' 
  return shell_public('currencies')
 
def Pairs():
  ''' Список валютных пар '''
  return shell_public('pairs')

# auth api

def shell_auth(api_name, api_params={}):
  '''Обёртка, чтобы не повторять код '''
  answer = auth_api(api_name, api_params)
  if answer['success']: return answer['data']
  else: return answer['error']
 
def GetInfo():
  ''' Получение информации об аккаунте (баланс) сервере '''
  return shell_auth('get_info') 

def MyOrders(pair):
  ''' Получение списка активных ордеров '''
  api_params = {'pair': pair} 
  return shell_auth('my_orders', api_params)
 
def MyHistory(pair):
  ''' Получение списка сделок '''
  api_params = {'pair': pair} 
  return shell_auth('my_history', api_params)
 
def MyCanceled(pair):
  ''' Получение списка отменённых ордеров '''
  api_params = {'pair': pair} 
  return shell_auth('my_canceled', api_params)
 
def MyCredits():
  ''' Получение списка активных кредитов ''' 
  return shell_auth('my_credits')
 
def CancelOrder(order_id):
  ''' Отмена ордера '''
  api_params = {'order_id': order_id} 
  return shell_auth('cancel_order', api_params)
 
def CreateOrder(pair, type, amount, buy_price, stop_loss, take_profit, use_trailing, trailing_stop):
  ''' Создание ордера '''
  api_params = {'pair': pair, 'type': type,
    'amount': amount, 'buy_price': buy_price,
    'stop_loss': stop_loss, 'take_profit': take_profit,
    'use_trailing': use_trailing,
    'trailing_stop': trailing_stop,
    'use_credit': 'false'} 
  return shell_auth('create_order', api_params)

# ########## Высоуровневые функции ############
def getPrice(pair, type):
  answer = Pairs()
  for answ in answer:
    if answ['name'] == pair:
      return answ[type]

def BuySell(pair, type, amount, price):
  if type=='buy':
    buy_price = price
    take_profit = 0
  elif type=='sell':
    buy_price = 0
    take_profit = price
    type = 'complex_' + type
  answer = CreateOrder(pair, type, amount, buy_price, 0, take_profit, 'false', 0)
  return answer['order_id']
 
def checkOrder(order_id, pair):
  active_orders = MyOrders(pair)
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

def getBalance(currency):
  return GetInfo()['balances_avialble'][currency]
