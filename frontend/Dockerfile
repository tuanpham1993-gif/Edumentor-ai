# Frontend EduMentor AI (React + Vite) — Tuấn · 13/11/2026.
# Build + chạy từ gốc dự án:   docker compose up -d --build frontend
#
# 2 bước: Node build ra dist/ (file tĩnh) → nginx phục vụ dist/ và chuyển /api, /uploads sang backend
# (thay proxy của Vite khi chạy dev — xem nginx.conf trong thư mục này).

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
