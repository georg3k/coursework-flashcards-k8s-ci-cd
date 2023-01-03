# Flask app + Kubernetes + GitLab CI/CD coursework
## Run using docker-compose
Build containers and start services:
```
docker-compose up -d --build
```
Open in browser: http://localhost:8080/ for main app and http://localhost:8081/ for Mongo-Express

Run tests (currently not included, Postman export is expected at ./tests/integrations.json):
```
docker-compose --profile testing up --build --abort-on-container-exit --exit-code-from newman
```
## Setup Kubernetes cluster
Download Vagrant box image (if Vagrant image repository is not available in your country):
```
wget https://app.vagrantup.com/ubuntu/boxes/focal64/versions/20221213.0.0/providers/virtualbox.box
vagrant box add ubuntu/focal64 ./virtualbox.box
```
Patch default VirtualBox settings for host network adapters:
```
echo "* 0.0.0.0/0 ::/0" | sudo tee -a /etc/vbox/networks.conf
```
Prepare virtualized cluster using Vagrant:
```
cd ./vagrant
vagrant up
```
SSH into master node (further commands are executed on virtual master node):
```
vagrant ssh master
```
Install load balancer in Kubernetes cluster (optionally):
```
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
```
Configure load balancer (optionally):
```
cat > ./pool.yml << EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: main-pool
  namespace: metallb-system
spec:
  addresses:
  - 10.0.0.240-10.0.0.250
EOF

cat > ./adv.yml << EOF
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: metallb-adv
  namespace: metallb-system
EOF

kubectl apply -f pool.yml
kubectl apply -f adv.yml
```
## Install GitLab Agent and GitLab Runner in Kubernetes cluster
Install Helm:
```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```
Create service account for GitLab Executor (this particular setup create a binding with admin privileges, you may want to use some other settings):
```
cat > ./user.yml << EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gitlab
  namespace: gitlab-runner
---
apiVersion: rbac.authorization.k8s.io/v1 
kind: ClusterRoleBinding
metadata:
  name: gitlab-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: gitlab
    namespace: kube-system
EOF

kubectl apply -f user.yml
```
Create values.yml file for GitLab Runner Helm chart configuration (insert your own runnerRegistrationToken):
```
image:
  registry: registry.gitlab.com
  image: gitlab-org/gitlab-runner
imagePullPolicy: IfNotPresent
gitlabUrl: https://gitlab.com/
runnerRegistrationToken: "***"
terminationGracePeriodSeconds: 3600
concurrent: 10
checkInterval: 30
sessionServer:
  enabled: false
rbac:
  create: false
  rules: []  
  serviceAccountName: gitlab        
  podSecurityPolicy:
    enabled: false
    resourceNames:
    - gitlab-runner
metrics:
  enabled: false
  portName: metrics
  port: 9252
  serviceMonitor:
    enabled: false
service:
  enabled: false
  type: ClusterIP
runners:
  config: |
    [[runners]]
      [runners.kubernetes]
        namespace = "{{.Release.Namespace}}"
        image = "ubuntu:16.04"                                                                                        
  cache: {}
  builds: {}
  services: {}
  helpers: {}                   
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false
  runAsNonRoot: true
  privileged: false
  capabilities:
    drop: ["ALL"]
podSecurityContext:
  runAsUser: 100
    fsGroup: 65533
resources: {}    
affinity: {}
nodeSelector: {}
tolerations: []
hostAliases: []
podAnnotations: {}
podLabels: {}
priorityClassName: ""
secrets: []
configMaps: {}
volumeMounts: []
volumes: []
```
Install GitLab Runner and GitLab Agent (insert your own config.token):
```
helm repo add gitlab https://charts.gitlab.io
helm repo update gitlab
helm install --namespace gitlab-runner gitlab-runner -f values.yml gitlab/gitlab-runner
helm upgrade --install k8s gitlab/gitlab-agent \
    --namespace gitlab-agent-k8s \
    --create-namespace \
    --set image.tag=v15.7.0 \
    --set config.token=*** \
    --set config.kasAddress=wss://kas.gitlab.com
```
*gitlab.io is not available in some countries so you may need a VPN connection or some other way to access Helm Charts repo*
## Use your cluster for CI/CD jobs and application deployments
Now you should be able to execute your CI/CD jobs on your cluster, build and upload Docker images to GitLab Registry and deploy applications using helm and/or manifests.