Настройка мониторинга производилась на основе созданного кластера Greenplum. 
	Master + Slave + 3X Node
Полезные источники для организации мониторинга:
- По данному мануалу производилась первоначальные действия 
https://avamk.ru/monitoring-greenplum-sredstvami-prometheus-grafana.html
- Но важно не забыдь включить **Ресурсные Группы** перед Postgres_exporter
[https://docs.vmware.com/en/VMware-Tanzu-Greenplum/6/greenplum-database/GUID-admin_guide-workload_mgmt_resgroups.html#topic8](https://vk.com/away.php?to=https%3A%2F%2Fdocs.vmware.com%2Fen%2FVMware-Tanzu-Greenplum%2F6%2Fgreenplum-database%2FGUID-admin_guide-workload_mgmt_resgroups.html%23topic8&cc_key=)
- Здесь описывается как установить расширения в саму БД для мониторинга 
[https://timeweb.cloud/tutorials/postgresql/rasshireniya-dlya-postgresql](https://vk.com/away.php?to=https%3A%2F%2Ftimeweb.cloud%2Ftutorials%2Fpostgresql%2Frasshireniya-dlya-postgresql&cc_key=)
- Рабочие дашборды для **postgres_exporter** и **node_exorter**  
![[node-exporter-full_rev29.json]]
В поле ID вписать 9628 - Postgres_exporter 
- Полезные ссылки 
	https://docs.ispsystem.ru/vmmanager-admin/monitoring/grafana/grafana-nastrojka-sobstvennogo-dashborda
	https://mcs.mail.ru/docs/additionals/cases/cases-monitoring/case-node-exporter

***Пошаговая настройка мониторинга***

- Установка node_exporter на всех машинах
`curl -Lo /etc/yum.repos.d/_copr_ibotty-prometheus-exporters.repo https://copr.fedorainfracloud.org/coprs/ibotty/prometheus-exporters/repo/epel-7/ibotty-prometheus-exporters-epel-7.repo
yum install node_exporter
useradd -s /sbin/false prometheus
- Конфигурируем сервис node_exporter /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
Restart=always
User=prometheus
Group=prometheus
ExecStart=/sbin/node_exporter

[Install]
WantedBy=multi-user.target
- Запускаем node_exporter
systemctl daemon-reload
systemctl start node_exporter
systemctl enable node_exporter
systemctl status node_exporter

Проверить метрики можно по **ip-server:9100/metrics**
- Подготовительные действия для установки postgres_exporter на всех машинах 
- Включение ресурных групп 
sudo yum install libcgroup-tools
nano /etc/cgconfig.conf
sudo cgconfigparser -l /etc/cgconfig.conf
sudo systemctl enable cgconfig.service
sudo systemctl start cgconfig.service
	На Мастере сделать 
gpconfig -s gp_resource_manager
gpconfig -c gp_resource_manager -v "group"
gpstop
gpstart
- Создадим в базе postgres ресурсную группу, пользователя и необходимые объекты для мониторинга на мастере
CREATE RESOURCE GROUP monitor_group WITH (concurrency=10, cpu_rate_limit=2, memory_limit=5, memory_shared_quota=0, memory_spill_ratio=0);
CREATE ROLE monitor NOSUPERUSER LOGIN password 'monitor' RESOURCE GROUP monitor_group;
ALTER USER monitor SET SEARCH_PATH TO monitor,pg_catalog;
ALTER USER monitor SET SEARCH_PATH TO monitor,pg_catalog;
CREATE SCHEMA IF NOT EXISTS monitor;
GRANT USAGE ON SCHEMA monitor TO monitor;
GRANT CONNECT ON DATABASE postgres TO monitor;
CREATE OR REPLACE FUNCTION get_pg_stat_activity() RETURNS SETOF pg_stat_activity AS
``$$ SELECT * FROM pg_catalog.pg_stat_activity; $$
LANGUAGE sql
EXECUTE ON MASTER
VOLATILE
SECURITY DEFINER;
CREATE OR REPLACE VIEW monitor.pg_stat_activity
AS
  SELECT * from get_pg_stat_activity();
GRANT SELECT ON monitor.pg_stat_activity TO monitor;
CREATE OR REPLACE FUNCTION get_pg_stat_replication() RETURNS SETOF pg_stat_replication AS
`$$ SELECT * FROM pg_catalog.pg_stat_replication; $$
LANGUAGE sql
EXECUTE ON MASTER
VOLATILE
SECURITY DEFINER;
CREATE OR REPLACE VIEW monitor.pg_stat_replication
AS
  SELECT * FROM get_pg_stat_replication();
GRANT SELECT ON monitor.pg_stat_replication TO monitor;
- Добавим файл паролей (_/home/gpadmin/.pgpass_). Последующие действия нужно выполнить на мастере и резервном мастере
`localhost:5432:*:monitor:monitor
chown gpadmin:gpadmin /home/gpadmin/.pgpass
chmod go-rwx /homegpadmin/.pgpass
- Добавим разрешение в файл pg_hba.conf.
host     all         monitor    127.0.0.1/28              md5
И потом ещё которые попросит добавить, можно сразу добавить стендбай и машину мониторинга 
host     all         all             192.168.31.220/32    md5
host     all         all             192.168.31.219/32    md5
host     all         all             192.168.31.221/32    md5
- Применим изменения
gpstop -u 
- Устанавливаем postgres_exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.11.1/postgres_exporter-0.11.1.linux-amd64.tar.gz -O - | tar -xzv -C /tmp
Актуальные версии гуглить 
cp /tmp/postgres_exporter-..../postgres_exporter /usr/local/bin/
rm -rf /tmp/postges_exporter...
chown -R gpadmin:gpadmin /usr/local/bin/postgres_exporter
- Создадим файл со строкой подключения /opt/postgres_exporter/postgres_exporter.env
DATA_SOURCE_NAME="postgresql://monitor:monitor@192.168.31.220:5432/postgres?sslmode=disable"
- Создадим файл дополнительными запросами /opt/postgres_exporter/queries.yaml
Брать от сюда - https://github.com/prometheus-community/postgres_exporter/blob/master/queries.yaml
- Сконфигурируем сервис /etc/systemd/system/postgres_exporter.service
[Unit]
Description=Prometheus exporter for Postgresql
Wants=network-online.target
After=network-online.target
[Service]
User=gpadmin
Group=gpadmin
WorkingDirectory=/opt/postgres_exporter
EnvironmentFile=/opt/postgres_exporter/postgres_exporter.env
ExecStart=/usr/local/bin/postgres_exporter --disable-settings-metrics --extend.query-path=/opt/postgres_exporter/querie$Restart=always
[Install]
WantedBy=multi-user.target
- Запускаем сервис postgres_exporter
systemctl daemon-reload
systemctl start postgres_exporter
systemctl enable postgres_exporter
systemctl status postgres_exporter

Проверить можно перейдя по **ip-server:9187/metrics**

***Установка и настройка Prometheus и Grafana производится на отдельной машине***

- Установка Prometheus ( Подготовка конфигурационного файла /opt/prometheus/prometheus.yml )
global:
  scrape_interval:     10s
  evaluation_interval: 10s
scrape_configs:
  - job_name: 'prometheus'
 static_configs:
  - targets: ['192.168.31.221:9090']
  - job_name: 'postgres_exporter'
    static_configs:
      - targets: ['192.168.31.220:9187', '192.168.31.219:9187']
  - job_name: 'gp_servers'
    scrape_interval: 10s
    static_configs:
      - targets: ['192.168.31.220:9100', '192.168.31.216:9100', '192.168.31.217:9100', '192.168.31.218:9100', '192.168.31.219:9100']
  - job_name: 'greenplum'
    static_configs:
      - targets: ['192.168.31.220:9187']
        labels:
          gpcluster: prod_cluster
          gprole: master
      - targets: ['192.168.31.219:9187']
        labels:
          gpcluster: prod_cluster
          gprole: slave
![[Pasted image 20230121143446.png]]
- Запускаем Docker образ перед этим предварительно скачать его 
docker run -d -p 9090:9090 -v /opt/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
- Установка Grafana так же из Docker образа 
docker run -d -p 3000:3000 grafana/grafana

***Настройка Grafana***

- Добавление Data Source 
Configuration -> Add Data Source и добавляем Prometheus 
![[Pasted image 20230121143847.png]]
- Добавление Dashboards 
Во вкладке Dashboards -> Import и добавляем те, что скачали ранее
- Настройка Alerts (Уведомлений)
- Добавление точек сообщений (Gmail, Telegram)
	Gmail
Зайти в Grafana docker exec -ti 0 
И отредактировать файл /etc/grafana/grafana.ini
ESC + /smtp
И редактируем на: 
[smtp]
enabled = true
host = smtp.mail.ru:465
user = toor321@mail.ru
#р the password contains # or ; you have to wrap it with triple quotes. Ex """#password;"""
password = ******************
;cert_file =
;key_file =
skip_verify = true
from_address = toor321@mail.ru
from_name = Grafana
#p identity in SMTP dialog (defaults to instance_name)
;ehlo_identity = dashboard.example.com
#p SMTP startTLS policy (defaults to 'OpportunisticStartTLS')
;startTLS_policy = NoStartTLS

Перезапускаем контейнер 

	 Telegram 
Получаем Bot Api Token. Заходим в телеграмм бота https://t.me/BotFather и пишем /newbot придумываем имя бота и username заканчивающийся на bot->Копируем APi     -> Заходим на созданного бота -> Заходим сюда https://t.me/username_to_id_bot и получаем свой id и также копируем в Grafana. 

**Отключить в Notification Settings Resolved Message, если не нужны**\
Должно выглядеть вот так: 
![[Pasted image 20230121150933.png]]

- Создание Rule
В Alrts Rules создаём New Alert Rule 
В метрикс выставляем что нужно:
![[Pasted image 20230121151154.png]]
В Rule Name пишем имя которое будет приходить в алерте, и которое будет указывать нам на проблему. Группу можно назвать как душа пожелает 
![[Pasted image 20230121151239.png]]

[[Кластер Greenplum]] [[Кластер postgresql]] [[Zabbix]]
