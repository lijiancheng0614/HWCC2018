#!/bin/bash

rm -fr bin
mkdir bin
rm -fr build
mkdir build
cd build

cmake ../ecs
tmp=$?
if [ ${tmp} -ne 0 ]
then
    exit -1
fi

make
tmp=$?
if [ ${tmp} -ne 0 ]
then
    exit -1
fi


cd ..

if [ -f ecs.tar.gz ]
then
    rm -f ecs.tar.gz
fi

tar -zcPf ecs.tar.gz *
