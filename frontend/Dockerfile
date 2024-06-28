# Stage 1: Build the Angular application
FROM node:alpine as build
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN npm install -g @angular/cli
RUN npm install
RUN ng build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine
COPY --from=build /usr/src/app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
