# ---- Stage 1: Build ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mkdocs.yml .
COPY docs/ docs/
COPY overrides/ overrides/

RUN mkdocs build

# ---- Stage 2: Serve ----
FROM nginx:1.27-alpine

# Use non-privileged port
COPY --from=builder /build/site /usr/share/nginx/html

# Custom nginx config: listen on 8080, SPA-style fallback
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
