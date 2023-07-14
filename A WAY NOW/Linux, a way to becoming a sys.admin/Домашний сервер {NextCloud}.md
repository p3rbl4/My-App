Создаём домашний сервер, на примере файлового сервера NextCloud 
***Объяснение общей схемы всей работы сети сервера***
	***Что мы имеем?***
1. Доменное имя 2 уровня (к примеру) будет practice-host-dfsystems.ru
2. ВМ на vscale.io (на ней Nginx (80,443), OpenVPN server со своим публичным IP,)


# Схема работы
Клиент в браузере вводит доменное имя > запрос попадает на DNS сервер и тем самым получает IP адрес > Далее запрос отправляется на сервер vscale, где его встречает Nginx, который проксирует запрос на адрес 10.8.0.13 > А так как рядом с Nginx развёрнут OpenVPN сервер со своей сетью 10.8.0.0/8 > OpenVPN сервер запакует этот запрос клиенту, то есть нашему серверу дома, где его встречает OpenVPN client > Этот запрос дешифруется и отправляется на порт 5555 того же адреса 10.8.0.13 где будет крутиться файловый сервер > После идёт ответ клиенту по обратной цепочке
![[Pasted image 20230216131941.png]]
***Пошаговая инструкция***
Простая установка OpenVPN: https://www.youtube.com/watch?v=7VvWZIz1kB8&t=4s
c 27 минуты 
1. Первым делом настроил ubuntu на домашем сервере, поднял ssh, открыл 22 порт, ufw allow 22. А также 80, 443, 5555.  Также не забываем прбросить порты 443 и 5555 в настройках маршрутизатора
2. Связываем доменное имя с IP адресов ВМ где у нас OpenVPN сервер Nginx и прочее. В общем редирект машина. Делается это во вкладке домены в самом vscale. А на площадке где покупался домен, вписать DNS сервера от поставшица ВМ. 
3. Устанавливаем и настраиваем Nginx на ВМ. Создаём файл /etc/nginx/sites-available/[имя домена] и прописываем туда следующее
```bash
server {
    server_name practice-host-dfsystems.ru;

    listen 80;

    location / {
          proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            client_max_body_size 0;
            add_header Strict-Transport-Security "max-age=31536000"; includeSubD>
            add_header Referrer-Policy "same-origin";

            proxy_pass http://10.8.0.13:5555;
   }
}
```
В этом конфиге всё просто, 1 строка показывает какой домен будет слушать данная конфигурация, 2 строка какой порт. И дальше директива говорит, что все запросы которые будут приходить на этот домен, будут перенаправлять на адресс 10.8.0.13:5555 
4. Далее мы получаем сертификат Let's encrypt для домена 
sudo add-apt-repository ppa:certbot/certbot 
sudo apt install python3-certbot-nginx 
sudo certbot --nginx -d [DOMAIN_NAME]
После чего если файл конфигурации сервера не поправился, но довести его до такого состояния 
```bash
listen 443 ssl;
    ssl_сertificate /etc/letsencrypt/live/practice-host-dfsystems.online/fullch>
    ssl_certificate_key /etc/letsencrypt/live/practice-host-dfsystems.online/pr>
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

}
server {
    if ($host = practice-host-dfsystems.online) {
        return 301 https://$host$request_uri;
    }


    server_name practice-host-dfsystems.online;

    listen 80;
    return 404;



}
```

В итоге выглядит конфигурация Nginx вот так: 
```bash
server {
    server_name practice-host-dfsystems.online;

    location / {
          proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            client_max_body_size 0;
            add_header Strict-Transport-Security "max-age=31536000"; includeSubD>
            add_header Referrer-Policy "same-origin";

            proxy_pass http://10.8.0.13:5555;
   }


    listen 443 ssl;
    ssl_сertificate /etc/letsencrypt/live/practice-host-dfsystems.online/fullch>
    ssl_certificate_key /etc/letsencrypt/live/practice-host-dfsystems.online/pr>
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

}
server {
    if ($host = practice-host-dfsystems.online) {
        return 301 https://$host$request_uri;
    }


    server_name practice-host-dfsystems.online;

    listen 80;
    return 404;



}
```
Данная конфигурация слушает 443 и 80 порт. 80 порт служит для ответа 443 порта с ssl подключением. 443 порт перебрасывает на 5555 порт где крутиться сам сервис. 
5. Разворачиваем на сервере nextcloud при помощи docker-compose 
```bash 
version: '2'

volumes:
  nextcloud:
  db:

services:
  db:
    image: postgres:latest
    restart: always
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - db:/var/lib/pgsql/data
    environment:
      - POSTGRES_PASSWORD=33HjpGfy
      - POSTGRES_DATABASE=nextcloud
      - POSTGRES_USER=nextcloud

  app:
    image: nextcloud
    restart: always
    ports:
      - 5555:80
    links:
      - db
    volumes:
      - nextcloud:/var/www/html
    environment:
      - POSTGRES_PASSWORD=33HjpGfy
      - POSTGRES_DATABASE=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_HOST=db
```

***Заметки***: Не стоит использовать на таких серверах Wi-Fi ^^, работать будет, но ужасно. 

Полезная статья для настройки ssl сертификата в веб серверы: https://help.reg.ru/support/ssl-sertifikaty/3-etap-ustanovka-ssl-sertifikata/kak-nastroit-ssl-sertifikat-na-nginx?query=%d0%a3%d1%81%d1%82%d0%b0%d0%bd%d0%be%d0%b2%d0%ba%d0%b0%20SSL-%d1%81%d0%b5%d1%80%d1%82%d0%b8%d1%84%d0%b8%d0%ba%d0%b0%d1%82%d0%b0%20%d0%bd%d0%b0%20N

[[Linux]] [[Сети]] 