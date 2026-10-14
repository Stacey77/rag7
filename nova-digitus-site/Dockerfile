# Nova Digitus Designs public site, served by nginx.
# Coolify: New Resource > Application > GitHub repo Stacey77/WellOff
#          Base Directory: /nova-digitus-site   Build Pack: Dockerfile   Port: 80
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html thanks.html /usr/share/nginx/html/
COPY apps/ /usr/share/nginx/html/apps/

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
