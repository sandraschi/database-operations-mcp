# Tailscale Networking Guide

## Table of Contents
- [File Sharing](#file-sharing)
- [Tailscale SSH](#tailscale-ssh)
- [Tailscale Funnel](#tailscale-funnel)
- [Tailscale Serve](#tailscale-serve)
- [Tailscale ACLs](#tailscale-acls)
- [Tailscale Kubernetes](#tailscale-kubernetes)
- [Recent Features (2024)](#recent-features-2024)
- [Use Cases](#use-cases)
- [Security Best Practices](#security-best-practices)

## File Sharing

### Windows File Share
```powershell
# Create a new share
$shareName = "ProjectFiles"
$folderPath = "D:\\Projects"
New-SmbShare -Name $shareName -Path $folderPath -FullAccess "Everyone"

# Get Tailscale IP
tailscale ip
```

### Tailscale Built-in Sharing
```bash
# Share a file
tailscale file cp file.txt partner@example.com:

# Share a directory (recursive)
tailscale file cp ./project/ partner@example.com:project/

# List shared files
tailscale file ls
```

## Tailscale SSH

### Basic Usage
```bash
# Connect to a device using Tailscale
tailscale ssh user@device-name

# Generate SSH key pair
tailscale cert --cert-file=./device.crt --key-file=./device.key
```

### SSH Config
```
Host *.ts.net
  ProxyCommand tailscale ssh -H %h:%p
```

## Tailscale Funnel

### Expose Local Services
```bash
# Make a local web server public
tailscale serve https / http://localhost:3000

# Enable Funnel (requires admin approval)
tailscale funnel 3000 on
```

### Check Status
```bash
tailscale serve status
tailscale funnel status
```

## Tailscale Serve

## Serving Local Content

### 1. Basic Web Server
Quickly share files over HTTPS with automatic TLS certificates:

```bash
# Share a local directory via HTTPS
tailscale serve http / /path/to/your/folder

# Example: Share your project's 'public' directory
tailscale serve http / /home/username/projects/myapp/public
```

This will:
- Create a secure HTTPS server
- Generate automatic TLS certificates
- Make content available at `https://your-device-name.ts.net/`
- Only accessible to your Tailscale network by default

### 2. Adding Authentication
Restrict access to specific Tailscale users or groups:

```bash
# Require Tailscale authentication
tailscale serve --require-auth=true http / /path/to/private/folder

# Allow specific users (comma-separated)
tailscale serve --allow-users=alice@example.com,bob@example.com http / /secured-docs

# Allow an entire Tailscale group
tailscale serve --allow-groups=team-eng http / /team-docs
```

### 3. Reverse Proxy Setup
Securely expose local development servers:

```bash
# Basic reverse proxy to localhost:3000
tailscale serve https:443 / http://localhost:3000

# With custom domain (requires DNS setup)
tailscale serve https:443 / http://localhost:3000 --hostname=dev.yourdomain.com

# Multiple paths to different services
tailscale serve https:443 /api http://localhost:3000 \
  /docs http://localhost:8080 \
  / http://localhost:8000
```

### 4. Real-World Examples

#### Development Environment
```bash
# Share your local dev server with the team
tailscale serve https:443 / http://localhost:3000 --hostname=dev-app.your-org.ts.net
```

#### Internal Tool Access
```bash
# Securely share an internal tool with your team
tailscale serve --allow-groups=team-ops https:443 / http://localhost:4000
```

#### Temporary File Sharing
```bash
# Share files for 24 hours
tailscale serve --expiry=24h http / /path/to/temp/files
```
### 5. Monitoring and Management

Check what's being served:
```bash
# List all active serve endpoints
tailscale serve status

# View detailed configuration
tailscale serve config

# Stop serving content
tailscale serve off
```

### 6. Security Considerations
- All traffic is encrypted with TLS 1.3
- Access is restricted to your Tailscale network by default
- Use `--require-auth` to enforce Tailscale authentication
- Regularly audit active serve endpoints with `tailscale serve status`

## Tailscale ACLs (Access Control Lists)

Access Control Lists define who can access what resources in your Tailscale network. Here's a comprehensive example with explanations:

### Example Policy

```json
{
  // ACL Rules - Define what traffic is allowed
  "acls": [
    {
      "action": "accept",  // Allow the following rules
      "users": ["alice@example.com"],  // Who this applies to
      "ports": ["*:*"]  // Which ports and protocols (all in this case)
    }
  ],
  
  // SSH (Secure Shell) Access Control
  "ssh": [
    {
      "action": "check",
      "src": ["autogroup:member"],
      "dst": ["autogroup:self"],
      "users": ["root"]
    }
  ]
}
```

## Tailscale Kubernetes Integration

### 1. Installation and Setup

#### A. Install Tailscale Operator
```bash
# Create namespace
kubectl create namespace tailscale

# Install the operator with recommended settings
helm repo add tailscale https://pkgs.tailscale.com/helm-charts
helm upgrade --install tailscale-operator tailscale/tailscale-operator -n tailscale \
  --create-namespace \
  --set authKey=tskey-auth-xxxxxxxxx \
  --set clusterName=my-k8s-cluster \
  --set metrics.enabled=true \
  --set logLevel=info

# Verify installation
kubectl get pods -n tailscale -w
kubectl get svc -n tailscale
kubectl logs -n tailscale -l app=tailscale-operator --tail=50
```

#### B. Namespace and RBAC Configuration
```yaml
# tailscale-ns-rbac.yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: tailscale
  labels:
    name: tailscale
    app.kubernetes.io/name: tailscale
    app.kubernetes.io/instance: tailscale-operator
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: tailscale-operator
  namespace: tailscale
rules:
- apiGroups: [""]
  resources: ["services", "endpoints", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "update", "patch"]
```

### 2. Ingress Configurations

#### A. Basic HTTP Service with TLS
```yaml
# web-app-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app
  namespace: default
  annotations:
    # Core Tailscale annotations
    tailscale.com/expose: "true"
    tailscale.com/hostname: "app.${CLUSTER_NAME}.ts.net"
    tailscale.com/tags: "tag:web,tag:production"
    
    # Security annotations
    tailscale.com/ts-https: "true"  # Force HTTPS
    tailscale.com/ts-insecure: "false"  # Disable HTTP
    tailscale.com/ts-authkey: "${TAILSCALE_AUTH_KEY}"  # From secret
    
    # Advanced routing
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    
spec:
  tls:
  - hosts:
    - "app.${CLUSTER_NAME}.ts.net"
    secretName: tailscale-tls  # Auto-generated by cert-manager
  rules:
  - host: app.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80
```

#### B. Path-Based Routing with Authentication
```yaml
# api-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway
  namespace: api
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "api.${CLUSTER_NAME}.ts.net"
    tailscale.com/tags: "tag:api,tag:production"
    
    # Authentication
    tailscale.com/ts-auth: "true"
    tailscale.com/ts-auth-users: "user1@example.com,user2@example.com"
    tailscale.com/ts-auth-groups: "group:api-users"
    
    # Timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"

spec:
  rules:
  - host: api.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /v1/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 8080
      - path: /v1/products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8080
```

#### C. WebSocket Support
```yaml
# websocket-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: websocket-app
  namespace: websocket
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "ws.${CLUSTER_NAME}.ts.net"
    
    # WebSocket specific annotations
    nginx.ingress.kubernetes.io/websocket-services: "websocket-service"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/upstream-hash-by: "$remote_addr"
    
    # Security
    tailscale.com/ts-https: "true"
    tailscale.com/ts-insecure: "false"

spec:
  rules:
  - host: ws.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: websocket-service
            port:
              number: 8080
```

### 3. Advanced Security Configurations

#### A. Network Policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-tailscale-ingress
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tailscale
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

#### B. Pod Security Policies
```yaml
# psp-tailscale.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: tailscale-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
```

### 4. Monitoring and Observability

#### A. Prometheus ServiceMonitor
```yaml
# tailscale-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tailscale-operator
  namespace: monitoring
  labels:
    app: tailscale-operator
spec:
  selector:
    matchLabels:
      app: tailscale-operator
  namespaceSelector:
    matchNames:
    - tailscale
  endpoints:
  - port: metrics
    interval: 30s
    scrapeTimeout: 10s
```

#### B. Logging with Fluent Bit
```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        Parsers_File parsers.conf
        HTTP_Server  On
        HTTP_Listen  0.0.0.0
        HTTP_Port    2020

    [INPUT]
        Name              tail
        Path              /var/log/containers/*tailscale*.log
        Parser            docker
        Tag               tailscale.*
        Refresh_Interval  5
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On

    [OUTPUT]
        Name            es
        Match           *
        Host            elasticsearch
        Port            9200
        Index           tailscale-logs
        Type            _doc
        Logstash_Format On
        Logstash_Prefix tailscale
```

### 5. Troubleshooting Guide

#### A. Common Issues and Solutions

**1. Pods stuck in ContainerCreating**
```bash
# Check events
kubectl get events --sort-by='.metadata.creationTimestamp' -n tailscale

# Check logs
kubectl logs -n tailscale -l app=tailscale-operator --tail=50

# Check for image pull issues
kubectl describe pod -n tailscale <pod-name> | grep -i image
```

**2. Ingress not working**
```bash
# Check Ingress status
kubectl get ingress -A
kubectl describe ingress <ingress-name> -n <namespace>

# Check Tailscale status
kubectl exec -it -n tailscale <tailscale-pod> -- tailscale status

# Check network policies
kubectl get networkpolicies -A
```

**3. Authentication issues**
```bash
# Check Tailscale auth status
kubectl exec -it -n tailscale <tailscale-pod> -- tailscale status --peers

# Check logs for auth errors
kubectl logs -n tailscale -l app=tailscale-operator | grep -i auth
```

#### B. Debugging Tools

**1. Network Debug Pod**
```bash
# Create debug pod
kubectl run -it --rm --restart=Never debug-pod --image=nicolaka/netshoot -- /bin/bash

# Test connectivity
curl -v http://tailscale-operator.tailscale.svc.cluster.local
nslookup tailscale-operator.tailscale.svc.cluster.local
traceroute tailscale-operator.tailscale.svc.cluster.local
```

**2. Port Forwarding**
```bash
# Forward Tailscale admin interface
kubectl port-forward -n tailscale svc/tailscale-operator 4040:80

# Access in browser at http://localhost:4040
```

### 6. CI/CD Integration

#### A. GitHub Actions Workflow
```yaml
# .github/workflows/deploy-tailscale.yaml
name: Deploy Tailscale Configuration

on:
  push:
    branches: [ main ]
    paths:
      - 'kubernetes/tailscale/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v1
      
    - name: Deploy Tailscale Configuration
      env:
        KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
        TAILSCALE_AUTH_KEY: ${{ secrets.TAILSCALE_AUTH_KEY }}
      run: |
        mkdir -p ~/.kube
        echo "$KUBE_CONFIG" > ~/.kube/config
        
        # Apply configurations
        kubectl apply -f kubernetes/tailscale/namespace.yaml
        kubectl apply -f kubernetes/tailscale/rbac.yaml
        
        # Install/upgrade Tailscale operator
        helm repo add tailscale https://pkgs.tailscale.com/helm-charts
        helm upgrade --install tailscale-operator tailscale/tailscale-operator \
          -n tailscale \
          --create-namespace \
          --set authKey=${TAILSCALE_AUTH_KEY} \
          --set clusterName=${GITHUB_REPOSITORY##*/}
        
        # Apply other configurations
        kubectl apply -f kubernetes/tailscale/network-policies.yaml
        kubectl apply -f kubernetes/tailscale/ingress/
```

### 7. Multi-Cluster Setup

#### A. Cluster Federation
```yaml
# cluster-federation.yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: tailscale-service
  namespace: tailscale
---
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: EndpointSliceExport
metadata:
  name: tailscale-endpoints
  namespace: tailscale
```

#### B. Cross-Cluster Communication
```yaml
# cross-cluster-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cross-cluster-app
  namespace: default
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "global.${CLUSTER_NAME}.ts.net"
    tailscale.com/tags: "tag:global,tag:multi-cluster"
    tailscale.com/ts-advertise-routes: "10.0.0.0/8"  # Route to other clusters
    tailscale.com/ts-accept-routes: "true"
    
spec:
  rules:
  - host: global.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: global-app-service
            port:
              number: 80
```

### 8. Best Practices

1. **Security**
   - Always use HTTPS with valid certificates
   - Implement network policies to restrict traffic
   - Use Tailscale ACLs for fine-grained access control
   - Rotate auth keys regularly
   
2. **Performance**
   - Use appropriate resource requests/limits
   - Enable metrics and monitoring
   - Consider using Tailscale Funnel for public endpoints
   
3. **Reliability**
   - Deploy multiple replicas of the Tailscale operator
   - Configure proper liveness/readiness probes
   - Monitor and alert on critical metrics
   
4. **Maintenance**
   - Keep Tailscale components updated
   - Regularly review and update security policies
   - Document all configurations and changes
  - host: app.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port: { number: 8080 }
```

#### B. Path-based Routing with Authentication
```yaml
# api-gateway-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "api.${CLUSTER_NAME}.ts.net"
    tailscale.com/users: "dev-team@company.com,ops@company.com"
    tailscale.com/groups: "group:developers"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  rules:
  - host: api.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /api/v1/?(.*)
        pathType: Prefix
        backend:
          service:
            name: api-service
            port: { number: 3000 }
      - path: /admin/?(.*)
        pathType: Prefix
        backend:
          service:
            name: admin-dashboard
            port: { number: 3001 }
```

#### C. TLS Termination with Let's Encrypt
```yaml
# tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-app
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "secure-app.example.com"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    cert-manager.io/acme-challenge-type: http01
    kubernetes.io/tls-acme: "true"
spec:
  tls:
  - hosts:
    - secure-app.example.com
    secretName: secure-app-tls
  rules:
  - host: secure-app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: secure-service
            port: { number: 443 }
```

### 3. Advanced Configurations

#### A. Stateful Applications (Databases)
```yaml
# postgres-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: postgres
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "db.${CLUSTER_NAME}.ts.net"
    tailscale.com/proxy-mode: "direct"  # Direct pod-to-pod communication
    tailscale.com/users: "db-admins@company.com"
    tailscale.com/ssh: "true"  # Enable SSH access to pods
    tailscale.com/ssh-user: "postgres"
    tailscale.com/ssh-port: "5432"
spec:
  rules:
  - host: db.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: postgres-primary
            port: { number: 5432 }
```

#### B. WebSocket Support
```yaml
# websocket-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: websocket-app
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "ws.${CLUSTER_NAME}.ts.net"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/websocket-services: "websocket-svc"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_http_version 1.1;
spec:
  rules:
  - host: ws.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: websocket-svc
            port: { number: 8080 }
```

### 4. Security Hardening

#### A. Network Policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tailscale-policy
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  
  # Allow only Tailscale traffic
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tailscale
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: tailscale
  
  # Allow DNS resolution
  egress:
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
      
  # Allow Tailscale control plane
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.0.0.0/8
        - 172.16.0.0/12
        - 192.168.0.0/16
    ports:
    - protocol: UDP
      port: 41641  # Tailscale port
```

#### B. Pod Security Policies
```yaml
# psp-tailscale.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: tailscale-psp
  annotations:
    seccomp.security.alpha.kubernetes.io/allowedProfileNames: 'runtime/default'
    apparmor.security.beta.kubernetes.io/allowedProfileNames: 'runtime/default'
    seccomp.security.alpha.kubernetes.io/defaultProfileName:  'runtime/default'
    apparmor.security.beta.kubernetes.io/defaultProfileName:  'runtime/default'
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
```

### 5. Monitoring and Observability

#### A. Prometheus Metrics
```yaml
# tailscale-metrics.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tailscale-operator
  namespace: monitoring
  labels:
    app: tailscale-operator
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: tailscale-operator
  namespaceSelector:
    matchNames:
    - tailscale
  endpoints:
  - port: metrics
    interval: 30s
    scrapeTimeout: 10s
```

#### B. Logging Configuration
```yaml
# fluentbit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: tailscale
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        Parsers_File parsers.conf
        HTTP_Server  On
        HTTP_Listen  0.0.0.0
        HTTP_Port    2020

    [INPUT]
        Name              tail
        Path              /var/log/containers/*tailscale*.log
        Parser            docker
        Tag               tailscale.*
        Refresh_Interval  5
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On

    [OUTPUT]
        Name            es
        Match           *
        Host            ${ELASTICSEARCH_HOST}
        Port            ${ELASTICSEARCH_PORT}
        Logstash_Format On
        Logstash_Prefix tailscale
        Retry_Limit     False
```

### 6. Troubleshooting Guide

#### A. Common Issues and Solutions

1. **Tailscale Pods Not Starting**
   ```bash
   # Check pod status
   kubectl get pods -n tailscale
   
   # View pod logs
   kubectl logs -n tailscale -l app.kubernetes.io/name=tailscale-operator
   
   # Check for node issues
   kubectl describe nodes | grep -i taint
   
   # Verify image pull secrets
   kubectl get secrets -n tailscale
   ```

2. **Connectivity Issues**
   ```bash
   # Check Tailscale status
   kubectl exec -n tailscale -it <tailscale-pod> -- tailscale status
   
   # Test DNS resolution
   kubectl run -it --rm --image=busybox:1.28 --restart=Never -- dns-test \
     -- nslookup <service>.<namespace>.svc.cluster.local
   
   # Check network policies
   kubectl get networkpolicies --all-namespaces
   
   # Verify service endpoints
   kubectl get endpoints <service-name> -n <namespace>
   ```

3. **TLS/SSL Issues**
   ```bash
   # Check certificate status
   kubectl get certificates,certificaterequests,order,challenge -A
   
   # View certificate details
   kubectl describe certificate <cert-name> -n <namespace>
   
   # Check cert-manager logs
   kubectl logs -n cert-manager -l app=cert-manager
   
   # Test TLS connection
   openssl s_client -connect <host>:443 -servername <host> -showcerts
   ```

4. **Performance Tuning**
   ```yaml
   # tailscale-operator-values.yaml
   resources:
     requests:
       cpu: 100m
       memory: 128Mi
     limits:
       cpu: 500m
       memory: 512Mi
   
   # Add node affinity for better performance
   affinity:
     nodeAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
         nodeSelectorTerms:
         - matchExpressions:
           - key: node-role.kubernetes.io/worker
             operator: In
             values:
             - "true"
   
   # Add pod anti-affinity
   podAntiAffinity:
     preferredDuringSchedulingIgnoredDuringExecution:
     - weight: 100
       podAffinityTerm:
         labelSelector:
           matchExpressions:
           - key: app.kubernetes.io/name
             operator: In
             values:
             - tailscale-operator
         topologyKey: kubernetes.io/hostname
   ```

#### B. Debugging Tools

1. **Network Debug Pod**
   ```bash
   # Create debug pod
   kubectl run -it --rm --restart=Never debug-pod --image=nicolaka/netshoot -- /bin/bash
   
   # Test connectivity
   curl -v http://<service>.<namespace>.svc.cluster.local:8080
   nc -zv <service> <port>
   dig <service>.<namespace>.svc.cluster.local
   ```

2. **Tailscale Debug Commands**
   ```bash
   # Get debug logs
   kubectl exec -n tailscale <pod-name> -- tailscale debug /var/run/tailscale/tailscaled.sock debug
   
   # View routes
   kubectl exec -n tailscale <pod-name> -- tailscale status --peers
   
   # Ping test
   kubectl exec -n tailscale <pod-name> -- tailscale ping <host>
   ```

3. **Network Policy Tester**
   ```yaml
   # network-policy-tester.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: netpol-tester
     labels:
       app: netpol-tester
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: netpol-tester
     template:
       metadata:
         labels:
           app: netpol-tester
       spec:
         containers:
         - name: netpol-tester
           image: nicolaka/netshoot
           command: ["/bin/sh", "-c", "sleep 3600"]
   ```

## 7. CI/CD Integration

### A. GitOps with ArgoCD
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tailscale-apps
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/kubernetes-gitops.git
    targetRevision: HEAD
    path: apps/tailscale
    plugin:
      name: kustomize
  destination:
    server: https://kubernetes.default.svc
    namespace: tailscale
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### B. GitHub Actions Workflow
```yaml
# .github/workflows/deploy-tailscale.yaml
name: Deploy Tailscale Configuration

on:
  push:
    branches: [ main ]
    paths:
      - 'kubernetes/tailscale/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Install kubectl
      uses: azure/setup-kubectl@v1
    
    - name: Configure kubeconfig
      uses: azure/k8s-set-context@v1
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy Tailscale resources
      run: |
        kubectl apply -f kubernetes/tailscale/namespace.yaml
        kubectl apply -f kubernetes/tailscale/operator.yaml
        kubectl apply -f kubernetes/tailscale/ingress/
      env:
        KUBECONFIG: ${{ secrets.KUBE_CONFIG }}
```

## 8. Multi-cluster Setup

### A. Cluster Federation
```yaml
# tailscale-federation.yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: tailscale-operator
  namespace: tailscale
---
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceImport
metadata:
  name: tailscale-operator
  namespace: tailscale
spec:
  type: ClusterSetIP
  ports:
  - port: 443
    protocol: TCP
```

### B. Cross-cluster Communication
```yaml
# tailscale-multicluster.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cross-cluster
  annotations:
    tailscale.com/expose: "true"
    tailscale.com/hostname: "global.${CLUSTER_NAME}.ts.net"
    tailscale.com/tags: "tag:global,tag:cross-cluster"
    # Enable cross-cluster load balancing
    tailscale.com/load-balancer: "true"
    # Enable session affinity
    tailscale.com/session-affinity: "ClientIP"
    # Enable connection draining
    tailscale.com/connection-draining-timeout: "30s"
spec:
  rules:
  - host: global.${CLUSTER_NAME}.ts.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: global-service
            port: { number: 80 }
```

## Recent Features (2024)

### 1. Tailscale SSH Certificates
```bash
# Generate SSH certificate
tailscale cert --cert-file=./device.crt --key-file=./device.key
```

### 2. MagicDNS Improvements
```bash
# Access devices by name
tailscale ping device-name
```

### 3. Subnet Router Improvements
```bash
# Advertise routes
tailscale up --advertise-routes=192.168.1.0/24
```

### 4. Tailscale Funnel (Beta)
```bash
# Make a local service public
tailscale funnel 8080 on
```

## Use Cases

### 1. Remote Development
```bash
# Access remote dev environment
tailscale ssh dev@dev-machine

# Share local dev server
tailscale serve https / http://localhost:3000
```

### 2. Secure File Transfer
```bash
# Send files securely
tailscale file cp report.pdf team@example.com:
```

### 3. Access Home Network
```bash
# Connect to home devices
tailscale up --exit-node=home-router
```

### 4. Team Collaboration
```bash
# Share access to internal tools
tailscale serve https /internal http://localhost:8080
```

## Security Best Practices

### 1. Use ACLs
```json
{
  "acls": [
    {
      "action": "accept",
      "users": ["team@example.com"],
      "ports": [
        "tag:webserver:80,443",
        "tag:database:5432"
      ]
    }
  ]
}
```

### 2. Enable MFA
```bash
# Require MFA for all devices
tailscale up --force-reauth
```

### 3. Use Tailscale SSH
```bash
# Enforce Tailscale SSH
tailscale up --ssh
```

### 4. Monitor Connections
```bash
# View active connections
tailscale status

# View logs
tailscale debug logs
```

## Troubleshooting

### Common Issues

1. **Connection Issues**
   ```bash
   # Check Tailscale status
   tailscale status
   
   # Check routes
   tailscale netcheck
   ```

2. **File Sharing**
   ```powershell
   # Check Windows sharing
   Get-SmbShare
   
   # Check firewall
   Get-NetFirewallRule -DisplayName "*Tailscale*" | Select-Object DisplayName,Enabled
   ```

3. **Performance**
   ```bash
   # Check connection quality
   tailscale ping device-name
   
   # Check network routes
   tailscale netcheck
   ```

## Additional Resources

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Tailscale Blog](https://tailscale.com/blog/)
- [GitHub Repository](https://github.com/tailscale/tailscale)
