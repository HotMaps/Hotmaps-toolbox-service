# HotMaps-toolbox Docker image

![Build Status](https://vlheasilab.hevs.ch/buildStatus/icon?job=Hotmaps-toolbox-service%2Fdevelop)

The Hotmaps toolbox is built around several services:
- frontend (Angular, typescript)
- backend (Flask, python)
- database (Postgresql + PostGIS)
- map server (Geoserver)
- calculation modules (Flask, python)
- reverse proxy (Nginx)
- wiki (Gollum)

All these services are built around Docker.
A docker-compose.yml file allows to configure and run the whole project in one place. Only the database is run separatly.

### Build, configure and run:
#### Build
Dockerfiles are available to build the project manually. 
A docker-compose.yml file is available to build all the services.

#### Configure

First configure all the services in docker-compose.yml.
Make sure the volume bindings, build and environment paths fits your project on your host machine.
If `.env` files are mentionned in the `docker-compose.yml`, update their content to match your own configuration (crendentials, urls, ...). 

The `docker-compose.yml` file should be place on the root directory of your project (where all you repositories are cloned).

You can also run the toolbox without reverse proxy, wiki and geoserver using the `docker-compose-local.yml`.

`.env` files should be place at the root of each repository (if necessary).

##### Project structure

- root /
  - toolbox-service /
    - [code]
    - .env (config. file)
  - toolbox-client /
    - [code]
    - .env (config. file)
  - wiki /
    - [code]
    - .env (config. file)
  - geoserver /
    - web.xml (config. file)
  - nginx / 
  - calculation_modules /
    - CM1 /
    - CM2 /
  - docker-compose.yml
  - docker-compose-local.yml


#### Run

First, run the database, either using Docker or using an external service. The database should have 4 schemas:
- geo
- public
- stat
- users

To populate the database, refer to the official Hotmaps [Wiki](https://wiki.hotmaps.eu/en/Developers#dataset-integration).

*If you hosted geoserver differently, make sure it's accessible.*

Run the project using docker-compose:
`docker-compose up -d --build`

