#!/usr/bin/env bash
git fetch && git checkout develop
git add .
echo Hello, Can you please add the commit message?
read commitmessage
git commit -m commitmessage
git push origin develop
ssh crem@vlhhotmapsdev.ch 'bash -s' < /var/hotmaps/scripts/toolbox-service/update.sh
