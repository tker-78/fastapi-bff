FROM node:22
WORKDIR /
COPY ui/package.json .
RUN npm install
COPY ui /code
WORKDIR /code
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
EXPOSE 5173