cp docker-compose.yml /var/hotmaps/docker-compose-release-all.yml
cd /var/hotmaps/
docker-compose -f docker-compose-release-all.yml up --build -d