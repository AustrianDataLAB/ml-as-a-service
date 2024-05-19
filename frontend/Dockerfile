# Maybe pinnning down the versiosn of the base image and the angular/cli does make sense ?

FROM node:alpine AS builder

ARG BACKEND_API_PORT
ARG BACKEND_API_URL

WORKDIR app

COPY package.json package-lock.json ./
RUN npm install -g @angular/cli && npm install

COPY . /app

RUN npm run build

FROM cgr.dev/chainguard/nginx:latest
COPY --from=builder /app/dist/frontend /var/www/html

EXPOSE 80

