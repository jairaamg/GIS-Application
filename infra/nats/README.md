# NATS JetStream

Streams (initial):

- `DATASET_EVENTS`
- `PROCESSING_EVENTS`
- `LAYER_EVENTS`

Consumers map 1:1 to workers where possible. Exactly-once semantics are not assumed; workers must be idempotent.
