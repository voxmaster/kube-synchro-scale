# kube-synchro-scale
Publish metrics that allows you to scale 2 Kubernetes Deployments almost synchronously using HPA

## How does it works
HTTP server gives you an `synchro_scale_coefficient` metric on `/metrics` URL path which represent next formula: `Source Deploy Replicas / Target Deploy Replicas`

## Configuration
Use environment variables to configure the application

| Environment variable name | Description             | Default value  |
|:--------------------------|:------------------------|:---------------|
|`METRIC_PORT`              | Metrics port            | `9102`           | 
|`METRIC_PATH`              | Metrics URL path        | `/metrics`       |
|`DEPLOY_SOURCE_NAME`       |Deployment name to be in sync with |      | 
|`DEPLOY_SOURCE_NAMESPACE`  |Deployment namespace to be in sync with|  | 
|`DEPLOY_TARGET_NAME`       |Deployment name to be synced    |         |
|`DEPLOY_TARGET_NAMESPACE`  |Deployment namespace to be synced   |     |

## Required permissions
- List and Get Deployments

## Example usage
Minimal setup (Permissions and prometheus configuration not included)
```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: targetapp
spec:
  selector:
    matchLabels:
      app: targetapp
  template:
    metadata:
      labels:
        app: targetapp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: /metrics
        prometheus.io/port: '9102'
    spec:
      containers:
        - name: kube-synchro-scale
          image: voxsoft/kube-synchro-scale:1.0.0
          imagePullPolicy: Always
          ports:
            - containerPort: 9102
              protocol: TCP
          env:
            - name: DEPLOY_SOURCE_NAME
              value: sourceapp
            - name: DEPLOY_SOURCE_NAMESPACE
              value: default
            - name: DEPLOY_TARGET_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: DEPLOY_TARGET_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace

---
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: scale-targetapp-based-on-sourceapp-replicas
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: targetapp
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Pods
      pods:
        metric:
          name: synchro_scale_coefficient
        target:
          type: AverageValue
          averageValue: 1000m
```

Other examples [./examples](./examples)
