***Расписывание по шагам >***
Установокой ISO образа любом сможет 

1. Проверить наличие соединения, если по кабелю, то должен быть сразу, если по WiFi, то следовать этому https://archlinux.org.ru/forum/topic/20666/
2. Синхронизация часов командой timedatectl set-ntp true и проверить timedatectl status
3. Монтирование диска, необходимо создать 3 раздела - 1 EFI-раздел 550МБ, 2-Файл подкачки 2гб, а 3 раздел - всё остальное пространство. 
   Делается это командами, fdisk /dev/sba  (или любой другой диск). > g
   1 раздел - n > 1 > Default > +550M
   2 раздел - n > 2 > Default > +2G
   3 раздел - n > 3 > Default > Default
   ***Меняем тип разделов***
   1 раздел - t > 1 > 1 (EFI System)
   2 раздел - t > 2 > 19 (Linux SWAP)
   **Сохраняемся**
   w (Записать)
   **Создание файловых система на резелах**
   EFI System - mkfs.fat -F32 /dev/sda1
   SWAP - mkswap /dev/sda2 > swapon /dev/sda2
   Основной раздел mkfs.ext4 /dev/sda3 > Сразу монтируем > mount /dev/sda3 /mnt
4. Установка базовых пакетов в /mnt (pacstrap) > pacstrap /mnt base linux linux-firmware 
   **Создание таблиц файловых систем**
   genfstab -U /mnt >> /mnt/etc/fstab
5. Вход в установленную базу > arch-chroot /mnt
6. Настройка региона и времени > ln -sf /usr/share/zoneinfo/Europe/Moscow 
Синхронизация времени системных часов и ОС > hwclock --systohc
7. Установка редактора pacman -S nano и редактируем файл локализации /etc/locale.gen расскоментируем 2 строки en_US.UTF-8 UTF-8 и ru_RU.UTF-8 UTF-8 дальше команда > locale-gen 
8. Hostname, hosts, пользователь и пароли 
   nano /etc/hostname придумывает имя ПК, nano /etc/hosts привёдм файл в вид 
   127.0.0.1    localhost
   ::1               localhost
   127.0.1.1    [имяпк].localdomain    [имяпк]
   Создаём пароль для Root > passwd
   Создаём пользователя user и также пароль для пользователя 
   Добавляем пользователяя в группы *usermod -aG wheel,audio,video,storage*
   Выдаём привилегия sudo, для начало устанавливаем pacman -S sudo 
   Переходим в suduers file и расскоментируем Wheel > EDITOR=nano visudo
9. Установка networkmanager > pacman -S networkmanager и включить в автозагрузку systemctl enable NetworkManager 
10. Установка refind и gdisk > pacman -S refind gdisk > refind-install 
Редактируем файл /boot/efi/EFI/BOOT/refind.conf изменить строку options "root=PARTUUID=**************** rw add memmap"***  Изменить, то что после PARTUUID и до rw на раздел диска где основная часть /dev/sda3

[[Linux]]