#!/bin/bash


if pgrep -f /root/er/bot.py
then
  echo "Процесс bot.py запущен.ЗБС"
  rm -rf /root/pathfinder/py/mainnet.sqlite
  rm -rf /root/pathfinder/py/mainnet.sqlite-wal
else
  echo "Процесс bot.py не запущен.хуёво. запускаю..."
  rm -rf /root/pathfinder/py/mainnet.sqlite
  rm -rf /root/pathfinder/py/mainnet.sqlite-wal
  source /root/test/my_env/bin/activate
  pip uninstall selenium webdriver-manager -y
  sleep 5
  pip install selenium webdriver-manager
  sleep 5
  python /root/er/bot.py
fi
