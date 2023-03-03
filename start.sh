#!/bin/bash

#Env
MY_IP=$(ip addr show | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')
TOKEN=$(grep $MY_IP "/root/My-App/tokens.txt" | awk '{print $2}')

# Команды для выполнения
cmds=(
    "apt update"
    "sed -i 's/zalupka/'$TOKEN'/g' /root/My-App/bot.py"
    "apt install python3-pip -y"
    "apt install python3-venv -y"
    "mkdir test"
    "cd test"
    "python3.8 -m venv my_env"
    "pip install --upgrade pip"
    "wget -nc https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    "apt update"
    "sudo apt install -f ./google-chrome-stable_current_amd64.deb -y"
    "source /root/test/my_env/bin/activate"
    "apt install nano -y"
    "pip install godel"
    "pip install godel[data-tools]"
    "pip install godel[web3]"
    "pip install langdetect"
    "pip install importlib-metadata"
    "pip install selenium"
    "pip install webdriver-manager"
    "pip install selenium webdriver-manager"
    "python /root/My-App/bot.py"
)

# Функция для проверки успешности выполнения предыдущей команды
check_status () {
    if [ $1 -eq 0 ]; then
        echo "Предыдущая команда выполнена успешно"
        sleep 2
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

