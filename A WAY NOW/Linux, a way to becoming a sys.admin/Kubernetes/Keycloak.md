# Keycloak - это 
*платформа для управления идентификацией и доступом (Identity and Access Management, IAM) с открытым исходным кодом. Она предоставляет централизованный механизм аутентификации, авторизации и управления пользователями, группами и клиентами, которые используют приложения в рамках вашей организации.

*Keycloak позволяет создавать и настраивать различные методы аутентификации, включая аутентификацию с помощью логина и пароля, OAuth 2.0, OpenID Connect и SAML. Он также предоставляет возможность настройки многофакторной аутентификации и управления сессиями пользователей.

*Keycloak также может использоваться для создания и управления API-интерфейсами, обеспечивая аутентификацию и авторизацию при вызове API.

*Использование Keycloak позволяет упростить и централизовать управление идентификацией и доступом, а также повысить безопасность и снизить риски, связанные с управлением учетными записями и доступом к приложениям внутри вашей организации.

# Deployment Keycloak с TLS/SSL сертификатом

Перед указанием сертификатов, для начала необходимо положить их в секрет
```bash
kubectl create secret tls auth-tls-secret --cert=path/to/fullchain.pem --key=path/to/key
```

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: keycloak
spec:
  selector:
    matchLabels:
      app: keycloak
  replicas: 1
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      securityContext:
        runAsUser: 0
      containers:
        - name: keycloak
          image: jboss/keycloak
          volumeMounts:
            - name: auth-tls-keycloak
              mountPath: /etc/x509/https
              readOnly: true
            - name: keycloak-pvc
              mountPath: /opt/jboss/keycloak/standalone/data
          ports:
            - containerPort: 8443
              protocol: TCP
              name: https
          env:
            - name: KEYCLOAK_USER
              value: admin
            - name: KEYCLOAK_PASSWORD
              value: admin
            - name: KC_HTTPS_CERTIFICATE_FILE
              value: "/etc/x509/https/tls.crt"
            - name: KC_HTTPS_CERTIFICATE_KEY_FILE
              value: "/etc/x509/https/tls.key"
            - name: KC_HOSTNAME
              value: practice-host.dfsystems.ru
      volumes:
        - name: auth-tls-keycloak
          secret:
            secretName: auth-tls-keycloak
        - name: keycloak-pvc
          persistentVolumeClaim:
            claimName: keycloak-pvc

---

apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: keycloak
spec:
  type: NodePort
  selector:
    app: keycloak
  ports:
    - name: https
      port: 443
      targetPort: 8443
      nodePort: 31233
```

# Настройка аутентифкации в Minio через openid-connect. 
Исходные данные: установлен MiniO в Kubernetes. 
***Инструкция***
Установка keycloak: 
PV, PVC
```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: keycloak-pv
  namespace: keycloak
spec:
  storageClassName: manual
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/data

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: keycloak-pvc
  namespace: keycloak
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
```
Keycloak 
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: keycloak
spec:
  selector:
    matchLabels:
      app: keycloak
  replicas: 1
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      securityContext:
        runAsUser: 0
      containers:
        - name: keycloak
          image: jboss/keycloak
          volumeMounts:
            - name: keycloak-pvc
              mountPath: /opt/jboss/keycloak/standalone/data
          ports:
            - name: http
              containerPort: 8080
            - name: https
              containerPort: 8443
          env:
            - name: KEYCLOAK_USER
              value: admin
            - name: KEYCLOAK_PASSWORD
              value: admin
      volumes:
        - name: keycloak-pvc
          persistentVolumeClaim:
            claimName: keycloak-pvc

---

apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: keycloak
spec:
  type: NodePort
  selector:
    app: keycloak
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: https
      port: 8443
      targetPort: 8443
```
login и pass: admin 

Настройка самой аутентификации.
1. Создали realm и клиента в нём Minio 
2. Настройка клиента
Изменить `Access Type` на `confidential`
Установить `Valid Redirect URIs`на `*`, развернуть `Advanced Settings` и установить `Access Token Lifespan` на `1 Hours`
Создать Mapper 
-   `Name` with any text
-   `Mapper Type` is `User Attribute`
-   `User Attribute` is `policy`
-   `Token Claim Name` is `policy`
-   `Claim JSON Type` is `string`
Далее необходимо создать пользователя
Был создал пользователь keycloak, дале во вкладке Attributes в key был добавлен policy, а в Value readwrite. 
3. Создание ConfigMap для MiniO 
Скорее всего он, не правильный и в данном примере ни на что не влияет. 
Но сделать можно его следующим образом. 
Создаём файл minio-config.yaml
```bash
credential:
  openID:
    enable: true
    issuer: "http://192.168.31.223:32131/auth/realms/minio"
    clientID: "minio"
    clientSecret: "6GXw1R4C5WvKFmSZUx07ZPaeZlyODE1S"
    scopes:
      - "openid"
    redirectURL: "http://192.168.31.223:31236/login"
    claimsNamespace: "keycloak"
    jwksURL: "http://192.168.31.223:32131/auth/realms/minio/protocol/openid-connect/certs"
    insecureSkipVerify: true
```
Далее создаём configmap опираясь на этот файл 
```bash
kubectl create configmap minio-config --from-file=minio-config.yaml
```
И добавляем в манифест деплоя Minio volumes и volumeMounts
```bash
volumes:
   - name: config
       configMap:
         name: minio-config
volumeMounts:
- name: config
      mountPath: /tmp/.minio/
      readOnly: false
```

4. Необходимо зайти в сам MiniO, от админских данных
Во вкладке Identify выбрать openid-connect и дальше настроить как показано на скрине данные для подключения. Client secret берётся из настроек клиента созданного в Keycloak, дальше разобраться не сложно.
```bash
Config URL   http://192.168.31.223:32131/auth/realms/minio/.well-known/openid-configuration
Client ID    minio
Client Secret   [secret]
Claim Name   policy
Redirect URI http://192.168.31.223:31236/oauth_callback
Role Policy  readwrite
```
После включить и перезагрузить. ***Аутентификация через Keycloak должна заработать!!!***


# Настройка аутентификации в Gitlab
Набросок конфига Gitlab 
```bash
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

[[Kubernetes]] [[MinIO (хранилище данных)]]  [[Git, Gitlab и Github]]