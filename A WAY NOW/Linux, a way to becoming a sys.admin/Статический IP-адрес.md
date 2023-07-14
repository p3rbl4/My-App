Чтобы поставить статический IP-адрес на сервере, необходимо выполнить ряд действий, а именно. 
1. Создать файл /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg и прописать туда network: {config: disabled}
2. Изменить файл конфигурации netplan в /etc/netplan/00-installer.yaml и выглядить он должен следующим образом 
3. Перезагрузить службу systemd-networkd
![[Pasted image 20221220154347.png]]
Статический IP - адресс на Centos настраивается в файле /etc/sysconfig/network-scripts/ifcfg следующим образом: 
![[Pasted image 20230123134146.png]]

[[Linux]]