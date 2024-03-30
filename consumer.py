from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer


# Define Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092',  # Adjust to your local Kafka broker
    'group.id': 'group01',                  # Adjust to your consumer group id
    'auto.offset.reset': 'latest'        # Adjust to your desired offset reset policy
}

# Create a Schema Registry client
schema_registry_client = SchemaRegistryClient({
    'url': 'http://localhost:8081'  # Adjust to your local Schema Registry URL
})

# Fetch the latest Avro schema for the value
subject_name = 'retail_data-value'
schema_str = schema_registry_client.get_latest_version(subject_name).schema.schema_str

# Define Avro Deserializer for the value
key_deserializer = StringDeserializer('utf_8')
avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

# Define the DeserializingConsumer
consumer = DeserializingConsumer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'key.deserializer': key_deserializer,
    'value.deserializer': avro_deserializer,
    'group.id': kafka_config['group.id'],
    'auto.offset.reset': kafka_config['auto.offset.reset']
})

# Subscribe to the 'retail_data' topic
consumer.subscribe(['retail_data'])

#Continually read messages from Kafka
try:
    while True:
        msg = consumer.poll(1.0) # How many seconds to wait for message

        if msg is None:
            continue
        if msg.error():
            print('Consumer error: {}'.format(msg.error()))
            continue

        print('Successfully consumed record with key {} and value {}'.format(msg.key(), msg.value()))

except KeyboardInterrupt:
    pass
finally:
    consumer.close()