# Kafka Vehicle Data Simulation - Code Documentation

## 📌 Objective

This Python script simulates a smart city's vehicle journey from London to Birmingham. It generates realistic data for vehicles, GPS, weather, emergency incidents, and traffic cameras, and sends this data to respective Kafka topics.

---

## ⚙️ Configuration

### Environment Variables

```python
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GPS_TOPIC = os.getenv('GPS_TOPIC', 'gps_data')
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_data')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC', 'emergency_data')
```

* These define Kafka connectivity and topic names, defaulting to local settings.

---

## 🗺️ Geographical Setup

```python
LONDON_COORDINATES = {"latitude": 51.5074, "longitude": -0.1278}
BIRMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}
LATITUDE_INCREMENT, LONGITUDE_INCREMENT = ...  # step-wise travel toward Birmingham
```

---

## ⏱️ Time Management

```python
def get_next_time():
    start_time += timedelta(seconds=random.randint(30, 60))
    return start_time
```

* Simulates real-world sensor polling intervals.

---

## 🧪 Data Generation Functions

### 1. Vehicle Data

```python
def generate_vehicle_data(vehicle_id):
```

* Location, speed, direction, make/model, fuel type, etc.

### 2. GPS Data

```python
def generate_gps_data(vehicle_id, timestamp):
```

* Speed, direction, and type.

### 3. Weather Data

```python
def generate_weather_data(vehicle_id, timestamp, location):
```

* Temperature, humidity, air quality, etc.

### 4. Traffic Camera Data

```python
def generate_traffic_camera_data(...):
```

* Camera ID, snapshot placeholder.

### 5. Emergency Data

```python
def generate_emergency_incident_data(...):
```

* Randomized incident types and status.

---

## 🛣️ Vehicle Movement Simulation

```python
def simulate_vehicle_movement():
```

* Increments location with randomness to simulate real-world movement.

---

## 🧬 Kafka Integration

### Kafka Producer Setup

```python
producer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'error_cb': lambda err: print(f'Kafka Error: {err}')
}
producer = SerializingProducer(producer_config)
```

### Serialization Helper

```python
def json_serializer(obj):
    if isinstance(obj, uuid.UUID): return str(obj)
```

* Ensures UUIDs are JSON serializable.

### Delivery Callback

```python
def delivery_report(err, msg):
    print success or failure
```

### Sending to Kafka

```python
def produce_data_to_kafka(producer, topic, data):
```

* Converts data to JSON and publishes to Kafka topic.

---

## 🚗 Journey Simulation

```python
def simulate_journey(producer, vehicle_id):
```

* Main loop that:

  * Simulates vehicle data
  * Sends all generated records to appropriate Kafka topics
  * Stops when destination (Birmingham) is reached

---

## 🧪 Execution Entrypoint

```python
if __name__ == '__main__':
```

* Initializes Kafka producer
* Calls `simulate_journey()`

---

## 🔗 Docker & Kafka Communication

This script will:

* Be run inside a Docker container
* Connect to Kafka (via `KAFKA_BOOTSTRAP_SERVERS`), likely defined in `docker-compose.yaml`

Ensure `confluent-kafka` Python module is installed, and Docker networking allows resolution of `kafka:9092` or `localhost:9092`.

---

## 📤 Output Summary

Each iteration sends:

* 1 vehicle record → `vehicle_data`
* 1 GPS record → `gps_data`
* 1 traffic camera snapshot → `traffic_data`
* 1 weather reading → `weather_data`
* 1 emergency incident (or none) → `emergency_data`

---

