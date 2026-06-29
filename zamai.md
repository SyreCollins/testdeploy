# ROLE

You are a Staff AI Engineer, Software Architect, and Technical Writer with experience building production-grade healthcare AI systems.

You have just joined a startup called Zamda Health as the founding AI engineer.

Your first responsibility is NOT writing code.

Your first responsibility is designing the entire Zam AI platform so that any engineer joining the company can understand exactly what needs to be built.

You are expected to think like a CTO and senior AI architect.

Do not make assumptions without explaining them.

Whenever multiple architectural approaches exist, choose the one that is the most scalable, modular, maintainable, and safest for a medical AI product.

This documentation should feel like something produced by OpenAI, Anthropic, Google DeepMind, or Microsoft.

It should be extremely detailed.

Do not optimize for brevity.

Think deeply before writing.

---------------------------------------------------------

# PROJECT CONTEXT

Zam AI is an AI-powered medical intelligence platform being built by Zamda Health.

The platform serves four major user groups.

1. Patients
2. Pharmacies
3. Doctors
4. Third-party health companies through APIs

Its responsibilities include

• Symptom checking
• Medication guidance
• Drug information
• Drug interaction checking
• Contraindication detection
• Dosage verification
• Prescription explanation
• Prescription OCR
• Medication reminders
• Personalized health recommendations
• Pharmacy intelligence
• Clinical decision support
• Predictive analytics
• Public API

The company has one absolute rule:

NO MEDICAL RESPONSE SHOULD EVER COME FROM THE LLM'S INTERNAL KNOWLEDGE.

Every medical answer must be grounded using Retrieval-Augmented Generation (RAG) from verified medical sources.

Hallucination prevention is the highest priority.

---------------------------------------------------------

# EXISTING MEDICAL SOURCES

The system will eventually integrate with

• NAFDAC
• EMDEX
• BNF
• MIMS
• WHO ATC
• Nigeria Essential Medicines List
• Internal Pharmacy Inventory
• Prescription History
• Patient Health Records

---------------------------------------------------------

# EXPECTED TECHNOLOGY

Backend:
FastAPI

Python

Supabase

Google Cloud Run

Docker

Redis

Postgres

LLMs:
Claude / Gemini (design should allow swapping providers)

Vector Database:
Recommend the best option and explain why.

Embeddings:
Recommend the best option and explain why.

OCR:
Recommend the best architecture.

Monitoring:
Recommend production-grade tooling.

---------------------------------------------------------

# YOUR TASK

Design the ENTIRE engineering documentation for the project.

This is NOT code generation.

This is system design.

Think like the CTO creating documentation before development starts.

Generate the documentation as multiple markdown files.

---------------------------------------------------------

# REQUIRED OUTPUT STRUCTURE

Create the following files.

docs/

00_PROJECT_HANDOFF.md

01_PRODUCT_REQUIREMENTS.md

02_SYSTEM_ARCHITECTURE.md

03_AI_ARCHITECTURE.md

04_RAG_ARCHITECTURE.md

05_DATABASE_DESIGN.md

06_API_SPECIFICATION.md

07_SECURITY_AND_COMPLIANCE.md

08_AI_EVALUATION.md

09_DEPLOYMENT_ARCHITECTURE.md

10_ENGINEERING_GUIDELINES.md

11_ROADMAP.md

12_DECISION_LOG.md

README.md

Each document should be extremely detailed.

---------------------------------------------------------

# README.md

Describe

Project vision

Architecture overview

Folder structure

Technology stack

How the documentation is organized

Development philosophy

---------------------------------------------------------

# 00_PROJECT_HANDOFF.md

This should become the single source of truth for project status.

Include

Current project state

Current milestone

Completed work

In-progress work

Upcoming work

Architecture decisions

Current risks

Known blockers

Technical debt

Database status

Infrastructure status

API status

AI status

Deployment status

Evaluation status

Open questions

Engineering notes

Decision history

This document should be updated throughout the project.

---------------------------------------------------------

# 01_PRODUCT_REQUIREMENTS.md

Write a complete PRD.

Include

Vision

Mission

Goals

Non-goals

User personas

Business objectives

Functional requirements

Non-functional requirements

Performance targets

Latency targets

Security requirements

Medical safety requirements

Success metrics

Acceptance criteria

Risks

Future roadmap

---------------------------------------------------------

# 02_SYSTEM_ARCHITECTURE.md

Design the complete backend architecture.

Include

System diagrams (Mermaid)

Service boundaries

Microservices vs Modular Monolith discussion

API Gateway

Authentication

Background workers

Queues

Caching

Databases

Storage

Monitoring

Deployment

Logging

Observability

Secrets management

CI/CD

---------------------------------------------------------

# 03_AI_ARCHITECTURE.md

This should be extremely detailed.

Design every AI component.

Include

Conversation orchestrator

Intent classifier

Tool calling

Memory

Prompt management

Context builder

Safety layer

Citation engine

Confidence scoring

Response generation

Language detection

Translation

Patient personalization

Doctor assistant

Pharmacy assistant

Voice architecture

Future predictive AI

Show how every AI component communicates.

Include diagrams.

---------------------------------------------------------

# 04_RAG_ARCHITECTURE.md

Design an enterprise-grade medical RAG pipeline.

Cover

Document ingestion

Normalization

Chunking

Metadata

Embeddings

Vector database

Hybrid retrieval

Query rewriting

Re-ranking

Citation generation

Grounding verification

Hallucination prevention

Prompt construction

Context compression

Evaluation

Update pipelines

Medical source versioning

---------------------------------------------------------

# 05_DATABASE_DESIGN.md

Design every table.

Patients

Doctors

Pharmacies

Conversations

Messages

Documents

Embeddings

Prescriptions

Medications

Drug interactions

Reminder schedules

Appointments

API keys

Audit logs

Evaluations

Feature flags

Everything.

Explain relationships.

---------------------------------------------------------

# 06_API_SPECIFICATION.md

Design every endpoint.

Patient APIs

Doctor APIs

Pharmacy APIs

Partner APIs

Authentication

Streaming

Error handling

Versioning

JSON schemas

---------------------------------------------------------

# 07_SECURITY_AND_COMPLIANCE.md

Design security.

NDPA compliance

Encryption

RLS

Least privilege

PII handling

Prompt injection protection

Rate limiting

Audit logging

Medical disclaimers

Consent

Threat model

---------------------------------------------------------

# 08_AI_EVALUATION.md

Design a full evaluation framework.

Groundedness

Faithfulness

Citation accuracy

Medical correctness

Hallucination rate

Latency

Cost

Safety

Prompt injection

Regression testing

Golden datasets

Continuous evaluation

Human review

---------------------------------------------------------

# 09_DEPLOYMENT_ARCHITECTURE.md

Design production infrastructure.

Google Cloud Run

Docker

Redis

Supabase

CDN

Load balancing

Autoscaling

Monitoring

Tracing

Logging

Disaster recovery

---------------------------------------------------------

# 10_ENGINEERING_GUIDELINES.md

Coding standards

Folder conventions

Naming

Dependency injection

Testing strategy

Documentation standards

Git workflow

Branch strategy

PR reviews

Feature flags

---------------------------------------------------------

# 11_ROADMAP.md

Instead of organizing by user type, organize by engineering dependencies.

Phase 0

Project setup

CI/CD

Infrastructure

Docker

Secrets

Monitoring

Phase 1

Medical knowledge platform

ETL

Normalization

Embeddings

Vector DB

Retriever

Citation system

Phase 2

AI Core

Conversation engine

Intent detection

Prompting

Safety

Tool calling

Memory

Phase 3

Patient MVP

Symptom checker

Drug information

Medication Q&A

Emergency triage

Phase 4

Prescription Intelligence

OCR

Parsing

Interaction checking

Dosage validation

Medication explanation

Phase 5

Patient Personalization

Profiles

Reminders

Health summaries

Risk scoring

Phase 6

Doctor & Pharmacy

Clinical decision support

Inventory intelligence

Alternative medications

Consultation assistant

Phase 7

Advanced AI

Voice

Multilingual

Predictive analytics

Outbreak detection

Demand forecasting

Drug repurposing

Phase 8

Public SaaS Platform

API

Billing

Usage

Developer portal

Load testing

Production hardening

Each phase should include

Objectives

Deliverables

Dependencies

Acceptance criteria

Testing requirements

Risks

---------------------------------------------------------

# 12_DECISION_LOG.md

Track all architectural decisions.

Every decision should include

Problem

Alternatives

Chosen solution

Reasoning

Tradeoffs

Future implications

---------------------------------------------------------

# ADDITIONAL REQUIREMENTS

Whenever architecture is discussed:

Explain WHY.

Discuss alternatives.

Mention tradeoffs.

Use Mermaid diagrams extensively.

Design for future scalability.

Assume millions of users.

Design for production.

Never optimize for shortcuts.

---------------------------------------------------------

# FINAL REQUIREMENT

This should read like internal engineering documentation from a world-class AI company.

It should be detailed enough that a new engineer could implement the platform using only these documents.

Do not skip details.

Do not summarize.

Err on the side of over-documenting every architectural decision.