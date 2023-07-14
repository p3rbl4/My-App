***Git*** - система контроля версий, локальное хранилище репозиториев.
Установка git на centos 7 - https://invs.ru/support/chastie-voprosy/kak-ustanovit-git-na-centos-7/
Как изменить пароль для пользователя - https://sidmid.ru/gitlab-reset-root-pass/
![[Pasted image 20230127140917.png]]
***Для того, чтобы инициализировать, репозиторий с GitHub на локальном ПК, необходимо:***

***Gitlab***
Установка - https://www.dmosk.ru/miniinstruktions.php?mini=gitlab-centos
Gitlab runner установка - https://docs.gitlab.com/runner/install/linux-manually.html
![[Pasted image 20230127171843.png]]
**Gitlab-ce Centos 7** - https://about.gitlab.com/install/#centos-7
https://www.dmosk.ru/miniinstruktions.php?mini=gitlab-centos

# Установка и настройка Локального Gitlab-сервера 
- Необходимо установить компоненты 
yum install policycoreutils openssh-server
- Установка репозитория 
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash
- Устанавливаем сам Gitlab
yum install gitlab-ce
- В конфиге /etc/gitlab/gitlab.rb изменить external_url на собственный зарегестрированный домен
- В этом же конфиге параметр registry_external_url изменить на тот что нужен, либо тот же что у гитлаба либо адрес реестра 
	Если есть желание работать по http с gitalb (container) registry https://sysadmintalks.ru/insecure-gitlab-registry/
- Применить настройкаи 
gitlab-ctl reconfigure
- Не забывать пробросить порт в настройках роутера для доступа к веб-морде.
- Создать проект (репку) в веб морде 
- Добавить ssh-ключ Kubernetes в настройки Gitlab
Полезные ссылки для установки Gitlab: https://daffin.ru/devops/docker/gitlab_registry/

# Работа с допустом по портам
 ***https://russianblogs.com/article/519199564/  Настройка доступа по домену, а точнее по ПОРТАМ*** 
	 Замечание: Не трогай nginx после применения настроек, ты сломаешь сокет, решением этого будет смена порта ещё раз
Чтобы доступ к репозиторию был по изменённому порту необходим указывать порт в external_url /etc/gitlab.rb и в /opt/gitlab/embedded/service/gitlab-rails/config/gitlab.yml
***Полезная ссылка для доступа по другому порту ssh:*** https://stackoverflow.com/questions/18517189/gitlab-with-non-standard-ssh-port-on-vm-with-iptable-forwarding

# Gitlab deployment Kubernetes с TLS/SSL указанием

PV и PVC
```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: gitlab-pv
spec:
  storageClassName: gitlab
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data/gitlab"

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: gitlab-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gitlab
  resources:
    requests:
      storage: 7Gi
  volumeName: gitlab-pv
```

Перед указанием сертификатов, для начала необходимо положить их в секрет
```bash
kubectl create secret tls gitlab-tls-secret --cert=path/to/cert --key=path/to/key
```

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gitlab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gitlab
  template:
    metadata:
      labels:
        app: gitlab
    spec:
      volumes:
      - name: gitlab-tls-secret
        secret:
          secretName: gitlab-tls-secret
      - name: gitlab-pvc
        persistentVolumeClaim:
          claimName: gitlab-pvc
      containers:
      - name: gitlab
        image: gitlab/gitlab-ce:latest
        env:
        - name: GITLAB_OMNIBUS_CONFIG
          value: |
            external_url 'https://practice-host.dfsystems.ru'
            nginx['ssl_certificate'] = "/etc/gitlab/ssl/tls.crt"
            nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/tls.key"
        ports:
        - containerPort: 443
          name: https
          protocol: TCP
        volumeMounts:
        - name: gitlab-tls-secret
          mountPath: /etc/gitlab/ssl
          readOnly: true
        - name: gitlab-pvc
          mountPath: /mnt/data/gitlab
      nodeSelector:
        kubernetes.io/hostname: kube1

---

apiVersion: v1
kind: Service
metadata:
  name: gitlab
spec:
  type: NodePort
  selector:
    app: gitlab
  ports:
  - name: https
    port: 443
    targetPort: 443
    nodePort: 30443
    protocol: TCP
  - name: ssh
    port: 22
    targetPort: 22
```
ConfigMap, в котором указана конфигурация для backup в minio, настройки аутентификации через Keycloak и основые настройки с указанием tls сертификатов
```bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: gitlab-config
data:
 gitlab.rb: |
  external_url 'https://practice-host.dfsystems.ru'
  nginx['ssl_certificate'] = "/etc/gitlab/ssl/tls.crt"
  nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/tls.key"
  gitlab_rails['backup_upload_connection'] = {
     'provider' => 'AWS',
     'region' => 'eu-west-1',
     'aws_access_key_id' => 'CF8oT5Z03wq1ZOzl',
     'aws_secret_access_key' => '3aSAy3LLxe0nrMhmj5OkKKpRChakufvx',
     'endpoint' => 'http://192.168.31.223:32691',
     'path_style' => true
  }
  gitlab_rails['backup_upload_remote_directory'] = 'gitlab-backups'
  gitlab_rails['omniauth_enabled'] = true
  gitlab_rails['omniauth_allow_single_sign_on'] = ['keycloak', 'saml', 'openid_connect']
  gitlab_rails['omniauth_block_auto_created_users'] = true
  gitlab_rails['omniauth_auto_link_ldap_user'] = true
  gitlab_rails['omniauth_providers'] = [
    {
      name: 'openid_connect',
      label: 'keycloak',
      args: {
        name: 'openid_connect',
        scope: ['openid', 'profile', 'email'],
        response_type: 'code',
        issuer: 'https://practice-host.dfsystems.ru:31233/auth/realms/gitlab',
        client_auth_method: 'query',
        discovery: true,
        uid_field: 'gitlab',
        pkce: true,
        client_options: {
          identifier: 'gitlab',
          secret: 'wRE3LfKH9MvVspUCWxI33Uk2BPoLt7rk',
          redirect_uri: 'https://practice-host.dfsystems.ru:30443/users/auth/openid_connect/callback'
        },
      }
    }
  ]
```
[[Kubernetes]] [[Keycloak]] [[MinIO (хранилище данных)]]
