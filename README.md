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

## Build, configure and run:
### Build
Dockerfiles are available to build the project manually. 
A docker-compose.yml file is available to build all the services.

### Configure

First configure all the services in docker-compose.yml.
Make sure the volume bindings, build and environment paths fits your project on your host machine.
If `.env` files are mentionned in the `docker-compose.yml`, update their content to match your own configuration (crendentials, urls, ...). 

The `docker-compose.yml` file should be place on the root directory of your project (where all you repositories are cloned).

You can also run the toolbox without reverse proxy, wiki and geoserver using the `docker-compose-local.yml` (and place it also at the root of your project).

`.env` config. files should be place at the root of each repository (if necessary) to set the configuration of each service.


#### Project structure


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
  - nginx.tmpl (config. file for dockergen service)

**Notes**

Wiki:
- the wiki image is pulled by the docker-compose
    - image and doc: [hotmaps/gollum](https://hub.docker.com/r/hotmaps/gollum)
- pull the wiki repository (the content of the wiki) to the root of your project according to structure
    - repository: [Official Hotmaps wiki](https://github.com/HotMaps/wiki/)
    - you can of cours configure your own repository for the content
- you should provide a valid ssh key to your wiki in order to push the modifications to the remote
    - config. in docker-compose.yml/wiki/volumes/.ssh
- `.env`: 
    - there is an .env.example in the wiki content [repository](https://github.com/HotMaps/wiki/)
    - you can find all options and environment variables available in the readme of the docker image on [hotmaps/gollum](https://hub.docker.com/r/hotmaps/gollum)

### Run

First, run the database, either using Docker or using an external service. The database should have 4 schemas:
- geo
- public
- stat
- users

To populate the database, refer to the official Hotmaps [Wiki](https://wiki.hotmaps.eu/en/Developers#dataset-integration).

*If you hosted geoserver differently, make sure it's accessible.*

Run the project using docker-compose:
`docker-compose up -d --build`

## Release

To release the project to a server, use the file `docker-compose.yml`.
This file is using a reverse proxy (nginx) automatically 
Your server should have: 
- 4 subdomains 'wiki', 'geoserver', 'api' and 'www'
    - edit `docker-compose.yml`: replace all VIRTUAL_HOST, VIRTUAL_PORT and LETSENCRYPT_HOST + LETSENCRYPT_EMAIL to match your own configuration
- min ports to open: 80/443 
- 1 postgis database setup somewhere
- 1 geoserver setup somewhere (or use the one in the docker-compose)
    - edit `web.xml` to match your own domain (`web.xml` is the one shared in the `docker-compose.yml`, especially the CORS)
- 1 gurobi v8 license for some calculation modules
- nginx.tmpl configured for the server url