read -s -p "Enter gpg passphrase: " PWD
cd /var/hotmaps/HotMaps-toolbox-service

git pull
git secret reveal -p PWD
docker build -t hotmaps/toolbox-service .
docker network disconnect -f bridge toolbox-service
docker kill toolbox-service
docker rm -fv toolbox-service
docker run \
        --name=toolbox-service \
        --link postgis-database:postgis \
        -p 9005:80 \
        -d \
        hotmaps/toolbox-service
