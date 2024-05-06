FROM node:alpine AS builder

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN npm install -g @angular/cli

RUN npm install

sed -i "s|API_URL_PLACEHOLDER|$API_URL|g" /usr/src/app/src/environments/environment.ts

CMD ["/usr/src/app/replace-env-vars.sh"]

CMD ["ng", "serve", "--host", "0.0.0.0"]


#ToDo: change to use latest and copy only what is needed
FROM cgr.dev/chainguard/nginx@sha256:bcc6b0d052298112e4644b258de0fa4dc1509e3df8f7c0fba09e8c92987825e7
COPY --from=builder /usr/src/app /var/www/html/public/
