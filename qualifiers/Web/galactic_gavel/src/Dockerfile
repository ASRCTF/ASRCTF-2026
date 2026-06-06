FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --production

COPY . .

ENV PORT=3000
ENV FLAG=ASRCTF{w3bs0ck3t_sp4c3_h34st_succ3ssful}
ENV PRIVATE_ROOM_ID=stardust-7sigma-9f3a

EXPOSE 3000

CMD ["node", "server.js"]
