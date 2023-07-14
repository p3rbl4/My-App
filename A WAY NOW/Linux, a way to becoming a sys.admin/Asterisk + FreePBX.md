Данные от аккаунта yodo.im
Логин: p3rbl4business@gmail.com
Пароль: K3hyMnVB
Данные от виртуалки Asterisk 
Логин: ron 
Пароль: toor
ip_address - 192.168.31.176
Курс по настройке Asterisk можно повторно проходить здесь https://yodo.im/asterisk 
Основные моменты: 
Устанавливаем с официального сайта последнюю версию на момент написания 19, командой wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-19-current.tar.gz и распоковкой tar zxf ... После чего делаем сборку командой ./configure и устанавливаем необходимые пакеты. (sudo apt install build-essential).

Используем скрипт, который установит нам всё необходимое 
cd contrib/scripts
sudo ./install_prereq install
sudo ./install_prereq install-unpackaged

Завершаем установку пакетов с корневой папки asterisk 19. . . командой ./configure --with-pjproject-bundled

Сборка:
sudo make 
sudo make install 

Создадим конфиги по-умолчанию
sudo make samples
sudo make config
sudo ldconfig

Запустим Asterisk 
sudo systemctl start asterisk

Проверка: 
sudo asterisk -rvvv

Установка FreePBX и окончательная настройка Asterisk пользователей:
https://yodo.im/free_pbx

Устанавливаем нужные репозитории.
apt-get install software-properties-common
add-apt-repository ppa:ondrej/php

Устанавливаем пакеты.
Смотрим официальные документации
[https://wiki.freepbx.org/display/FOP/Version+16.0+Installation](https://wiki.freepbx.org/display/FOP/Version+16.0+Installation)
Вместо python-dev писать python2-dev

Непосредственная установка FreePBX
wget http://mirror.freepbx.org/modules/packages/freepbx/freepbx-16.0-latest.tgz
tar -xvzf freepbx-16.0-latest.tgz
apt install nodejs

Устанавливаем нужные зависимости.
./install -n

Далее меняем пользователя в Apache на asterisk и разрешаем AllowOverride
sed -i 's/^\(User\|Group\).*/\1 asterisk/' /etc/apache2/apache2.conf
sed -i 's/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

Увеличиваем upload_max_filesize
sed -i 's/\(^upload_max_filesize = \).*/\120M/' /etc/php/7.4/apache2/php.ini
sed -i 's/\(^upload_max_filesize = \).*/\120M/' /etc/php/7.4/cli/php.ini

Включаем и перезапускаем Apache.
a2enmod rewrite
systemctl restart apache2

FreePBX имеет кучу модулей, расширяющих базовый функционал. Поставим три нужных:
fwconsole ma downloadinstall arimanager
fwconsole ma downloadinstall asteriskinfo
fwconsole ma downloadinstall queues
Модуль queues позволит настраивать входящую очередь звонков. Модуль **asteriskinfo** даст нам возможность отладки настроек в графическом режиме. Чтобы не залезать на сервер по **ssh** и не заходить в **asterisk -r.** От модуля arimanager зависит модуль **asteriskinfo** и поэтому устанавливается перед ним.

В nano открой файл **/etc/systemd/system/freepbx.service**
И добавить 
**[Unit]**
**Description=FreePBX VoIP Server**
**After=mariadb.service**
**[Service]**
**Type=oneshot**
**RemainAfterExit=yes**
**ExecStart=/usr/sbin/fwconsole** **start -q**
**ExecStop=/usr/sbin/fwconsole** **stop -q**
**[Install]**
**WantedBy=multi-user.target**

Устанавливаем FreePBX в автозагрузку 
systemctl enable freepbx.service
systemctl start freepbx.service

НАСТРОЙКА ВЕБ-ИНТЕРФЕЙСА FREEPBX

SIP - сигнальный протокол. Его задача взять абонента А и абонента Б и договориться о разговоре. SIP отвечает за то что у вас в трубке гудит, за то что вы получаете сигнал занято.
Еще раз - задача SIP установить соединение.

Запрещаем анонимные входящие звонки во вкладке "Установки Asterisk для SIP".

Существуют 2 драйвера протокола SIP: chan_pjsip и chan_sip.
chan_sip позволяет подключать только одно устройство к одной учетке.
pjsip несколько

Оставляем chan_pjsip, переходим в дополнительные настройки и найдёт строку SIP Channel Driver
И изменим порт на 5060 в окне Установки канала SIP и включаем SRV 

После этого сохраняем и перезапускаем сервер fwconsole restart

Здесь я столкнулся с проблемой Unable to install module pm2 
Решение: 
(https://github.com/nodesource/distributions/blob/master/README.md)
curl -fsSL https://deb.nodesource.com/setup_19.x | sudo -E bash - &&\
sudo apt-get install -y nodejs

Нужно добавить модуль app_macro в Asterisk для соединения абонентов
**cd Asterisk ...
make menuselect
->applications 
->deprecated
->app_macro**
**Save&exit
make
make install
asterisk -rx 'core restart now'**

Добавляем 3 внутренних номера и проверяем работаспособность через софтфоны Zoiper и 3CX, MicroSIP




[[Linux]] [[системное администрирование]] [[телефония]] [[Trunk (SIP-trunk)]] 