FROM node:20-alpine

WORKDIR /app

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "if [ -f package.json ]; then npm install && npm start; else node -e \"require('http').createServer((req,res)=>{res.writeHead(200, {'Content-Type':'application/json'});res.end(JSON.stringify({status:'ok'}));}).listen(3000,'0.0.0.0')\"; fi"]
