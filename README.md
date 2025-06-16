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

## TODO

1. add comment about the map in the documentation popup
1. send query as csv file
```python
    def getSamples(self, path):
        filtered_data = {}
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                lat = row["lat"] or row["latitude"]
                long = row["long"]
                date = row["date"]
                print(lat, long, date)
                if lat == 'NA' and long == 'NA':
                    continue
                # else:
                    # long,lat=trans4mEPSG("EPSG:4326","EPSG:3035",float(long),float(lat))
                if float(lat) > self.minlat and float(lat) < self.maxlat and float(long) > self.minlong and float(long) < self.maxlong:
                    sampleinfo = (row["lat"], row["long"], row["date"])
                    filtered_data[row["sampleId"]] = sampleinfo
                    # filtered_data.append(sampleinfo)
        self.samples = filtered_data
```
