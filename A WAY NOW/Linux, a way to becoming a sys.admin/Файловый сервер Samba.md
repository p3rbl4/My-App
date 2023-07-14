https://yodo.im/samba
https://serverspace.ru/support/help/configuring-samba/#step3
ip_address файл сервера - 192.168.31.26

**SMB** - протокол работы с файловым серверам от **Microsoft**.
На самом деле сейчас **Samba** умеет не только работать файловым сервером, но еще и контроллером доменов, совместимым с **Microsoft Active Directory** с немного урезанными групповыми политиками.

**Не секрет что для своей работы Samba использует порты: 139/tcp и 445/tcp.**
apt install samba
После скачивания Samba 
**cd /etc/samba**
***Настройка конфигурации***
Переместим дефолтную конфигурацию на всякий случай 
**sudo mv smb.conf smb.conf.old**

Теперь создаем два пустых файла:
**sudo touch smb.conf**
**sudo touch smbusers**

А также создадим папку, которую будем расшаривать в сеть.
**sudo mkdir /opt/FirstTestShare**
**sudo chmod 0777 /opt/FirstTestShare**

Открываем файл **smb.conf**
Настройка представления сервера в сети Windows 
[global]
server string = Test Fileserver Samba
workgroup = WORKGROUP
server role = standalone server
security = user
passdb backend = smbpasswd
smb passwd file = /etc/samba/smbusers
encrypt passwords = yes
map to guest = bad user
log file = /var/log/samba/log.%m
syslog = 3
[FirstTestShare]
comment = Our First Test Share
path = /opt/FirstTestShare
browseable = yes
writeable = yes
create mask = 0775
directory mask = 0775

***Перед тем как запускать сервис необходимо проверить конфиг***
**testparm -s**

После сохранения правильного конфига необходимо перезапускать 
**sudo service smbd restart
sudo systemctl enable smbd
sudo service smbd status**

Создаём 3 пользователей, для доступа к папке 
**sudo useradd -c "samba test n1" -s /sbin/nologin/ test1**

Параметр **-s /sbin/nologin** означает, что эти пользователи не имеют права логиниться в консоль сервера. Это важно с точки зрения безопасности.
**sudo smbpaswwd -a test1**
А вот теперь мы можем ввести учетные данные любого из пользователей и попасть на шару.

В организации работал бухгалтер test1. Но время идет, фирма растет, нагрузка растет.
И вот наняли ему в помощь test2.
Пользователь test2 заходит на шару в папку Buh и может все файлы просматривать, но не может их редактировать.

Нам требуется групповая работа над файлами. Значит будем настраивать общую группу для пользователей test1 и test2.
**sudo groupadd buh**
Устанавливаем группу buh по умолчанию для пользователей test1 и test2
**sudo usermod -aG buh test1
sudo usermod -aG buh test2**

**sudo service smbd restart**
Меняем настройки владельца для всех файлов, которые уже были созданы и для самой папки Buh
**sudo chown -R test1:buh /opt/FirstTestShare/Buh**

***SMB STATUS***

1. Список открытых сессий (один пользователь можешь открыть их несколько как с одного компьютера, так и с нескольких). Ключевое поле тут PID. Это идентификатор сессии.
2. Список открытых шар, с указанием pid сессии.
3. Список заблокированных на запись файлов. Для нас будет полезно знать, что PID сессии равнозначен Proccess ID в ОС Linux. Запомним эту информацию. Она нам пригодится через пару мгновений

[[Linux]] [[системное администрирование]] 
#Linux #samba 