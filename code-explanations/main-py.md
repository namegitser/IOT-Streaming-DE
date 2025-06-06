# Kafka Data Simulation & Producer Script Documentation

---

## 📌 Overview
This Python script simulates the journey of a vehicle from **London** to **Birmingham**, generating synthetic smart city data in real time and producing it to Apache Kafka topics using the `confluent_kafka.SerializingProducer`.

---

## 📁 Structure of the Code

### 🔧 1. **Configuration Section**
```python
LONDON_COORDINATES = {"latitude": 51.5074, "longitude": -0.1278}
BIRMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}
LATITUDE_INCREMENT = ...
LONGITUDE_INCREMENT = ...
```
- These define start and end coordinates.
- Increments simulate stepwise travel from London to Birmingham in 100 steps.

```python
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GPS_TOPIC = os.getenv('GPS_TOPIC', 'gps_data')
... (other topics)
```
- Use environment variables to configure Kafka connection and topic names.

---

### 🚙 2. **Time & Location Utilities**
```python
def get_next_time():
```
- Increments global time by a random interval between 30-60 seconds.

```python
def simulate_vehicle_movement():
```
- Adds incremental + random changes to simulate real-world vehicle movement.

---

### 🧪 3. **Data Generators**
These functions synthesize data based on simulated inputs:

#### 🚗 Vehicle Data
```python
def generate_vehicle_data(vehicle_id):
```
- Make, model, speed, coordinates, etc.

#### 🛰️ GPS Data
```python
def generate_gps_data(vehicle_id, timestamp):
```
- Speed, direction, vehicle type.

#### 🌦️ Weather Data
```python
def generate_weather_data(vehicle_id, timestamp, location):
```
- Temperature, humidity, air quality, etc.

#### 🚨 Emergency Data
```python
def generate_emergency_incident_data(...):
```
- Type of emergency, status, description.

#### 📷 Traffic Camera Data
```python
def generate_traffic_camera_data(...):
```
- Captures vehicle via smart camera with mock snapshot.

---

### 🧾 4. **Kafka Utilities**

#### ✅ JSON Serializer
```python
def json_serializer(obj):
```
- Converts UUIDs into strings for JSON compatibility.

#### 📬 Delivery Callback
```python
def delivery_report(err, msg):
```
- Callback function to print delivery results of Kafka messages.

#### 🚀 Data Producer
```python
def produce_data_to_kafka(producer, topic, data):
```
- Serializes and sends messages to Kafka.

---

### 🔁 5. **Main Journey Loop**
```python
def simulate_journey(producer, vehicle_id):
```
- Generates and sends all 5 types of data for each step.
- Stops once the simulated vehicle reaches Birmingham.
- Delays for 5 seconds between steps.

---

## 🧵 Program Execution

```python
if __name__ == '__main__':
    producer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'error_cb': lambda err: print(f'Kafka Error: {err}')
    }

    producer = SerializingProducer(producer_config)
    simulate_journey(producer, 'Vehicle-Project-111')
```
- The script is launched with default or injected Kafka configurations.
- It creates a producer and starts the simulation with a unique vehicle ID.

---

## 📡 Kafka Communication Flow

1. **Producer Setup:** The script initializes `SerializingProducer` using the broker address (`localhost:9092` or Docker hostname `broker:29092`).
2. **Message Sending:** Serialized JSON payloads are pushed to Kafka topics.
3. **Delivery Confirmation:** A callback confirms successful message delivery.
4. **Kafka Topics:** 
   - `vehicle_data`
   - `gps_data`
   - `traffic_data`
   - `weather_data`
   - `emergency_data`

---

## 🐳 Integration with Docker Compose
When used with Docker Compose:
- The Python container uses Docker's internal network (e.g., `broker:29092`) to reach Kafka.
- The environment variables (`KAFKA_BOOTSTRAP_SERVERS`, etc.) are injected via the Compose file.

Example Docker service:
```yaml
kafka-simulator:
  build: .
  environment:
    - KAFKA_BOOTSTRAP_SERVERS=broker:29092
    - VEHICLE_TOPIC=vehicle_data
    - GPS_TOPIC=gps_data
  depends_on:
    - broker
```

---

## ✅ Summary
This simulation creates a realistic stream of smart city IoT data for testing Kafka-based data pipelines. It supports modular configuration, runs continuously, and simulates a journey with diversified data formats.


