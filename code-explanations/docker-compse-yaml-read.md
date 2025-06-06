# 📘 Understanding `docker-compose.yml`: A Complete Guide with Example

---

## 🔧 What is `docker-compose.yml`?

The `docker-compose.yml` file is a **configuration file** used by **Docker Compose**, a tool for defining and running multi-container Docker applications. Instead of running individual `docker run` commands for each service, `docker-compose.yml` lets you define and manage all services, networks, and volumes in one place.

---

## 🚀 Why Do We Need `docker-compose.yml`?

* **Simplified orchestration**: Manage multiple containers with a single command (`docker-compose up`).
* **Version control**: Your environment setup becomes code.
* **Portability**: Share `docker-compose.yml` to reproduce the environment.
* **Consistency**: Ensures all developers and servers use the same container configurations.

---

## 📋 Steps to Build a `docker-compose.yml` File

1. **Identify your services** (e.g., web app, database, message broker).
2. **Choose container images** (e.g., `mysql`, `nginx`, `spark`).
3. **Define networks** if services need to talk to each other.
4. **Mount volumes** for persistence or code sharing.
5. **Set environment variables**.
6. **Expose ports** to the host.

---

## 🧪 Real Project Example: Streaming + Spark Processing

This example sets up a real-time data processing pipeline using Kafka, ZooKeeper, and Spark.

```yaml
version: '3.8'
```

* Specifies the Docker Compose file format version (3.8 supports latest features).

---

### 🧱 Reusable Config Block: `x-spark-common`

```yaml
x-spark-common: &spark-common
  image: bitnami/spark:latest
  volumes:
    - ./jobs:/opt/bitnami/spark/jobs
    - ./spark_ivy_cache_data:/tmp/.ivy2_cache
    - ./conf/core-site.xml:/opt/bitnami/spark/conf/core-site.xml
  command: bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
  depends_on:
    - spark-master
  environment:
    SPARK_MODE: Worker
    SPARK_WORKER_CORES: 2
    SPARK_WORKER_MEMORY: 1g
    SPARK_MASTER_URL: spark://spark-master:7077
    HADOOP_USER_NAME: spark
    HOME: /tmp
    USER: spark
    SPARK_DRIVER_JAVA_OPTIONS: "-Duser.name=spark -Dhadoop.security.authentication=simple"
    SPARK_EXECUTOR_JAVA_OPTIONS: "-Duser.name=spark -Dhadoop.security.authentication=simple"
  networks:
    - datamasterylab
```

* **YAML Anchor** to reuse this Spark Worker config for multiple workers.

---

### 🧩 Services Explained

#### 1. Zookeeper

```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:7.4.0
  ports: ["2181:2181"]
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
    ZOOKEEPER_TICK_TIME: 2000
```

* Coordinates Kafka broker clusters.
* Required by Kafka for leader election and metadata management.

#### 2. Kafka Broker

```yaml
broker:
  image: confluentinc/cp-server:7.4.0
  ports:
    - "9092:9092"     # Host access
    - "9101:9101"     # JMX Monitoring
  environment:
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
```

* Kafka message broker for streaming.
* Talks to Zookeeper.
* Advertises two listeners: one for Docker internal network, one for host.

#### 3. Spark Master

```yaml
spark-master:
  image: bitnami/spark:latest
  ports:
    - "9090:8080"   # Spark UI
    - "7077:7077"   # Spark cluster communication
  command: bin/spark-class org.apache.spark.deploy.master.Master
```

* Central controller for Spark cluster.
* Assigns tasks to workers.

#### 4. Spark Workers (2)

```yaml
spark-worker-1:
  <<: *spark-common

spark-worker-2:
  <<: *spark-common
```

* Execute tasks from Spark Master.
* Use the config from `x-spark-common`.

---

## 🔗 Network Configuration

```yaml
networks:
  datamasterylab:
```

* All containers are on the same custom bridge network.
* Enables name-based resolution (e.g., `broker`, `spark-master`).

You can rename `datamasterylab` to anything.

---

## 📞 Communication & Docker Internals

### How does this code communicate with Docker?

* Docker Compose CLI parses `docker-compose.yml`.
* It uses **Docker Engine API** to:

  * Pull images
  * Create and run containers
  * Set up networks and volumes

### Inter-container Communication

* Services use the Docker-defined network (`datamasterylab`).
* They refer to each other using container names (e.g., `broker:29092`).
* Kafka talks to Zookeeper on port 2181.
* Spark workers register with master at `spark://spark-master:7077`.

---

## ✅ Benefits

* No need for complex scripts.
* Easy to start/stop with `docker-compose up/down`.
* Scales easily (e.g., add more Spark workers).

---

## 📌 Common Commands

```bash
# Start all services
$ docker-compose up -d

# View logs
$ docker-compose logs -f spark-master

# Stop all services
$ docker-compose down

# Rebuild containers
$ docker-compose build
```

---

## 🧠 Conclusion

The `docker-compose.yml` file is the backbone of your multi-container setup. For data engineering projects involving Kafka, Spark, and real-time processing, it provides a consistent, declarative, and reproducible environment. By mastering this file, you gain full control over orchestration, scaling, and deployment of complex data systems.
