---
description: "Make and restore Redis Backups for local development and rollback operations"
---

# Redis Backups

This guide explains how to create Redis database backups, use them for local development, and restore them when needed. These procedures are essential for testing changes safely and performing rollbacks in production environments.

## Prerequisites

- `redis-tools` package (for `redis-cli`)
- `kubectl` (for Kubernetes operations)
- Docker (for local Redis instance)

## Creating Redis Backups

There are two primary methods to create Redis backups:

1. **Direct method**: Connect to the Redis database using `redis-cli` and generate a backup directly on your local machine
2. **Kubernetes method**: Create a backup within the Redis pod and copy it to your local machine

### Method 1: Using `redis-cli` Directly

This method allows you to create a backup directly from any Redis instance without requiring access to the underlying pod.

#### Step 1: Install Redis CLI Tools

```bash
# On Ubuntu/Debian
sudo apt-get install redis-tools
```

#### Step 2: Create the Redis Dump File

The following command connects to your Redis instance and creates a `.rdb` dump file containing all your data:

```bash title="Creating a Redis dump file"
redis-cli -a <redis_pwd> --rdb dump.rdb
```

Replace `<redis_pwd>` with your actual Redis password. This command will create a `dump.rdb` file in your current directory containing a complete snapshot of your Redis database.

### Method 2: Using Kubernetes to Access a Redis Instance

This method is useful when you need to backup Redis instances running in Kubernetes clusters.

#### Step 1: Set Up Environment Variables

First, define a descriptive name for your backup file:

```bash title="Setting up backup environment variables"
export CSM_BACKUP_DUMP_FILE="<some-platform>-<some-tenant-name>-backup-example.rdb"
```

Replace `<some-platform>` and `<some-tenant-name>` with appropriate values that identify your environment.

#### Step 2: Create a Backup in the Redis Pod

These commands create a backup directory in the Redis pod and copy the current Redis dump file to it:

```bash title="Creating a backup in the Redis pod"
kubectl -n <some-namespace> exec --stdin --tty <some-pod> -- mkdir -p /opt/backups
kubectl -n <some-namespace> exec --stdin --tty <some-pod> -- cp /data/dump.rdb /opt/backups/$CSM_BACKUP_DUMP_FILE
```

Replace:

- `<some-namespace>` with your Kubernetes namespace
- `<some-pod>` with the name of your Redis pod

#### Step 3: Download the Backup File to Your Local Machine

After creating the backup in the pod, download it to your local machine:

```bash title="Downloading the backup file"
kubectl cp <some-namespace>/<some-pod>:/opt/backups/$CSM_BACKUP_DUMP_FILE /data/$CSM_BACKUP_DUMP_FILE
cp /data/$CSM_BACKUP_DUMP_FILE /data/dump.rdb
```

This copies the backup file from the pod to your `/data` directory and creates a copy named `dump.rdb` for easier reference.

## Using a Redis Backup for Local Development

You can run a local Redis instance with your backup data for testing and development purposes.

### Step 1: Pull the Redis Docker Image

First, pull the Cosmotech Redis image and tag it for easier reference:

```bash title="Pulling the Redis Docker image"
docker pull ghcr.io/cosmo-tech/cosmotech-redis:1.0.12
docker tag ghcr.io/cosmo-tech/cosmotech-redis:1.0.12 csm-redis
```

### Step 2: Start a Local Redis Instance with Your Backup Data

Launch a Redis container using your backup data:

```bash title="Starting a local Redis with backup data"
docker run -e REDIS_PASSWORD=$REDIS_PASSWORD -e REDIS_NODES=0 -e REDIS_AOF_ENABLED=no -p 6379:6379 -v /data:/bitnami/redis/data csm-redis
```

This command:

- Uses the environment variable `REDIS_PASSWORD` for authentication
- Disables Redis clustering with `REDIS_NODES=0`
- Disables AOF persistence with `REDIS_AOF_ENABLED=no`
- Maps port 6379 for Redis access
- Mounts your local `/data` directory (containing the dump file) to the container's data directory

Once running, you can connect to this Redis instance using `redis-cli` with the password defined in the `REDIS_PASSWORD` environment variable.

## Restoring a Backup to a Remote Redis Instance

This procedure allows you to restore a backup to a production or staging Redis instance.

### Step 1: Disable Redis Persistence on the Target Instance

First, connect to the Redis master instance and disable the save operation to prevent data corruption during restore:

```bash title="Disabling save on the Redis instance"
kubectl -n <some-namespace> exec --stdin --tty <name-master-redis-instance> -- /bin/bash
redis-cli -a $REDIS_PASSWORD
CONFIG set save ""
exit
exit
```

This sequence:

1. Opens a shell in the Redis master pod
2. Connects to Redis using the CLI
3. Disables the automatic save operation
4. Exits both the Redis CLI and the pod shell

### Step 2: Upload and Apply the Backup File

Copy your local backup file to the Redis master pod and replace the current dump file:

```bash title="Uploading the backup file to the pod"
kubectl cp $PWD/data/$CSM_BACKUP_DUMP_FILE <some-namespace>/<name-master-redis-instance>:/data/dump.rdb-1
kubectl -n <some-namespace> exec --stdin --tty <name-master-redis-instance> -- chmod 777 /data/dump.rdb-1
kubectl -n <some-namespace> exec --stdin --tty <name-master-redis-instance> -- cp /data/dump.rdb-1 /data/dump.rdb
kubectl -n <some-namespace> exec --stdin --tty <name-master-redis-instance> -- rm /data/dump.rdb-1
```

This sequence:

1. Copies your backup file to the pod with a temporary name
2. Sets appropriate permissions on the file
3. Replaces the current dump file with your backup
4. Removes the temporary file

### Step 3: Restart the Pods to Apply Changes

Finally, restart the Redis master pod and the API pod to ensure the changes take effect:

```bash title="Restarting the pods"
kubectl -n <some-namespace> delete pod <name-master-redis-instance>
kubectl -n <some-namespace> delete pod <name-cosmotech-api-instance>
```

This forces Kubernetes to recreate the pods, which will load the new Redis data from your backup file.

## Important Notes

- Always test your backup and restore procedures in a non-production environment first
- Ensure you have sufficient disk space for large Redis databases
- The Redis password should be properly secured and not exposed in scripts
- Consider scheduling regular backups for critical Redis instances
