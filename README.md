# QueryCube Web

A web version of the querycube tool https://github.com/FAIRiCUBE/uc3-drosophola-genetics/tree/main/projects/QueryCube

## **Clone repository from git**

```bash
git clone https://github.com/FAIRiCUBE/querycube-web
```

## Set environment varables

**Create a file called `.env` in the `root` folder and set the variables**

```
RASDAMAN_SERVICE_ENDPOINT=
RASDAMAN_CRED_USERNAME=
RASDAMAN_CRED_PASSWORD=
API_PORT=5000
CLIENT_PORT=80
```

## Docker

Make sure you have Docker engine installed. (https://www.docker.com/)  
Then build and run the `docker-compose` file.

```powershell
# build and run
docker compose up --build -d
# Access at: http://localhost
```
