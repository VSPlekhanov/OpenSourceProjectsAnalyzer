#!/bin/bash
#ls -a /usr/lib/node_modules/
#set -m
/usr/apache-maven-3.6.3/bin/mvn org.springframework.boot:spring-boot-maven-plugin:run &
cd src/main/resources/js/angularclient/
ng serve --host 0.0.0.0 --disable-host-check
#fg %1