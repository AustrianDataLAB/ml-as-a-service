FROM node:alpine AS indexer

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN npm install -g @angular/cli

RUN npm install

CMD ["ng", "serve", "--host", "0.0.0.0"]


FROM cgr.dev/chainguard/nginx:latest
COPY --from=builder /usr/src/app /var/www/html/public/
