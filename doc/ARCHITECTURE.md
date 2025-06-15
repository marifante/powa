# Power Warden application architecture

Powa daemon is composed by:

- a time-series database client, which takes data from a queue and sends it to a time-series database server.
- a power-domain controller, which can manage several power domains. The power-domain controller pushes data to a queue.

```mermaid
erDiagram


    POWA-DAEMON ||--|| TIME-SERIES-CLIENT: have
    POWA-DAEMON ||--|| POWER-DOMAIN-CONTROLLER : have

    POWER-DOMAIN-CONTROLLER ||--|| QUEUE: push_power_domain_data
    TIME-SERIES-CLIENT ||--|| QUEUE: pops_power_domain_data

    TIME-SERIES-CLIENT }|--|| TIME-SERIES-DATABASE-SERVER: send_data

    TIME-SERIES-CLIENT {
        string database_connection
    }

    POWA-DAEMON {
        int pid
    }

    TIME-SERIES-DATABASE-SERVER {
        int pid
    }

    POWER-DOMAIN-CONTROLLER {
        list power_domains
    }

    POWER-DOMAIN-CONTROLLER ||--o{ POWER-DOMAIN : manage

    POWER-DOMAIN {
        string name
        bool power_state
        bool alarm_active
        float current_limit

    }
```
