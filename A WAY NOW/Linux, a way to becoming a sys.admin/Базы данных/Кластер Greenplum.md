***Пошаговый мануал для постройки кластера greenplum из мастера, стендбая и 3 сегментов***

https://www.youtube.com/watch?v=-T3zl7aE0Yk
https://gpdb.docs.pivotal.io/6-2/install_guide/prep_os.html	

- Отключение Firewalld и SELinux
- Обновление, скачивание yum install epel-release htop nano ntpd wget
- В файле /etc/hosts указать все хосты которые будут присутствовать в кластере 
В таком роде: 192.168.31.220 gphost
- В файле /etc/ssh/sshd_config раскомментировать MaxSessions 200 и MaxStartups 200, после перезагрузить сервис 
- Настройка ntp, а именно синхронизация часов на всех машинах, на мастере указать сам ntp сервер, на стендбае сервере server ip_master prefer и server ntp, а на сегментах server ip_master prefer и server ip_standby 
- Дальше нужно создать группу и пользователя для БД
groupadd gpadmin
useradd gpadmin -u 997-r -m -g gpadmin - главное чтобы был один UID у всех пользователей в кластере
passwd gpadmin - любой пароль (toor) 
- Из под пользователя gpadmin настраиваем SSH, а именно создаём пару ключей 
su - gpadmin
ssh-keygen -t rsa -b 4096
Пароль не нужен, чтобы была возможность подключения без пароля 
-  Из под рута зайти в visudo и расскоментировать строчку 
%wheel        ALL=(ALL)       NOPASSWD: ALL
	Дальшей выполнить
	usermod -aG wheel gpadmin
- Установка Greenplum 
wget https://github.com/greenplum-db/gpdb/releases/download/6.23.0/open-source-greenplum-db-6.23.0-rhel7-x86_64.rpm
yum install ./open-source-greenplum-db-6.23.0-rhel7-x86_64.rpm -y
- Даём права на greenplum пользователю 
sudo chown -R gpadmin:gpadmin /usr/local/greenplum*
- Из под пользователя gpadmin в .bashrc добавить строчку . /usr/local/greenplum-db/greenplum_path.sh , чтобы команды greenplum работали и чтобы активировать переменную $GPHOME 
- На каждом хосте из под пользователя необходимо поделится ssh ключами, также собственным 
ssh-copy-id hostname - именно **хостнейм**
`Если накосячил, то удали старые ssh через ssh-keygen -R ip или хост`
https://techreact.ru/udalit-ustarevshie-klyuchi-ssh/
- Создать файл hostfile_exkeys на мастере и скопировать туда содержимое файла /etc/hosts и выполнить 
gpssh-exkeys -f hostfile_exkeys
- Создать директорию /data/master на мастере и стендбае в корне пользователя / и дать права созданным директориям 
chown gpadmin:gpadmin /data
chown gpadmin:gpadmin /data/master
- На сегментах создать директории data и data/primary также в корне / и также выдать права 
- Создать директорию gpconfigs на мастере в корне и в ней файл hostfile_gpinitsystem туда внести хосты ***сегментов*** 
- Для создания файла инициализации, берём примерный конфиг и переделываем его под себя 
cp $GPHOME/docs/cli_help/gpconfigs/gpinitsystem_config /home/gpadmin/gpconfigs/gpinitsystem_config
- Настройка конфига 
Изменяем: 
declare -a DATA_DIRECTORY=(/data/primary) - директории сегментов
MASTER_HOSTNAME=192.168.31.220 - лучше использовать хостнейм 
- Инициализируем БД 
gpinitsystem -c gpconfigs/gpinitsystem_config -h gpconfigs/hostfile_gpinitsystem 
Если всё ок, то подтверждаем создание
- В .bashrc добавляем - на мастере и стендбае 
export MASTER_DATA_DIRECTORY=/data/master/gpseg-1
export PGPORT=5432
- Инициализация Standby
gpinitstandby -s host_standby
https://sites.google.com/a/greenplumdba.com/gpdb/troubleshooting-dca-issues

***Осуществление репликации***
https://habr.com/ru/company/tinkoff/blog/267733/

- Отключаем postmaster на мастере, или если рабочая ситуация, то сервер грубо говоря отпал 
/usr/local/greenplum-db-6.23.0/bin/pg_ctl stop --pgdata=/data/master/gpseg-1 --mode=fast
посмотреть через ps aux остановился ли процесс
- Активация Standby на нём же
gpactivatestandby -d /data/master/gpseg-1


***Команды для работы с Greenplum***

**gpstate**
https://greenplum.org/checking-greenplum-database-status-linux/

Через саму БД можно вывести таблицу хостов в кластере 
select * from gp_segment_configuration ;


[[Кластеризация]] [[Кластер postgresql]] 
#Linux 





