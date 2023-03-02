#!/bin/bash

#ENV
OLDTOKEN=$(head -n1 /root/My-App/tokens.txt)
NEWTOKEN=$(head -n2 /root/My-App/tokens.txt | tail -1)
#Script
cmds=(
    "kill -9 $(ps aux | grep bot.py | awk '{print $2}' | head -1)"
    "rm -rf /root/pathfinder/py/mainnet.sqlite"
    "sed -i 's/'$OLDTOKEN'/'$NEWTOKEN'/g' /root/My-App/bot.py"
    "sed -i '1d' /root/My-App/tokens.txt"
    "source /root/test/my_env/bin/activate"
    "python /root/My-App/bot.py"
)
# Функция для проверки успешности выполнения предыдущей команды
check_status () {
    if [ $1 -eq 0 ]; then
        echo "Предыдущая команда выполнена успешно"
        sleep 3
    else
        echo "Предыдущая команда завершилась с ошибкой, прерываю выполнение скрипта"
        exit 1
    fi
}

# Перебираем команды и выполняем их
for cmd in "${cmds[@]}"
do
    eval "${cmd}"
    check_status $?
done

