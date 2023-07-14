Настроить конфигурацию под почту с которой будут отправляться 
![[Pasted image 20221215122539.png]]
```bash
mailhub=smtp.mail.ru:587
AuthUser=toor321@mail.ru
AuthPass=X2tgtJd5u4GdiqhyxRNi
UseSTARTTLS=YES
FromLineOverride=YES
# Where will the mail seem to come from?
rewriteDomain=mail.ru
```
Также править файл /etc/ssmtp/revaliases
```bash
root:toor321@mail.ru:smtp.mail.ru:587
```

Почта отправляется с /usr/sbin/ssmtp или просто с mail
Пример скрипта написанный для отправки почты 
![[Pasted image 20221215122654.png]]

Отправка email при помощи mailx [centos 7]
Для того чтобы отправить сообщения нужно настроить файл /etc/mail.rc следующим образом 
![[Pasted image 20221216132719.png]]
```bash
account mail {
        set smtp=smtps://smtp.mail.ru:465
        set smtp-auth=login
        set smtp-auth-user=toor321@mail.ru
        set smtp-auth-password=BQ2amwFc2rwJePmWHpVN
        set ssl-verify=ignore
        set nss-config-dir=/etc/ssl/certs
}
```

Пароль для mail почты задаётся в настройка паролей для сторонних приложений nss-config-dir задаётся сертификатами cert8.db и key3.db, необходимо их найти в системе и перенаправить в папку /etc/ssl/certs и указать это в конфиге
Дальше почту отправлять необходимо следуюшей командой:
mailx -v -A mail -s "sdff" -r toor321@mail.ru heagekvat@gmail.com

[[Linux]]
