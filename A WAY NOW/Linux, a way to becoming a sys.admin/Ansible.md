Установку можно посмотреть на официальном сайте Ansible: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

*На примере основной машины и сервера на котором хочется производится развёртывание чего-либо*
https://www.youtube.com/watch?v=dQN2LHqhsVY
1. Устанавливается Ansible на основную машину
2. Создать на основе ssh-ключ через ssh-keygen 
3. На сервере создать пользователя ansible (useradd -m ansible) и создаём директорию .ssh, в которую заносим ключ ssh основной машины в файл authorized_keys. Разграничим права на файл authorized_keys, chown ansible:ansible и chmod 600
4. Для упрощения работы ansible на сервере в файле visudo в конце прописывается строка ansible ALL=(ALL:ALL) NOPASSWD: ALL
5. Для поддержки версионности сервисных настроек, создаётся репозиторий в Git, (для Github создать access tokens в разделе developers settings)
6. После того как настроен git и работа происходит в его директории, создаётся *INVENTORY-файл* где будут определенны хосты для которых, нужно выполнить разные playbook'и, файл выглядит следующим образом, где определяются настойки для подключения и группировки хостов
```bash
[group_test]
test ansible_host=Standby2

[group_test:vars]
ansible_user=ansible
ansible_port=22
```
7. Для упрощения жизни и не использования ключа -i, чтобы каждый раз указывать inventory файл и файл для вывода логов, создаётся файл ansible.cfg, где указывается какой файл является необходимым
```bash
[defaults]
inventory = hosts
log_path = ansible.log
```
8. Log-файл лучше добавить в исключения Git, чтобы он не пушился с остальной конфигурацией, в файл .gitconfig, который нужно создать, добавляется само название Log-файла

*Playbooks*

```yaml
- name: Install Docker
  gather_facts: No
  hosts: test
  vars:
    user_name: ansible
  tasks:
    - name: Install utils
      package:
        name: "{{ item }}"
        state: latest
      become: yes
      with_items:
        - yum-utils
        - lvm2
        - device-mapper-persistent-data
```
**gather_facts** - ansible собирает информацию о сервере к которой мы может обратиться по средством переменных, здесь она отключена
**"item"** - это синтаксис шаблона jnj2 и подставляет вместо себя перечисление в блоке **with_items**
**become** - разрешает выполнять с привелигероваными правами 

Полный playbook, для установки docker на centos
```yaml
- name: Install Docker
  gather_facts: No
  hosts: test
  vars:
    user_name: ansible
  tasks:
    - name: Install utils
      package:
        name: "{{ item }}"
        state: latest
      become: yes
      with_items:
        - yum-utils
        - lvm2
        - device-mapper-persistent-data

    - name: Add Docker Repo
      get_url:
        url: https://download.docker.com/linux/centos/docker-ce.repo
        dest: /etc/yum.repos.d/docker-ce.repo
      become: yes

    - name: Install Docker
      package:
        name: docker-ce
        state: latest
      become: yes

    - name: Start Docker Service
      service:
        name: docker
        state: started
        enabled: yes
      become: yes

    - name: Add User ansible to Docker Group
      user:
        name: ansible
        groups: docker
        append: yes
      become: yes
```

[[Linux]]
#ansible #git 