#!/usr/bin/env bash
git fetch && git checkout develop
git add .
echo Hello, Can you please add the commit message?
read commitmessage
git commit -m commitmessage
git push origin develop
ssh root@vlhh2020.hevs.ch <<'ENDSSH'
#commands to run on remote host
sudo -i

sh /var/hotmaps/scripts/toolbox-service/update.sh
ENDSSH