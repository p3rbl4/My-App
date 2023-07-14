**RPM - утилита управления пакетами в Red Hat системах**
Rpm2cpio - разбор пакета на двоичные файлы  - переделывает файлы c расширением .rpm в cpio, который пригоден почти для всех Unix систем 

rpm --query --all   -  выводит список всех установленных пакетов 

**YUM - программа работы с пакетами программ в Red Hat - системах**
yumdownloader - скачивание пакетов без установки
/etc/yum.repos.d/ - перечень репозиториев

*Чтобы добавить собственный репозиторий, необходимо выполнить следующее*
Создать файл с новым репозиторием 
```bash
sudo vi /etc/yum.repos.d/myrepo.repo
```
Добавить в файл следующую конфигурацию 
```bash
[repository_name]
name=My Repository
baseurl=http://example.com/repo/
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-MyRepo
```
gpgcheck можно поставить в 0, тогда ключ проверяться не будет.

Обновите кэш репозиториев YUM, чтобы новый репозиторий был добавлен
```bash
sudo yum makecache
```

Чтобы удалить необходимо выполнить удаление файла и очистки кеша
```bash
sudo rm /etc/yum.repos.d/myrepo.repo
sudo yum clean all
```


[[Linux]]
#Управлениепакетами #Пакеты 