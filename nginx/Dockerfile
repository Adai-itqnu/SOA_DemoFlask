FROM nginx:alpine

# Cài đặt consul-template
RUN apk add --no-cache curl unzip && \
    curl -L https://releases.hashicorp.com/consul-template/0.36.0/consul-template_0.36.0_linux_amd64.zip -o /tmp/consul-template.zip && \
    unzip /tmp/consul-template.zip -d /usr/local/bin && \
    rm /tmp/consul-template.zip && \
    chmod +x /usr/local/bin/consul-template

# Copy frontend files (will be copied from parent context)
COPY frontend /usr/share/nginx/html

# Copy nginx config template
COPY nginx.conf.ctmpl /etc/nginx/templates/nginx.conf.ctmpl

# Copy script để chạy consul-template và nginx
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]

