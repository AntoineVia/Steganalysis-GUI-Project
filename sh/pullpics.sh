#!/bin/bash

test -f ./txt/pictures-clean.txt && rm ./txt/pictures-clean.txt

adb -s "$1" shell "test -f /sdcard/pictures.txt && rm /sdcard/pictures.txt"
adb -s "$1" shell "test -f /sdcard/pictures-clean.txt && rm /sdcard/pictures-clean.txt"
adb -s "$1" shell "find /sdcard/ -iname '*.jpg' -o -iname '*.jpeg' | grep -v .thumbnails >> /sdcard/pictures.txt"
adb -s "$1" shell "tr -d '\r' < /sdcard/pictures.txt > /sdcard/pictures-clean.txt"
adb -s "$1" shell "rm /sdcard/pictures.txt"
adb -s "$1" pull /sdcard/pictures-clean.txt ./txt

mkdir ./imports/"$2"
while read -r LINE
    do
        adb -s "$1" pull "$LINE" ./imports/"$2"
    done < ./txt/pictures-clean.txt