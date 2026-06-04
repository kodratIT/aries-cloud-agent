FROM node:18
WORKDIR /app

COPY ./package*.json ./
RUN npm install
RUN npm install -g nodemon

COPY ./templates .
COPY ./index.js ./

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["npm", "start"]
