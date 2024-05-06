FROM node:alpine AS builder
ARG BACKEND_API_PORT
ARG BACKEND_API_URL
WORKDIR /usr/src/app

ARG BACKEND_URL=$BACKEND_API_URL
ARG BACKEND_PORT=$BACKEND_API_PORT

COPY . /usr/src/app

RUN npm install -g @angular/cli

RUN npm install

RUN npm run build

RUN cat src/environments/environment.ts
CMD ["npm", "start"]
#CMD ["ng", "serve", "--host", "0.0.0.0"]



##ToDo: change to use latest and copy only what is needed
#FROM cgr.dev/chainguard/nginx@sha256:bcc6b0d052298112e4644b258de0fa4dc1509e3df8f7c0fba09e8c92987825e7
#COPY --from=builder /usr/src/app /var/www/html/public/
