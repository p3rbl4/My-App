MinIO - это объектное хранилище, которое может использоваться в кластере Kubernetes для хранения файлов и объектов.

В кластере Kubernetes могут быть запущены различные приложения и сервисы, которые могут производить большой объем данных. Вместо того чтобы хранить эти данные внутри контейнеров, их можно сохранять во внешнее хранилище, такое как MinIO.

MinIO может использоваться в кластере Kubernetes в качестве хранилища для множества приложений, например, для хранения файлов, баз данных и других видов данных. В кластере Kubernetes, где может быть много узлов и микросервисов, данные можно распределить между узлами хранилища, обеспечивая тем самым доступность и отказоустойчивость данных.

Также, MinIO может использоваться для создания приватных облачных хранилищ. В этом случае, MinIO будет предоставлять доступ к объектам, сохраненным в облаке, только авторизованным пользователям.

В общем, использование MinIO в кластере Kubernetes позволяет легко масштабировать хранилище, обеспечивать доступность и отказоустойчивость данных, а также предоставлять возможность управления данными из любого места в мире.

# Деплой MinIO в качестве Standalone с 1 диском (лёгкая версия)

***В начале необходимо разобраться с тем, где будет хранить данные сам Minio.***
1. StorageClass , PV , PVC
Необходимо создать StorageClass, если нету стандартного 
```bash
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Retain
allowVolumeExpansion: true
mountOptions:
  - debug
volumeBindingMode: Immediate
```
После чего PV и PVC для Minio, где указывается только что созданный StorageClass
```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: minio-pv
  labels:
    type: local
spec:
  storageClassName: standard
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  # This name uniquely identifies the PVC. Will be used in deployment below.
  name: minio-pv-claim
  labels:
    app: minio-pv-claim
spec:
  # Read more about access modes here: http://kubernetes.io/docs/user-guide/persistent-volumes/#access-modes
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    # This is the request for storage. Should be available in the cluster.
    requests:
      storage: 2Gi
```
И уже сам Deployment ямлик вместе с сервисом 
```bash
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: minio
  name: minio # Change this value to match the namespace metadata.name
spec:
  volumes:
     - name: data
       persistentVolumeClaim:
         # Name of the PVC created earlier
         claimName: minio-pv-claim
  containers:
  - name: minio
    image: quay.io/minio/minio:latest
    command:
    - /bin/bash
    - -c
    args:
    - minio server /data --console-address :9090
    env:
   # Minio access key and secret key
    - name: MINIO_ACCESS_KEY
      value: "minio"
    - name: MINIO_SECRET_KEY
      value: "minio123"
        # Mount the volume into the pod
    volumeMounts:
    - name: data # must match the volume name, above
      mountPath: "/data"
  nodeSelector:
    kubernetes.io/hostname: kube1 # Specify a node label associated to the Worker Node on which you want to deploy the pod.

---

apiVersion: v1
kind: Service
metadata:
  name: minio-service
spec:
  type: NodePort
  ports:
    - port: 9090
      name: console
    - port: 9000
      name: s3
  selector:
    app: minio
```
После этих действий, можно будет зайти в веб интерфейс minio используя Ip-адресс ноды, где был развёрнут minio, то есть kube1, ну или это можно посмотреть при помощи команды kubectl get po [pod] -o wide, по порту который дал уже NodePort
Данные для входа указаны в переменных манифеста.

# Backup, резервное копирование Gitlab в MiniO
Для начала необходимо, чтобы у нас был ***mc*** (MiniO Client) , установить его можно по следующему мануалу https://min.io/docs/minio/linux/reference/minio-mc.html

После чего нам необходимо связать mc с самим MiniO делается это следующим образом
Если MiniO развёрнут в Kubernetes узнаем его **ip** с портом **9000** командой 
```bash
kubectl logs minio 
```

Далее устанавливаем config host 
```bash
./mc config host add myminio http://172.16.18.21:9000 minio minio123
```
minio и minio123 - стандартные имя пользователя и пароль 

Дальше можно создать *bucket* для Gitlab, командой:
```bash
./mc mb myminio/gitlab-backups
```

Далее уже из веб-интерфейса самого MiniO, во вкладке Acces Keys создаём новый Key, сохраняем данные и используем их в конфиге Gitlab 
1. **Как должен выглядеть конфиг /etc/gitlab/gitlab.rb на локальном сервере**
```bash
gitlab_rails['backup_upload_connection'] = {
   'provider' => 'AWS',
   'region' => 'eu-west-1',
   'aws_access_key_id' => 'CF8oT5Z03wq1ZOzl',
   'aws_secret_access_key' => '3aSAy3LLxe0nrMhmj5OkKKpRChakufvx',
   'endpoint' => 'http://192.168.31.223:32691',
   'path_style' => true
}
gitlab_rails['backup_upload_remote_directory'] = 'gitlab-backups'
```

access_key_id - тот что создали в MiniO
secret_access_key - тот что создали в MiniO
далее сам адресс MiniO с общедоступным портом 9000:32691
backup_upload_remote_directory - bucket который создали недавно gitlab-backups

Реконфигурируем Gitlab
```bash
gitlab-ctl reconfigure
```

Делаем тестовый backup 
```bash
gitlab-rake gitlab:backup:create
```

После завершения процесса бэкапа проверяем в Kubernetes через ранее установленную утилиту *mc* либо через веб интерфейс, наличие созданного бэкапа в хранилище 
```bash
mc ls myminio/gitlab-backups
```

2. Backup, когда Gitlab развёрнут непосредственно в самом Kubernetes (**с ручной сменой конфигураци в Gitlab**) Говно короче 
1. Omnibus Package 
Представим, что у нас упал кластер и перезагрузил все образы, Gitlab получается пустой и снова без конфигурации
>Заходим в под и меняем там конфигурацию как и в локальном Gitlab и применяем 
```bash
kubectl exec -ti [pod] -- /bin/sh
```
Бэкапы буду делаться через cronjob по расписанию с использованием образа kubectl, то есть просто буду передаваться команды в под где лежит Gitlab. Перед этим необходимо сделать clusterrolebinding, если под лежит в спец. неймспейсе, то нужно делать ещё role, но это не точно, здесь пример для default service account и для default namaspace 
>Создаём clusterrolebinding
```bash
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fabric8-rbac
subjects:
  - kind: ServiceAccount
    # Reference to upper's `metadata.name`
    name: default
    #         # Reference to upper's `metadata.namespace`
    namespace: default
roleRef:
   kind: ClusterRole
   name: cluster-admin
   apiGroup: rbac.authorization.k8s.io
```
>Создаём yaml файл, в котором описан процесс бэкапа, а именно передачи команд в под 
```bash
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gitlab-backup
spec:
  schedule: "*/2 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: gitlab
            image: bitnami/kubectl:latest
            command: ["/bin/sh", "-c", "kubectl exec [pod] -- gitlab-backup create"]
            env:
              - name: MINIO_ACCESS_KEY
                valueFrom:
                  configMapKeyRef:
                    name: gitlab-config
                    key: MINIO_ACCESS_KEY
              - name: MINIO_SECRET_KEY
                valueFrom:
                  configMapKeyRef:
                    name: gitlab-config
                    key: MINIO_SECRET_KEY
              - name: MINIO_ENDPOINT
                valueFrom:
                  configMapKeyRef:
                    name: gitlab-config
                    key: MINIO_ENDPOINT
              - name: MINIO_BUCKET
                valueFrom:
                  configMapKeyRef:
                    name: gitlab-config
                    key: MINIO_BUCKET
            volumeMounts:
            - name: gitlab-data
              mountPath: /mnt/data/gitlab
          restartPolicy: OnFailure
          volumes:
          - name: gitlab-data
            persistentVolumeClaim:
              claimName: gitlab-pvc
```
Время и наименование пода изменяем, имя пода лучше сделать сразу статическое при деплое. 
2. Helm 






[[Kubernetes]]  [[Git, Gitlab и Github]]