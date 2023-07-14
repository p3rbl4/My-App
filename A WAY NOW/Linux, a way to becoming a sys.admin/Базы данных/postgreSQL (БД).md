Машина centos 7 (2)
Установку производить с сайта https://www.postgresql.org/download/linux/redhat/
Лучше всего выключить firewalld, чтобы не было проблем, либо разрешить **ufw allow 5432/tcp**
зайди в бд можно командой ***sudo -i -u postgres***
в ней создаётся БД createdb name_db
Чтобы убить БД - dropdb name_db
Дальше переход в консоль **psql**

**При работе с БД не рекомендуется работать из под root пользователя**

***Изменение конфигов***
в файле **sudo nano /var/lib/pgsql/12/data/postgresql.conf** изменить ![[Pasted image 20221216223049.png]]
В строке listen_addresses можно поставить ip хоста 
в файле **sudo nano /var/lib/pgsql/12/data/pg_hba.conf** поменять METHOD на md5 там где он другой и добавить строки которых не хватает как на скрине 
![[Pasted image 20221216223601.png]]
***Подключение БД в DBeaver***
В настройках выбрать БД указать host и имя БД 
***Создание бекапа, резервной копии (Backup) для БД***
Делается это при помощи команды pg_dump подробнее про неё можно прочитать здесь https://selectel.ru/blog/postgresql-backup-tools/
При использовании программы может вылезти ряд ошибок, если вылезла ошибка с аутинфикацией, необходимо поменять peer на md5 
![[Pasted image 20221219133140.png]]

***Перенос postgres***
Выключил службу
Скопировал data_directory в отдельный каталог на новом диске
rsync -av /mnt/volume-nycl-01/pgsql /_mydata2_/post

Выдал права chown -R postgres:postgres /_mydata2/_post/pgsql/12/data

Переименовал на всякий старый PGDATA

mv /mnt/volume-nycl-01/pgsql/12/data /mnt/volume-nycl-01/pgsql/12/data.bak

Изменил data_directory в postgres.conf

data_directory = '/_mydata2_/post/pgsql/12/data'

В конфиге сервиса systemctl edit postgresql-12

Изменил переменную:

***[Service]
Environment=PGDATA=_mydata2_/post/pgsql/12/data***

Изменил PGDATA так же в файле /_usr/pgsql-12/bin/postgresql-12-check-db-dir_




[[Linux]]

