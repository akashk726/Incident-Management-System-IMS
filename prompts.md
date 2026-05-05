# Prompts Used During Development

This document captures the prompts used during the design and development of the Incident Management System (IMS). These prompts were used to explore system design decisions, implementation approaches, and best practices.

---

## 1. System Design & Architecture

**Prompt:**
Design a scalable Incident Management System capable of handling high-throughput signals (10,000+ signals/sec) with asynchronous processing, debouncing, and workflow management.

**Outcome:**

* Adopted Producer-Consumer architecture
* Introduced async queue for decoupling ingestion and processing
* Designed layered system: ingestion → queue → worker → storage → UI

---

**Prompt:**
What architecture should be used to handle burst traffic in distributed systems without crashing?

**Outcome:**

* Implemented bounded queue (asyncio.Queue)
* Added backpressure handling (503 when queue full)
* Introduced rate limiting

---

## 2. Backend Design (FastAPI + Async)

**Prompt:**
How to design a non-blocking API using FastAPI for high-throughput ingestion?

**Outcome:**

* Used FastAPI with async endpoints
* Implemented non-blocking queue insertion
* Ensured ingestion remains fast under load

---

**Prompt:**
How to implement async worker processing using Python asyncio?

**Outcome:**

* Created background worker loop
* Used asyncio.Queue for communication
* Enabled concurrent signal processing

---

## 3. Concurrency & Race Conditions

**Prompt:**
How to handle race conditions when multiple signals update the same resource?

**Outcome:**

* Implemented per-component locks
* Ensured thread-safe updates for incidents
* Prevented duplicate incident creation

---

## 4. Debouncing & Signal Aggregation

**Prompt:**
How to prevent duplicate incidents when multiple signals arrive for the same component?

**Outcome:**

* Used component-based aggregation
* Checked for existing OPEN incident
* Incremented signal count instead of creating new incident

---

**Prompt:**
What is the difference between time-based debouncing and state-based aggregation?

**Outcome:**

* Chose state-based aggregation (simpler and effective)
* Avoided strict time-window complexity

---

## 5. Database Design & Persistence

**Prompt:**
What is the simplest reliable database choice for a small-scale system?

**Outcome:**

* Selected SQLite for simplicity and zero setup
* Designed schema for incidents, RCA, and MTTR

---

**Prompt:**
How to handle database write failures in production systems?

**Outcome:**

* Implemented retry queue
* Created background retry worker
* Ensured no data loss during transient failures

---

## 6. Retry & Resilience

**Prompt:**
How to design retry mechanisms for failed operations in distributed systems?

**Outcome:**

* Added retry queue (deque-based)
* Background retry worker executes failed operations
* Retry with delay (2 seconds)

---

## 7. Rate Limiting & Backpressure

**Prompt:**
How to implement rate limiting in a REST API?

**Outcome:**

* Used sliding window approach
* Limited ingestion to 200 requests/sec

---

**Prompt:**
How to handle backpressure in high-throughput systems?

**Outcome:**

* Used bounded queue
* Returned 503 when queue is full
* Prevented system overload

---

## 8. Incident Workflow & RCA

**Prompt:**
How to enforce mandatory fields before closing an incident?

**Outcome:**

* Implemented validation for RCA fields
* Prevented closure without complete RCA

---

**Prompt:**
How to calculate MTTR in incident management systems?

**Outcome:**

* MTTR = end_time - start_time
* Calculated during incident closure
* Stored in database

---

## 9. Frontend Design (React)

**Prompt:**
How to design a simple dashboard for real-time incident monitoring?

**Outcome:**

* Created dashboard with cards for incidents
* Displayed severity, status, and signal count
* Implemented navigation to detail view

---

**Prompt:**
How to implement auto-refresh in React without WebSockets?

**Outcome:**

* Used polling (setInterval every 5 seconds)
* Updated incident list dynamically

---

**Prompt:**
How to build a form for structured RCA submission?

**Outcome:**

* Created form with required fields
* Connected to backend API
* Displayed response and MTTR

---

## 10. UI/UX Improvements

**Prompt:**
How to improve usability of dashboards with multiple data points?

**Outcome:**

* Added filtering (severity, status)
* Implemented search functionality
* Added KPI cards (Total, Open, Closed)

---

## 11. Observability

**Prompt:**
What are basic observability features required in backend systems?

**Outcome:**

* Implemented /health endpoint
* Added queue size monitoring
* Logged signal throughput

---

## 12. Docker & Deployment

**Prompt:**
How to containerize a full-stack application using Docker?

**Outcome:**

* Created Dockerfile for backend and frontend
* Used docker-compose for orchestration
* Enabled single-command startup

---

## 13. Testing & Validation

**Prompt:**
How to simulate load testing for API endpoints?

**Outcome:**

* Created test_load.py script
* Sent multiple signals to ingestion API
* Verified system stability under load

---

## 14. Trade-offs & Design Choices

**Prompt:**
What are trade-offs of using SQLite vs PostgreSQL?

**Outcome:**

* SQLite chosen for simplicity
* Acknowledged scalability limitations
* Suggested PostgreSQL for future

---

**Prompt:**
Should WebSockets be used instead of polling?

**Outcome:**

* Used polling for simplicity
* Identified WebSockets as future improvement

---

## 15. Learning & Iteration

**Prompt:**
How to structure a production-like backend system with limited resources?

**Outcome:**

* Focused on core features
* Prioritized reliability over complexity
* Simulated distributed system concepts locally

---

# Summary

The use of these prompts helped in:

* Designing a scalable system architecture
* Implementing asynchronous processing
* Ensuring system resilience and fault tolerance
* Building a clean and functional user interface

This approach enabled rapid development while maintaining a strong focus on engineering best practices.

---
