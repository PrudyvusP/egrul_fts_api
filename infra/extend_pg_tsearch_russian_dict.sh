#!/bin/bash

CONTAINER_NAME=infra_db_1;
BASE_RUSSIAN_DICTIONARY_NAME=russian.stop;
CUSTOM_RUSSIAN_DICTIONARY_NAME=russian_extended.stop;

dir_with_dictionaries=$(docker exec $CONTAINER_NAME pg_config --sharedir)/tsearch_data;

docker exec $CONTAINER_NAME cp "$dir_with_dictionaries/$BASE_RUSSIAN_DICTIONARY_NAME" "$dir_with_dictionaries/$CUSTOM_RUSSIAN_DICTIONARY_NAME";
docker exec $CONTAINER_NAME bash -c "echo -e 'общество\nответственностью\nограниченной' >> $dir_with_dictionaries/$CUSTOM_RUSSIAN_DICTIONARY_NAME"