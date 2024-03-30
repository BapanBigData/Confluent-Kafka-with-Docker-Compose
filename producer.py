from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
import pandas as pd
import time


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """
    if err is not None:
        print("Delivery failed for record {}: {}".format(msg.key(), err))
        return
    
    print('Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))
    
    return

# Define Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092'     # Adjust to your local Kafka broker
}

# Create a Schema Registry client
schema_registry_client = SchemaRegistryClient({
    'url': 'http://localhost:8081'           # Adjust to your local Schema Registry URL
})

# Fetch the latest Avro schema for the value
subject_name = 'retail_data-value'
schema_str = schema_registry_client.get_latest_version(subject_name).schema.schema_str

# Create Avro Serializer for the value
key_serializer = StringSerializer('utf_8')
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

# Define the SerializingProducer
producer = SerializingProducer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'key.serializer': key_serializer,      # Key will be serialized as a string
    'value.serializer': avro_serializer    # Value will be serialized as Avro
})


# Load the CSV data into a pandas DataFrame
df = pd.read_csv('retail_data.csv')
df = df.fillna('null')

# Iterate over DataFrame rows and produce to Kafka
for index, row in df.iterrows():
    # Create a dictionary from the row values
    value = row.to_dict()
    # Produce to Kafka
    producer.produce(topic='retail_data', key=str(index), value=value, on_delivery=delivery_report)
    producer.flush()
    #break
    
    time.sleep(1)

print("All Data successfully published to Kafka!")