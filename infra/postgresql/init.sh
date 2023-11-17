#!/bin/bash
BASE_RUSSIAN_DICTIONARY_NAME=russian.stop;
CUSTOM_RUSSIAN_DICTIONARY_NAME=russian_extended.stop;
dir_with_dictionaries=$(pg_config --sharedir)/tsearch_data;
BASE_FILE="$dir_with_dictionaries/$BASE_RUSSIAN_DICTIONARY_NAME";
NEW_FILE="$dir_with_dictionaries/$CUSTOM_RUSSIAN_DICTIONARY_NAME";
cp $BASE_FILE $NEW_FILE;
echo -e 'общество\nответственностью\nограниченной' >> $NEW_FILE;
exec "$@"