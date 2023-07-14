***Кластер postgres + daemon Patroni (предотвращает всевозможные отвалы и сплитбрейны) + ETCD (отказоустойчивая БД) + pgbouncer (легковесный пул соединений, решает проблему большого кол-ва линков) + HAProxy*** :
1. https://www.youtube.com/watch?v=4PJIdMRrGCE&list=PLprvDkBQwz6YQLJQ_qlm3-gkk-BXYuuR0
2. https://www.youtube.com/watch?v=slkA7qJyW3E

**Синхронный режим реплики - клиент получает подтверждение транзакции только тогда, когда данные записаны на все хосты**

![[Pasted image 20221230135239.png]]

![[Pasted image 20221230142514.png]]

***КЛАСТЕР С REPMGR***
https://www.youtube.com/watch?v=LvDHdgQqaQw
***1 ШАГ - РЕПЛИКАЦИЯ***
***По порядку:*** 
- Установка необходимых пакетов на все машины 
yum install -y repmgr12 postgresql12 postgresql12-server postgresql12-contrib postgresql12-libs
- На мастере инициализировал БД 
/usr/pgsql-12/bin/postgresql-12-setup initdb
- Чтобы на пользователе работала команда repmgr 
cat >>/var/lib/pgsql/.bash_profile<<'EOF'
PATH=$PATH: $HOME/bin:/usr/pgsql-12/bin
export PATH
EOF
- Включение в автозагрузку 
systemctl enable repmgr-12 postgresql-12
- Правка postgresql.conf (стандартная порт и ip адресс)
- Создание файла repmgr.conf в PGDATA со стандартными настройками 
cat >/var/lib/pgsql/12/data/repmgr.conf<<EOF`
shared_preaload_libraries = 'repmgr'
max_wal_senders = 10
max_replication_slots = 15
wal_level = 'replica'
hot_standby = on
archive_mode = on
archive_command  = '/bin/true'
EOF
- Добавляем repmgr.conf в конец основного кфг 
echo -e "include_if_exists 'repmgr.conf'" >> /var/lib/pgsql/12/data/postgresql.conf 
- Правка файла pg_hba.conf 
	Для начал можно мувнуть реплику 
mv /var/lib/pgsql/12/data/pg_hba.conf{,.b}
	Дальше создали новый файл и вписали туда 
cat >/var/lib/pgsql/12/data/pg_hba.conf<<EOF`
local    all             all                            peer
host     all             all           127.0.0.1/32     md5
host     study_db        study         192.168.31.0/24  md5

local    replication     repmgr                         trust
host     replication     repmgr        127.0.0.1/32     trust
host     replication     repmgr        192.168.31.0/24  trust

local    repmgr          repmgr                         trust
host     repmgr          repmgr        127.0.0.1/32     trust
host     repmgr          repmgr        192.168.31.0/24  trust
- Изменение прав для новый файлов 
chown postgres:postgres /var/lib/pgsql/12/data/{repmgr.conf,pg_hba.conf}
chmod 600 /var/lib/pgsql/12/data/{repmgr.conf,pg_hba.conf} 
- После этого postgresql уже должен стартовать 
- Создание пользователя и БД для repmgr 
createuser -s repmgr
createdb repmgr -O repmgr
`\c repmgr`
- Присвоил что-то не понятное пользователю repmgr 
ALTER USER repmgr SET search_path TO repmgr, "$user", public; 
- Настройка файла /etc/repmgr/12/repmgr.conf для всех пользователей, меняется node id, name и ip 
mv /etc/repmgr/12/repmgr.conf{,.b}
cat >/etc/repmgr/12/repmgr.conf<<`EOF`
node_id=1
node_name='standby1'
conninfo='host=192.168.31.211 dbname=repmgr user=repmgr connect_timeout=4'
data_directory='/var/lib/pgsql/12/data/'
use_replication_slots=yes
log_file='/var/log/repmgr/repmgr.log'
pg_bindir='/usr/pgsql-12/bin/'
ssh_options='-q -o ConnectTimeout=10 -o "StrictHostKeyChecking no"'
failover=automatic
priority=80
reconnect_attempts=6
reconnect_interval=10
promote_command='/usr/pgsql-12/bin/repmgr standby promote -f /etc/repmgr/12/repmgr.conf'
follow_command='/usr/pgsql-12/bin/repmgr standby follow -f /etc/repmgr/12/repmgr.conf -w --upstream-node-id=%n'
service_start_command = 'sudo systemctl start postgresql-12'
service_stop_command = 'sudo systemctl stop postgresql-12'
service_restart_command = 'sudo systemctl restart postgresql-12'
service_reload_command = 'sudo systemctl reload postgresql-12'
EOF
- Уже сам кластер 
	Под хостом:
repmgr primary register 
repmgr cluster show - проверяем кластер 
	Под standby: 
repmgr -h 192.168.31.207 -U repmgr -d repmgr standby clone
	Запускаем postgresql на standby и активируем из под пользователя postgres
systemctl start postgresql-12 
repmgr standby register
- Проверяем на хосте 
repmgr cluster show 

***2 ШАГ - ОТКАЗОУСТОЙЧИВОСТЬ***







[[Linux]] [[postgreSQL (БД)]]