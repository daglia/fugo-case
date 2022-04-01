from datetime import datetime

def log(msg):
  print(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - {msg}')