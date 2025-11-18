#!/bin/sh

# Đợi Consul sẵn sàng
until wget -q -O- http://${CONSUL_ADDR:-consul:8500}/v1/status/leader > /dev/null 2>&1; do
    echo "Waiting for Consul..."
    sleep 2
done

# Chạy consul-template để generate nginx config và reload nginx khi có thay đổi
consul-template \
    -consul-addr=${CONSUL_ADDR:-consul:8500} \
    -template="/etc/nginx/templates/nginx.conf.ctmpl:/etc/nginx/nginx.conf:nginx -s reload || true" \
    -log-level=info &

# Chờ consul-template tạo file config đầu tiên
sleep 3

# Chạy nginx ở foreground
nginx -g "daemon off;"

