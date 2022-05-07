from kubernetes import client, config, watch
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import environ

metric_port = environ.get('METRIC_PORT', '9102')
metric_path = environ.get('METRIC_PATH', '/metrics')
deploy_source_name      = environ.get('DEPLOY_SOURCE_NAME')
deploy_source_namespace = environ.get('DEPLOY_SOURCE_NAMESPACE')
deploy_target_name      = environ.get('DEPLOY_TARGET_NAME')
deploy_target_namespace = environ.get('DEPLOY_TARGET_NAMESPACE')

def metric_value():
    try:
        config.load_incluster_config()
    except:
        print("ERROR: Incluster config load failed. Loading local kube config. If you see this in cluster check Pod permissions")
        config.load_kube_config()
    v1 = client.AppsV1Api()
    deploy_source = v1.list_namespaced_deployment(deploy_source_namespace, field_selector = f"metadata.name={deploy_source_name}")
    deploy_target = v1.list_namespaced_deployment(deploy_target_namespace, field_selector = f"metadata.name={deploy_target_name}")
    return deploy_source.items[0].status.replicas / deploy_target.items[0].status.replicas

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == metric_path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            message = "synchro_scale_coefficient" + " " + str(metric_value())
            self.wfile.write(bytes(message, "utf8"))
        else:
            self.send_response(404)

with HTTPServer(('', int(metric_port)), handler) as server:
    server.serve_forever()
