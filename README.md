# FlashShield 🛡️
> Ultra-Resilient Flash-Traffic Result Delivery Platform & Circuit Breaker

FlashShield is an SRE and cloud-native resilience platform built to solve the **"result-day thundering herd"** problem commonly faced by educational institutions. When thousands of students reload result portals simultaneously, traditional database architectures experience connection starvation and catastrophic failure.

FlashShield mitigates flash crowds using a multi-tiered defense: edge rate limiting, Kubernetes Horizontal Pod Autoscaling (HPA), Redis pre-warming, and graceful circuit breaking (virtual waiting room).

---

## 🏗️ Architecture

```text
[ Students / Browser ]         [ SRE Operations Dashboard ]
           │                                 │
           │                                 ├──► [ Trigger Traffic Burst ]
           ▼                                 └──► [ Live Metrics Polling ]
 [ Ingress-NGINX Controller ]
     ├── Rate Limiter (30 RPS / burst multiplier)
     └── Circuit Breaker (Static 429 Waiting Room Page)
           │
           ▼
 [ Kubernetes Cluster ]
   ├── HPA (Autoscaling 2 ──► 10 Pods on CPU/traffic)
   └── API Pods (FastAPI)
         ├── Fast In-Memory Path: Redis Pre-warmed Cache (<2ms)
         └── Cold Fallback: PostgreSQL via PgBouncer
