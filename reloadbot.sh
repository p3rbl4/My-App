#!/bin/bash

#ENV
OLDTOKEN=$(head -n1 /root/My-App/tokens.txt)
NEWTOKEN=$(head -n2 /root/My-App/tokens.txt | tail -1)
#Script
if pgrep -f /root/My-App/bot.py > /dev/null
then
   echo "Команда 'bot.py' уже запущена.Выключаю бота..."
   kill -9 $(ps aux | grep /root/My-App/bot.py | awk '{print $2}' | head -1)
   rm -rf /root/pathfinder/py/mainnet.sqlite
   sleep 2
   source /root/test/my_env/bin/activate
   python /root/My-App/bot.py
else
   echo "'bot.py' не запущен, включаю бота..."
   source /root/test/my_env/bin/activate
   python /root/My-App/bot.py

fi
