FROM node:22-bookworm-slim AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /source
COPY Vamos_MVP_Fullstack_1.9.7.zip /tmp/vamos.zip
RUN unzip -q /tmp/vamos.zip -d /source

WORKDIR /source/backend
RUN npm ci
RUN npm run build

FROM node:22-bookworm-slim AS runtime

ENV NODE_ENV=production
WORKDIR /app

COPY --from=build /source/backend/package.json /source/backend/package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --from=build /source/backend/dist ./dist
COPY --from=build /source/admin /admin

EXPOSE 3000
CMD ["node", "dist/main.js"]
