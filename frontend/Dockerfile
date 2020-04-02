FROM node:12.16.1-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json /app/package.json
RUN yarn install

COPY run.sh /app/run.sh
ENTRYPOINT ["/bin/sh", "/app/run.sh"]
CMD ["start"]