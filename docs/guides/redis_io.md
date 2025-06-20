---
description: "Interact with redis to download and upload data"
---

# Redis I/O
This guide explains how to interact with Redis to download and upload data using CSM-DUQ

## Redis Use

Any command using redis has multiple parameters to configure

  - `host` with a default value at `localhost`.  
    &emsp;
    It can be set either :  
        &emsp;&emsp;
        - while calling a command with `--host`.  
          &emsp;&emsp;
        - as an environment variable under `REDIS_HOST`.  
  - `port` with a default value at `6379`.  
      &emsp;
    It can be set either :  
          &emsp;&emsp;
        - while calling a command with `--port`.  
          &emsp;&emsp;
        - as an environment variable under `REDIS_PORT`.
  - `password` it can be set either :  
    &emsp;
    \- while a command with `-p` or `--password`.  
    &emsp;
    \- as an environment variable under `REDIS_SECRET`.

## Redis Storage

Whether it is downloaded or data to be uploaded, all data to be used are to be organized the same way with :

- `parent folder` the name is unimportant.
- `index folders` with the name of the index used for this category of objects.
- `object files` the files containing the objects downloaded/to be uploaded to redis, most of the time as `json`.  
    &emsp;
    The name of the file should be the id of the object stored inside

It should be structured as such :

```
parent folder
│
├──  index folder
│    ├── object file
│    └── object file
│
├── index folder
│   └── object file
│
└── index folder
    ├── object file
    ├── object file
    └── object file
```


## Redis Download

To download data from redis, the command `redis-dump` is used, this command can take multiple arguments on top of the default redis ones :

- `file path` is the folder in which the downloaded data will be stored.
    It can either be set while calling with `--file_path` or `-f` or with the environment variable `REDIS_FILE_PATH`.  
- `index list` allows to only download data stored under certain indexes.  
    It can be set while calling with `--index_list` or `-i` and can be used multiple times to query multiple indexes.  
    If it's not used, then all indexes will be collected and all indexed objects in the database will be downloaded.


## Redis Upload

To upload data to redis, the command `redis-file-upload` is used, this command take one argument on top of the default redis ones :

- `file path` is the folder in which the data to upload is stored.
    It can either be set while calling with `--file_path` or `-f` or with the environment variable `REDIS_FILE_PATH`. 

Before running this command, assert that the names of the index folders are the proper domain names and the object files the correct object id.


## Redis Index List

If you're not sure about which index exist in your redis database, you can get the list by calling `redis-list-index` command