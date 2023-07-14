Любое резервное копирование (дамп) производится автоматически в виде скрипта, а сам алгоритм скрипта выглядит так: 
1. В определенное время **cron** запускает скрипт.
2. Скрипт монтирует сетевую папку бэкапов.
2.1 Если монтирование не удалось, то отсылается уведомление об ошибке и скрипт завершается.
3. Создаем архив из файлов папки **/opt/Share**. В названии архива указываем дату бэкапа, чтобы впоследствии можно было найти нужный.
4. По завершении архивации просматриваем файлы бэкапа и удаляем все старше месяца.

***1 Сценарий Bash скрипта для Backup файлового хранилища на NAS сервер***
Для начала задаются переменные самой собой их можно посмотреть здесь для удобства https://yodo.im/backup_

После идёт создание функций

**Функция для записи логов в красивом отфарматированном виде**
```bash
function toLog {

  local message=$1

  echo "[`date \"+%F %T\"`] ${message}" >> $BACKUP_LOG

}
```
В данном случае local message=1$ означает, что аргумент переданный в функцию будет записан в переменную message, которую можно использовать локально, внутри функции

**Функция проверки свободного места наNAS**. Если оно кончается, то эта информация попадет в лог-файл.
```bash
function checkUsedSpace {

if [[ `df -h|grep //$REMOTE_HOST/$REMOTE_BACKUP_DIR|awk '{print $5}'|sed 's/%//g'` -ge $USED_SPACE ]]; then

toLog "Used space on $REMOTE_HOST:$REMOTE_BACKUP_DIR higher then $USED_SPACE%."

toLog "END"

toLog ""

rm -f $BACKUP_LOCK

umount $BACKUP_DIR

exit

fi

}
```

**Функция для чистки папки бэкапов от старых файлов.**
```bash
function checkBackupDir {

  local backup_duration=$1

  find $BACKUP_DIR/$host/$backup_level -type f -mtime +$backup_duration -exec rm -rf {} \;

}
```
Команда  `find $BACKUP_DIR/$host/$backup_level -type f -mtime +$backup_duration -exec rm -rf` найдет в директории BACKUP_DIR/host/backup_level файлы старше чем $backup_duration и удалит их.

**Начинаем сам скрипт**
Для начала проверяем не идёт ли уже процесс бекапа, чтобы не было конфликта
```bash
while [ -e $BACKUP_LOCK ]

do

  sleep 1

done

  

touch $BACKUP_LOCK

toLog "START"
```
Проверяем существование файла из переменной **BACKUP_LOCK**. Если запущен, то ждем. Если не запущен, то создаем файл блокировки и идем дальше.

**Монтируем сетевую папку.** Если не смонтировалась, то выходим с ошибкой (естественно все логируется).
Если смонтировалась, то идем дальше
```bash
mount -t cifs //$REMOTE_HOST/$REMOTE_BACKUP_DIR $BACKUP_DIR -o username=$USER,password=$PASSWORD,rw > /dev/null 2>&1

if [ $? -ne 0 ]; then

   if [[ `df -h|grep //$REMOTE_HOST/$REMOTE_BACKUP_DIR|awk '{print $1 $6}'` == "//$REMOTE_HOST/$REMOTE_BACKUP_DIR$BACKUP_DIR" ]]; then

         checkUsedSpace

    else

         toLog "Problems with mounting directory"

         toLog "END"

         toLog ""
         rm -f $BACKUP_LOCK

         exit

      fi

fi
```
*2* условие проверят, что Это условие проверяет, если первые 6 символов возвращенного результата из команды _if [[ `df -h|grep //$REMOTE_HOST/$REMOTE_BACKUP_DIR|awk '{print $1 $6}'` == "//$REMOTE_HOST/$REMOTE_BACKUP_DIR$BACKUP_DIR" ]]; then
равны 

**Основное действие довольно незамысловатое**
Пихаем данные в архив и складываем на сетевую шару:
tar -c $BACKUP_SRC | pbzip2 -p4 -c > $BACKUP_DIR/$DT.tar.bz2
$BACKUP_SRC = /opt/share, то что бекапим

**И заканчиваем выполнение:**
```bash
toLog "END"

toLog ""

  

rm -f $BACKUP_LOCK

umount $BACKUP_DIR

exit
```


***2 сценарий Bash-скрипта для дампа БД mysql***
За основу берётся тот же скрипт 
Добавляются переменные для подключения к БД
_**DBHOST="localhost"**_

_**DBNAME="our_site"**_

_**DBUSER="site_user"**_

_**DBPASS="db_secure_pass"**_

А основная часть выглядит вот так
```bash
mysqldump -u $DBUSER -p$DBPASS -h $DBHOST $DBNAME > /tmp/our_site.sql

tar -c $BACKUP_SRC /tmp/our_site.sql | pbzip2 -p4 -c > $BACKUP_DIR/$DT.tar.bz2
```

***Следующая ситуация***
Будем бэкапить виртуалки. 
**1 Сценарий** Бэкапим все виртуалки. Виртуальные диски в виде файлов.
Скрипт выглядит следующим образом 
```bash
#Получаем список виртуалок 
VMLIST=`virsh list | grep '[[:digit:]]' | awk '{ print $2 }'`

#Script 

for VMNAME in $VMLIST

do
   virsh dumpxml $VMNAME > /tmp/$VMNAME.xml

   DISKLIST=`virsh domblklist $VMNAME | grep img | awk '{ print $2 }'`

  

   virsh suspend $VMNAME

   sleep 30

  

   tar -c $DISKLIST /tmp/$VMNAME.xml | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME.tar.bz2

  

   virsh resume $VMNAME

  

done

```
**VMLIST**
Из вывода утилиты virsh я извлекаю строки, в которых есть цифры (а это только записи о виртуалках), а после этого беру из второго столбца названия виртуальных машин.

*Скрипт*
Сначала он выполняет цикл по списку виртуальных машин, заданному в переменной $VMLIST. Для каждой машины он выполняет следующие действия:

1.  Создает XML-дамп виртуальной машины с помощью команды `virsh dumpxml $VMNAME" и сохраняет его в файл /tmp/$VMNAME.xml.
2.  Получает список виртуальных дисков, подключенных к данной виртуальной машине, с помощью команды "virsh domblklist $VMNAME | grep img | awk '{ print $2 }'" и сохраняет его в переменную $DISKLIST.
    
3.  Приостанавливает выполнение виртуальной машины с помощью команды "virsh suspend $VMNAME" и ждет 30 секунд, чтобы убедиться в том, что все изменения в памяти виртуальной машины сохранены на диске.
    
4.  Архивирует все диски виртуальной машины и XML-дамп в единый архив, используя команду "`tar -c $DISKLIST /tmp/$VMNAME.xml | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME.tar.bz2`". Файлы архивируются с помощью программы pbzip2, которая позволяет использовать несколько ядер процессора для ускорения процесса.
    
5.  Возобновляет выполнение виртуальной машины с помощью команды "virsh resume $VMNAME".
    

Таким образом, скрипт выполняет автоматическое создание резервных копий виртуальных машин, позволяя сохранить данные виртуальных машин в случае сбоя системы или других проблем.

***Сценарий в котором диски это не файлы, а LV***

Соответственно чтобы скопировать диск безболезненно надо использовать снапшоты.
```bash
#Получаем список виртуалок 
VMLIST=`virsh list | grep '[[:digit:]]' | awk '{ print $2 }'
#Script

for VMNAME in $VMLIST

do

   virsh dumpxml $VMNAME > /tmp/$VMNAME.xml

   cp /tmp/$VMNAME.xml $BACKUP_DIR/$VMNAME.xml

   virsh suspend $VMNAME

   sleep 30

  

   DISKLIST=`virsh domblklist $VMNAME | grep img | awk '{ print $2 }'`

for DISK in $DISKLIST

do

   LV=`lvdisplay $DISK | grep 'LV Name' | awk '{ print $3 }'`

   VG=`lvdisplay $DISK | grep 'VG Name' | awk '{ print $3 }'`
   
   SZ=`lvdisplay $DISK | grep 'Size' | awk '{ print $3 }'`

   lvcreate -L $SZ --snapshot --name $LV-test $DISK

done

  

   virsh resume $VMNAME

  

   tar -c $DISKLIST /tmp/$VMNAME.xml | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME.tar.bz2

  

for DISK in $DISKLIST

do

   LV=`lvdisplay $DISK | grep 'LV Name' | awk '{ print $3 }'`

   VG=`lvdisplay $DISK | grep 'VG Name' | awk '{ print $3 }'`

   dd if=$DISK-test conv=sync,noerror bs=64K | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME-$LV.bz2

   sleep 30

   lvremove $DISK-test

  done

done
```

Сначала он выполняет цикл по списку виртуальных машин, заданному в переменной $VMLIST. Для каждой машины он выполняет следующие действия:

1.  Создает XML-дамп виртуальной машины с помощью команды "`virsh dumpxml $VMNAME" и сохраняет его в файл /tmp/$VMNAME.xml.
    
2.  Копирует XML-дамп виртуальной машины в папку с резервными копиями ``$BACKUP_DIR с помощью команды "cp /tmp/$VMNAME.xml $BACKUP_DIR/$VMNAME.xml".
    
3.  Приостанавливает выполнение виртуальной машины с помощью команды "virsh suspend $VMNAME" и ждет 30 секунд, чтобы убедиться в том, что все изменения в памяти виртуальной машины сохранены на диске.
    
4.  Получает список виртуальных дисков, подключенных к данной виртуальной машине, с помощью команды "virsh domblklist $VMNAME | grep img | awk '{ print $2 }'" и сохраняет его в переменную $DISKLIST.
    
5.  Для каждого диска в списке $DISKLIST выполняет следующие действия:
    

a. Получает имя логического тома (LV) и группы томов (VG), на которых находится данный диск, с помощью команд "lvdisplay $DISK | grep 'LV Name' | awk '{ print $3 }'" и "lvdisplay $DISK | grep 'VG Name' | awk '{ print $3 }'".

b. Получает размер диска (SZ) с помощью команды "lvdisplay $DISK | grep 'Size' | awk '{ print $3 }'".

c. Создает снимок диска с помощью команды "lvcreate -L $SZ --snapshot --name $LV-test $DISK".

6.  Возобновляет выполнение виртуальной машины с помощью команды "virsh resume $VMNAME".
    
7.  Создает архив, содержащий все диски виртуальной машины и XML-дамп в едином файле, используя команду "`tar -c $DISKLIST /tmp/$VMNAME.xml | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME.tar.bz2". Файлы архивируются с помощью программы pbzip2, которая позволяет использовать несколько ядер процессора для ускорения процесса.
   `tar -c $DISKLIST /tmp/$VMNAME.xml` архивирует содержимое дисков (`$DISKLIST) и файла XML-описания виртуальной машины (/tmp/$VMNAME.xml).
   `pbzip2 -p4 -c` используется для сжатия архива с помощью алгоритма bzip2 с установкой параметра сжатия в 4.
   Результат сохраняется в файл с именем, содержащим дату и время создания архива, имя виртуальной машины и расширение ".tar.bz2" `($DT-$VMNAME.tar.bz2) в каталоге $BACKUP_DIR.
8. Далее выполяется ещё один цикл, казалось повторный, но он необходим чтобы для каждого созданного в предыдущем цикле снимки дисков, были скопированы в архив. Каждый снимок сохраняетс в отдельном файле, имя которого содержит имя виртуальной машины, имя тома, дату и время создания.
   Речь идёт про эту команду 
   `dd if=$DISK-test conv=sync,noerror bs=64K | pbzip2 -p4 -c > $BACKUP_DIR/$DT-$VMNAME-$LV.bz2
   >`dd` используется для копирования содержимого снимка диска ($DISK-test) и записи его в выходной поток.
   > `conv=sync,noerror` используется для обеспечения синхронизации данных и игнорирования ошибок при копировании.
9. После копирования данных в архив, снимки дисков удаляются.


[[Linux]] [[Bash]]