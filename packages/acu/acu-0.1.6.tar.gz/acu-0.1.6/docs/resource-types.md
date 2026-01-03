# ACU Resource Types (Draft)

This document lists common resource types and suggested default properties. Enforce the allowed set
and defaults in the validation layer.

## Shared Fields

- `id` (string/int): unique across the infra
- `name` (string): human-friendly name
- `type` (enum): one of the types below
- `labels` (map[string]string): optional metadata
- `properties` (object): type-specific configuration

## Types and Suggested Defaults

### `artifact_repo`

Repository for build artifacts (binaries, charts, bundles).

- retention_days: 30
- immutability: true
- replication: none

### `autoscaling_group`

Group of compute instances that scale automatically.

- min_size: 1
- max_size: 5
- desired_size: 2
- metric: cpu
- scale_in_cooldown: 300s
- scale_out_cooldown: 300s

### `batch_job`

One-off or scheduled batch workload.

- runtime: python3.14
- cpu: 1
- memory: 512Mi
- retries: 3
- timeout: 900s

### `bucket`

Object storage for blobs, files, or artifacts.

- versioning: false
- encryption: provider-default

### `cache`

Ephemeral low-latency key-value store for speeding up reads.

- engine: redis
- memory: 1Gi
- replicas: 1

### `cdn`

Content delivery network edge distribution for static/media assets.

- provider: generic
- caching: true
- ttl: 300s
- tls: true

### `certificate`

TLS/SSL certificate for domains or services.

- managed: true
- key_type: rsa2048
- renewal: auto

### `cluster`

Group of nodes that schedule and run workloads together.

- nodes: 3
- cpu_per_node: 2
- memory_per_node: 4Gi
- network: default
- autoscale: false

### `container_service`

Containerized service managed by a scheduler/orchestrator.

- image: REQUIRED
- replicas: 2
- ports: [80]
- cpu: 0.5
- memory: 512Mi
- strategy: rolling

### `database`

Managed or self-hosted database instance (SQL/NoSQL generic).

- engine: generic (resolved per provider: postgres/mysql/mongo/...)
- storage: 20Gi
- replicas: 1

### `dns_record`

DNS record mapping names to targets.

- record_type: A
- ttl: 300s
- value: REQUIRED

### `file_share`

Network file share for multi-host consumption.

- protocol: nfs
- size: 100Gi
- encrypted: true

### `firewall_rule`

Allow/deny rule for network access.

- action: allow
- protocol: tcp
- ports: [80]
- source: 0.0.0.0/0
- description: ""

### `function`

Serverless function for short-lived event-driven compute.

- runtime: python3.14
- memory: 256Mi
- timeout: 30s

### `gateway`

API or network gateway entrypoint.

- protocol: http
- tls: true
- auth: none
- rate_limit: null

### `iam_role`

Identity/role with permissions and trust policy.

- assumed_by: []
- permissions: []
- managed: true

### `kms_key`

Managed encryption key entry.

- key_type: symmetric
- rotation_days: 365
- deletion_window_days: 30

### `load_balancer`

Distributes traffic across upstream services.

- ports: [80]
- protocol: http
- strategy: round_robin

### `log_sink`

Log destination/collector (bucket, lake, logging service).

- target: REQUIRED
- format: json
- retention_days: 30

### `metric_alarm`

Threshold alarm on a metric.

- metric: REQUIRED
- threshold: REQUIRED
- comparison: ">="
- period: 60s
- evaluation_periods: 1

### `network`

Virtual network boundary for addressing and routing.

- cidr: 10.0.0.0/16
- subnets: []

### `proxy`

Forward/egress or reverse proxy for routing and policy enforcement.

- mode: reverse
- protocol: http
- tls: true
- auth: none
- rate_limit: null

### `queue`

Message queue or pub/sub endpoint for async workloads.

- kind: generic (resolved per provider: rabbitmq/sqs/pubsub/...)
- throughput: 100

### `registry`

Container/image registry.

- visibility: private
- retention_days: 30
- vulnerability_scanning: true

### `scheduler`

Cron/periodic trigger for jobs or functions.

- schedule: "0 0 \* \* \*"
- timezone: UTC
- retries: 3
- concurrency: 1

### `secret`

Secure storage for credentials, keys, or tokens.

- managed: true

### `server`

Compute instance (VM/container host) for general workloads.

- cpu: 2
- memory: 4Gi
- image: REQUIRED
- replicas: 1

### `serverless`

Fully managed runtime for event-driven code without servers.

- runtime: python3.14
- memory: 256Mi
- timeout: 30s
- concurrency: 10

### `service`

Logical service grouping (often a deployable app/API).

- replicas: 1
- ports: []

### `storage`

Block or persistent volume storage for stateful workloads.

- size: 20Gi
- class: standard

### `subnet`

Subnet carved from a parent network.

- cidr: 10.0.1.0/24
- availability_zone: a
- public: false
- network: default

## Connections (kinds)

Allowed: `forwards`, `consumes`, `publishes`, `reads`, `writes`, `depends_on`, `connects_to`,
`calls`.

## Scopes (optional)

Group resources under a scope with:

- id (string)
- members (list of resource ids)
- purpose (string)
