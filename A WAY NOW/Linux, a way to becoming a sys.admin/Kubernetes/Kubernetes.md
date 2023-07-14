# Краткий обзор[](https://kubernetes.io/ru/docs/concepts/#%D0%BA%D1%80%D0%B0%D1%82%D0%BA%D0%B8%D0%B9-%D0%BE%D0%B1%D0%B7%D0%BE%D1%80)
Kubernetes — это портативная расширяемая платформа с открытым исходным кодом для управления контейнеризованными рабочими нагрузками и сервисами, которая облегчает как декларативную настройку, так и автоматизацию. У платформы есть большая, быстро растущая экосистема. Сервисы, поддержка и инструменты Kubernetes широко доступны.

Чтобы работать с Kubernetes, вы используете _объекты API Kubernetes_ для описания _желаемого состояния вашего кластера_: какие приложения или другие рабочие нагрузки вы хотите запустить, какие образы контейнеров они используют, количество реплик, какие сетевые и дисковые ресурсы вы хотите использовать и сделать доступными и многое другое. Вы устанавливаете желаемое состояние, создавая объекты с помощью API Kubernetes, обычно через интерфейс командной строки `kubectl`. Вы также можете напрямую использовать API Kubernetes для взаимодействия с кластером и установки или изменения желаемого состояния.

После того, как вы установили желаемое состояние, _Плоскость управления Kubernetes_ заставляет текущее состояние кластера соответствовать желаемому состоянию с помощью генератора событий жизненного цикла подов ([Pod Lifecycle Event Generator, PLEG](https://github.com/kubernetes/community/blob/master/contributors/design-proposals/node/pod-lifecycle-event-generator.md)). Для этого Kubernetes автоматически выполняет множество задач, таких как запуск или перезапуск контейнеров, масштабирование количества реплик данного приложения и многое другое. Плоскость управления Kubernetes состоит из набора процессов, запущенных в вашем кластере. ***Kubernetes - автоматически распределяет нагрузку между всеми воркерами, так что прямой связи к ним иметь не нужно.***

-   **Мастер Kubernetes** — это коллекция из трех процессов, которые выполняются на одном узле в вашем кластере, который обозначен как главный узел. Это процессы: [kube-apiserver](https://kubernetes.io/docs/admin/kube-apiserver/), [kube-controller-manager](https://kubernetes.io/docs/admin/kube-controller-manager/) и [kube-scheduler](https://kubernetes.io/docs/admin/kube-scheduler/).
-   Каждый отдельный неосновной узел в вашем кластере выполняет два процесса:
  -   **[kubelet](https://kubernetes.io/docs/admin/kubelet/)**, который взаимодействует с мастером Kubernetes.
  -   **[kube-proxy](https://kubernetes.io/docs/admin/kube-proxy/)**, сетевой прокси, который обрабатывает сетевые сервисы Kubernetes на каждом узле.
![[Pasted image 20230123184005.png]]

**Объяснение что такое Kubernetes:** https://www.youtube.com/watch?v=6HIXuufbdtk

# Control plane состоит из компонентов:
-   kube-apiserver - предоставляет API кубера
-   etcd - распределенное key-value хранилище для всех данных кластера. Необязательно располагается внутри мастера, может стоять как отдельный кластер
-   kube-scheduler - планирует размещение подов на узлах кластера
-   kube-controller-manager - запускает контроллеры
-   kubelet - сервис или агент, который контролирует запуск основных компонентов (контейнеров) кластер
https://habr.com/ru/post/589415/

# Про различиные виды сервисов (services) (NodePort, Loadbalancer, ClusterIP, Ingress)

***Что такое Services?*** - это объект, который позволяет вашим подам или деплойментам общаться между собой или с внешним миром. Service устанавливает правило маршрутизации для входящего трафика, направляя его к конкретным подам. Это означает, что вы можете выделить один IP-адрес для вашего Service и обращаться к нему, не заботясь о том, какие конкретные поды или деплойменты в данный момент обслуживают вашу нагрузку. Это помогает вам сделать ваш кластер более устойчивым и независимым от конкретных нод.

https://habr.com/ru/company/southbridge/blog/358824/
Существует 4 вида Сервисов и вот для чего нужен каждый: 
ClusterIP - IP только внутри кластера 
NodePort - Определённый порт на всех воркер нодах 
ExternalName - DNS CNAME Record 
LoadBalancer - только в Cloud Clusters (AWS, GCP, Azure)
![[Pasted image 20230216173421.png]]
***Load Balancer***
Как правило он используется для облачных развёртыванией, но есть и решение для настольных моментов, так называемым Bare Metal. Load Balancer на Barel Metal не будет работать, если его просто поставишь и запустишь. Для этого нужен специальный App, а именно Metal LB
***Установка Load Balancer (MetalLB)***
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
И создание yaml файла для определения IP external ip -
```bash
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default
  namespace: metallb-system
spec:
  addresses:
  - 192.168.31.100-192.168.31.110
  autoAssign: true
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - default
```

***Что такое Ingress Controller?***
https://www.youtube.com/watch?v=ThP-OEjpDZk
***Ingress Controler***, как полицейский, к нему отправляют трафик, а он уже при заранее созданых ***Ingress Rules*** решает куда именно отправить трафик. 
Есть множество Ingress Controllers (https://docs.google.com/spreadsheets/d/191WWNpjJ2za6-nbG4ZoUMXMpUK8KlCIosvQB0f-oq3k/edit#gid=907731238) сейчас использую Contour - устанавливается одной командой 
	kubectl apply -f https://projectcontour.io/quickstart/contour.yaml\

# Что такое Labels
Labels (метки) в Kubernetes - это пары ключ-значение, которые вы можете присвоить ресурсам Kubernetes, таким как Pod, Service, Deployment, и другим. Они предназначены для организации и классификации ваших ресурсов Kubernetes и предоставляют механизм для группировки ресурсов, связанных между собой.

Как правило, метки используются для присвоения семантического значения объекту, например, для указания версии приложения или окружения, в котором оно запущено. Метки также могут использоваться для выбора объектов, которые соответствуют определенным критериям при выполнении операций, таких как создание сервисов или развертывание приложений.

Одним из примеров использования меток может быть группировка Pod-ов в соответствии с приложениями, которые они поддерживают. Например, если у вас есть несколько приложений, работающих на кластере Kubernetes, вы можете присвоить каждому приложению метку, например, "app: myapp", и использовать эту метку для выбора всех Pod-ов, которые поддерживают данное приложение.

Метки также могут использоваться для выбора объектов, которые соответствуют определенным критериям. Например, если вы хотите назначить LoadBalancer только для Pod-ов, работающих в определенной зоне доступности, вы можете использовать метки для выбора этих Pod-ов.

В целом, метки в Kubernetes обеспечивают мощный механизм для организации и управления вашими приложениями в Kubernetes, облегчая управление и автоматизацию работы с ресурсами в кластере.

# Работа с командой kubectl
https://kubernetes.io/ru/docs/reference/kubectl/cheatsheet/

# Развёртывание кластера с 1 Master и 2 Worker's
Следовать официальной документации: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/
Источники:
https://www.youtube.com/watch?v=XfWE7NqgbLE&t=326s
https://www.youtube.com/watch?v=8W23gOff894

По шагам: 
- Для мастер ноды необходимо 4096 мб ОЗУ и 2 Ядра на воркерах можно по стандарту 
- Первым делом стандартная настройка Centos и добавление всех машин в кластере в файл /etc/hosts
- Создать и обменяться со всеми нодами ключами ssh
- Отключаем SWAP 
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
- Установка среды выполнения контейнеров (containerd)
	https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd
	https://github.com/containerd/containerd/blob/main/docs/getting-started.md
wget https://github.com/containerd/containerd/releases/download/v1.6.15/containerd-1.6.15-linux-amd64.tar.gz
tar Cxzvf /usr/local containerd-1.6.15-linux-amd64.tar.gz
	Скачиваем containerd.service
wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
mv containerd.service /usr/lib/systemd/system/
systemctl daemon-reload
systemctl enable --now containerd
systemctl status containerd
	Установка runc
wget https://github.com/opencontainers/runc/releases/download/v1.1.4/runc.amd64
install -m 755 runc.amd64 /usr/local/sbin/runc
	Установка cni-plugins 
wget https://github.com/containernetworking/plugins/releases/download/v1.2.0/cni-plugins-linux-amd64-v1.2.0.tgzwget https://github.com/containernetworking/plugins/releases/download/v1.2.0/cni-plugins-linux-amd64-v1.2.0.tgz
mkdir -p /opt/cni/bin
tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.2.0.tgz
	Создаём дефолтный конфиг для Containerd 
mkdir /etc/containerd
containerd config default > /etc/containerd/config.toml
	Настройка systemd драйвера cgroup
Редактируем кфг /etc/containerd/config.toml
Строчку SystemdCgroup = true, в 
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
systemctl restart containerd
- Переадрессация IPV4 и разрешение iptables видеть мостовой трафик
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
	Убедиться что br_netfilter и overlay загружены 
lsmod | grep br_netfilter
lsmod | grep overlay

sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward
- Установка kubeadm, kubelet и kubectl 
```bash
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

sudo systemctl enable --now kubelet
```
	Изменяем конфиг cgroup в kubelet 
kubectl edit cm kubelet-config -n kube-system
cgroupDriver: systemd
- Инициализация проводится только на мастере 
	Во время инициализации и присоединения воркеров к мастеру kubelet должен быть отключён 
Делается от root:
kubeadm init
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
- Присоединение воркеров к мастеру
mkdir -p $HOME/.kube
	Через ssh клиенты (bitvise), а именно SFTP окно, перекинуть файл config всё с того же мастера в папки $HOME/.kube на воркерах
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
	На мастере создаём token
kubeadm token create --print-join-command
	И уже присодиняемся с воркеров 
kubeadm join 192.168.31.222:6443 --token iuipu4.zw89n83b5m7uzr5a --discovery-token-ca-cert-hash sha256:6b609836721f99ee8f4aedfef0640a3690d99d4185dc8e8b6ff43538cb2f2bcd
- Команды для проверки node и кластера в целом 
kubectl get nodes
kubectl -n kube-system get all
kubectl cluster-info
kubectl get pods -A

# Установка и настройка Gitlab-runner для Kubernetes
https://cloud.yandex.ru/docs/managed-kubernetes/tutorials/gitlab-containers#create-gitlab
**Для и установки и регестрации gitlab-runner использовался helm chart**
- Установка helm 
wget https://get.helm.sh/helm-v3.11.0-linux-amd64.tar.gz
tar -zxvf helm-v3.11.0-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/
- Добавил репозиторий gitlab
helm repo add gitlab https://charts.gitlab.cn
- Содал файл values.yaml и добавил туда конфиг для развёртывания gitlab-runner в поде
```bash
---
imagePullPolicy: IfNotPresent
gitlabUrl: http://192.168.31.226/
runnerRegistrationToken: "GR1348941GChdd5ScarRe52EWqcQp"
terminationGracePeriodSeconds: 3600
concurrent: 10
checkInterval: 30
sessionServer:
 enabled: false
rbac:
  create: true
  clusterWideAccess: true
  podSecurityPolicy:
    enabled: false
    resourceNames:
      - gitlab-runner
runners:
  config: |
    [[runners]]
      [runners.kubernetes]
        namespace = "gitlab-runner"
        image = "ubuntu:20.04"
        privileged = true
```
gitlab-url и runnerRegistrationToken меняются в зависимости от своего гитлаба
Либо же сделать ***helm show values gitlab/gitlab-runner > [конфиг файл для раннера]*** и уже в нём изменить стандартные параметры и добавить **tags**
 - Установка и регистрация runner'a
kubectl create ns gitlab-runner
helm install --namespace gitlab-runner gitlab-runner -f values.yaml gitlab/gitlab-runner
- Проверяем под
kubectl get pods -A
Должен быть в статусе `running`
- Выдача прав для пода 
kubectl create clusterrolebinding --clusterrole=cluster-admin -n [namespace] --serviceaccount=[namespace]:default [pod-runner]

В веб-морде гитлаба проверить состояние только что подключённого раннера.

# Установка Gitlab Agent для работы с Kubernetes

В репозитории создать директорию ***.gitlab/agents/[имя_агента]***
Далее во вкладке infrastracture выбрать connect Kubernetes Cluster и выбрать только что созданного агента. После чего установить gitlab-agent при помощи данной ссылки, так как указанный репозиторий helm не добавляется (https://gitlab.com/gitlab-org/charts/gitlab-agent) 
При установке set config kas, добавить порт на котором держится сам gitlab.

# Доступ к частному реестру образов (container registry)

***Containerd***
На примере Gitlab registry (http). Для каждой ноды кластера kubernetes сделать следующие действия:
1. В файле /etc/containerd/config.toml добавить данные строчки 
```
[plugins."io.containerd.grpc.v1.cri".registry]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
          endpoint = ["https://registry-1.docker.io"]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."practice-host.dfsystems.ru:5005"]
          endpoint = ["http://practice-host.dfsystems.ru:5005"]
        [plugins."io.containerd.grpc.v1.cri".registry.configs]
          [plugins."io.containerd.grpc.v1.cri".registry.configs."practice-host.dfsystems.ru:5005".tls]
            insecure_skip_verify = true
```
 2. Перезагрузить сервис и установить в качестве исполнителя 
 crictl config runtime-endpoint /run/containerd/containerd.sock после чего можно пулить образы командой **crictl pull --creds "username:password" [путь к образу]**
 
 ***Docker***
 Добавить в файл /etc/docker/daemon.json следующее 
 ```
 {
  "insecure-registries" : ["practice-host.dfsystems.ru:5005"]
}
```
И перезагрузить 

**Далее**
Необходимо создать секрет с данным для аутентификации следующим образом 
```
kubectl create secret docker-registry -n runner regcred --docker-server=practice-host.dfsystems.ru:5005 --docker-username=Roman --docker-password=33HjpGfy --docker-email=toor321@mai.ru
```
По идее надо, чтобы был секрет в одном неймспейсе с самим деплоем. 

# Развёртывание приложения в kubernetes при помощи CI pipeline (postgresql)

***Что такое ConfigMap?*** - это объект, который хранит конфигурационные данные, которые можно использовать в вашем приложении. Например, это может быть адрес сервера, логин и пароль или любые другие настройки, которые ваше приложение может использовать. Вы можете создать ConfigMap в yaml файле или программно с помощью API клиента Kubernetes, а затем использовать его в своем манифесте для деплоя приложения. Таким образом, вы можете отделить конфигурационные данные от самого приложения и легко менять их без необходимости передеплоя приложения
Установка: https://adamtheautomator.com/postgres-to-kubernetes/
https://webhamster.ru/mytetrashare/index/mtb339/153754015478w0utzf29

***Развёртывание*** можно применять как при использовании CI/CD пайплайнов так и на прямую из консоли. Главное отличие, что секрет должен находится в неймспейсе где будет развёрнуто приложение. Если при использовании пайплайна, то оно будет развёрнуто там где gitlab-runner.

По шагам:
1. Создание PV и PVC
Они должны находится в default неймспейс, чтобы их было видно системе. Это необходимо указывать. Пример создания PV и PVC
```bash
kind: PersistentVolume
apiVersion: v1
metadata:
  name: postgres-pv-volume
  namespace: default
  labels:
    type: local
    app: postgresql-12
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  hostPath:
    path: "/mnt/data"

---

kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: postgres-pv-claim
  namespace: default
  labels:
    app: postgresql-12
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```
2. Развёртывание ConfigMap сам Deployment и Service
Пример развёртывания при взятии image (образа) с реестра образов

```bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  labels:
    app: postgresql-12
data:
  POSTGRES_DB: postgres
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgresql-12
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgresql-12
  template:
    metadata:
      labels:
        app: postgresql-12
    spec:
      containers:
      - name: postgresql-12
        image: practice-host.dfsystems.ru:5005/syktyvkar/dopustim
        imagePullPolicy: IfNotPresent
        ports:
          - containerPort: 5432
        envFrom:
          - configMapRef:
              name: postgres-config
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/pgsql/12/data
      restartPolicy: Always
      imagePullSecrets:
      - name: regcred
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pv-claim
        
---

apiVersion: v1
kind: Service
metadata:
  name: postgres-nodeport
  labels:
    app: postgresql-12
spec:
  type: NodePort
  ports:
   - name: postgresql-12
     port: 5432
     targetPort: 5432
  selector:
   app: postgresql-12
```
если image берётся с Docker Hub, то дальше всё просто:
вместо `image: practice-host.dfsystems.ru:5005/syktyvkar/dopustim` необходимо прописать `image: [название образа]`
3. Проверит работаспособность через kubectl get po -A. kubectl get logs или describe

# Что такое PersistentVolume (PV) и PersistentVolumeClaim (PVC)
Когда мы работаем с контейнерами, состояние у контейнеров **stateless**, что означает когда мы перезапускаем контейнер, наши какие-то изменения все стираются. Для того чтобы сохранить состояние контейнера используется примонтированный диск PV и есть это решение.

PersistentVolume (PV) и PersistentVolumeClaim (PVC) в Kubernetes - это способы управления хранилищем (например, жестким диском, файловой системой, NFS) в кластере.

PV - это объект, который представляет собой блок дискового пространства, который может быть назначен одному или нескольким подам.

PVC - это объект, который запрашивает определенный объем дискового пространства в кластере. Он запрашивает конкретный объем из PV.

В общем, PVC используется для запроса хранилища, а PV - для предоставления этого хранилища. Таким образом, у вас есть гибкость в настройке хранилища в вашем кластере Kubernetes, так как вы можете просто добавить или удалить PV для увеличения или уменьшения доступного дискового пространства.

**Storage Class**
Данная сущность используется для общения с **облачными платформами**. Допусти когда мы говорим, что приложению нужен кусок диска в 20гб, можно попросить его у клауда и он закинет его в PVC

# Dynamic NFS Provisioner
https://www.youtube.com/watch?v=LUg8E4OMHTs&t=560s

Полезные источники и примеры постройки CI/CD с kubernetes и gitlab:
https://habr.com/ru/company/cloud_mts/blog/658427/
https://habr.com/ru/post/679826/
https://helm.sh/docs/chart_template_guide/values_files/
https://mcs.mail.ru/docs/additionals/cases/cases-gitlab/case-k8s-app
https://www.dmosk.ru/miniinstruktions.php?mini=gitlab-runner-web
http://snakeproject.ru/rubric/article.php?art=gitlab_31012022
# Harbor (реестр образов)

***Harbor*** — это реестр с открытым исходным кодом, который защищает артефакты с помощью политик и управления доступом на основе ролей, обеспечивает сканирование образов и отсутствие уязвимостей, а также подписывает образы как доверенные. Harbour, дипломированный проект CNCF, обеспечивает соответствие требованиям, производительность и функциональную совместимость, помогая вам последовательно и безопасно управлять артефактами на облачных вычислительных платформах, таких как Kubernetes и Docker. Harbor — реестр (локальное хранилище) для Docker-контейнеров
https://habr.com/ru/company/flant/blog/419727/
- Установка harbor на чистый centos 7
https://www.youtube.com/watch?v=_wSjzd73nrU
https://habr.com/ru/company/flant/blog/419727/
https://github.com/aronberman/youtubevideo/blob/main/harbor_installation/installation_script.txt
- 

[[Linux]] [[CI CD (пайплайн-конвейер)]] [[Git, Gitlab и Github]]