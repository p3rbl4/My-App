zabbix:toor
https://www.zabbix.com/download?zabbix=6.0&os_distribution=ubuntu&os_version=22.04&components=server_frontend_agent&db=mysql&ws=nginx
Для всего добра необходимо установить mysql или postgresql 
Вся настройка почти на сайте, дальше уже нужно переходить в web интерфейс, localhost/zabbix 
Во вкладке Configuration создаём хост в него вписываем Hostname Samba (Asterisk) Templates ICMP Ping, Linux by Zabbix Agent, Group - жмем на кнопку Select и выбираем там Virtual Machines, Agent Interfaces - IP-адрес - 
На хосты мониторинга необходимо поставить zabbix-agent из репозитория который ставился в начале мануала 
После установки необходимо поменять конфиг **/etc/zabbix/zabbix_agentd.conf**
Hostname = Samba (Asterisk)
Server = IP-адрес
Перезапускаем сервис 
**Настройка уведомлений на почту (Actions)**
Trigger severity is greater than or equals. Average
***Только что мы задали условие по которому это действие будет выполняться для любого триггера важность которого выше чем просто предупреждение.***
Добавить пользователя 
![[Pasted image 20221217164643.png]]
И после чего осталось настроить Smtp во вкладке Administration -> Media Types 

***Написание шаблонов (templates)***
Configuration - Templates и создаём новый шаблон, в данном примере для Samba 
Дальше нужно найти шаблон в списке и нажать на items (элементы данных)
Элементы данных - это ключи на основе которых принимаются раздного рода решения
Создаём счётчик процессов smbd и nmbd, должно выглядеть вот так 
![[Pasted image 20221220154834.png]]
Но также необходимо чтобы всё это работало элемент данных который отвечате за пропуск портов 139 и 445 
![[Pasted image 20221220154939.png]]
***Вкладка triggers***
Создаём триггер и заполняем по шаблону 
![[Pasted image 20221220155044.png]]
Где expression нажать на кнопочку Add 
![[Pasted image 20221220155112.png]]
***Подключение шаблона к хосту***
**Configuration** - **Hosts** - выбираем хост **Samba** и поделючаем наш шаблон **Templates App Samba**
![[Pasted image 20221220155232.png]]
***Отладка мониторинга*** 
Отладку мониторинга можо производить и с веб интерфейса, но лучше всего через терминал, установим на Zabbix-сервер:
**zabbix-get**
И подключимся к smbd 
zabbix_get -s IP - хоста (samba) -k 'net.tcp.listen[445]'



[[Linux]] [[ssmtp (mail)]] [[Мониторинг Node_exporter + Postgres_exporter + Prometheus + Grafana]] 
