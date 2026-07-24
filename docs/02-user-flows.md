# User Flows

This document describes the lifecycle of users, organizations, projects, memberships, and API keys.

---

# Signup Flow

When a new user signs up:

```mermaid
flowchart LR

    A[User Signs Up]

    A --> B[Create User]

    B --> C[Create Personal Organization]

    C --> D[Assign Owner Role]

    D --> E[Create Default Project]

    E --> F[Dashboard Ready]
```

Result:

```
User
└── Personal Organization
      └── Default Project
```

---

# Personal Organization

Every account receives:

- Personal Organization
- Owner role
- Default Project

The Personal Organization behaves exactly like a Team Organization.

The only difference is that it starts with one member.

---

# Creating a Team Organization

```mermaid
flowchart LR

    Dashboard --> CreateOrg[Create Organization]

    CreateOrg --> Configure[Configure Organization]

    Configure --> Invite[Invite Members]

    Invite --> Ready[Organization Ready]
```

---

# Member Invitation Flow

```mermaid
flowchart LR

    OWNER[Organization Owner]

    OWNER --> INVITE[Invite User]

    INVITE --> EMAIL[Invitation Email]

    EMAIL --> ACCEPT[Accept Invitation]

    ACCEPT --> MEMBER[Membership Created]

    MEMBER --> ACCESS[Access Organization]
```

---

# Project Lifecycle

```mermaid
flowchart LR

    Organization

    --> Project

    --> APIKey

    --> AIRequests

    --> Usage

    --> Billing
```

---

# API Key Lifecycle

```mermaid
flowchart TD

    Create[Create API Key]

    --> Active[Active]

    --> Rotate[Rotate]

    --> Revoke[Revoke]

    --> Archived[Archived]
```

---

# AI Request Flow

```mermaid
flowchart LR

    Client

    --> APIKey

    --> Gateway

    --> Authentication

    --> RateLimit

    --> Router

    --> Provider

    --> Response

    --> Usage

    --> Billing
```

---

# Complete Platform Flow

```mermaid
flowchart TD

    Signup

    --> PersonalOrg

    --> DefaultProject

    --> Dashboard

    Dashboard --> CreateTeamOrg

    CreateTeamOrg --> InviteMembers

    InviteMembers --> CreateProjects

    CreateProjects --> GenerateAPIKeys

    GenerateAPIKeys --> MakeAIRequests

    MakeAIRequests --> UsageTracking

    UsageTracking --> Billing

    UsageTracking --> Logs
```

---

# Permission Model

```text
Owner
├── Full Access

Admin
├── Manage Members
├── Manage Projects
├── Manage API Keys

Developer
├── Create API Keys
├── View Logs
├── Make Requests

Viewer
├── View Usage
├── View Logs
```

---

# Summary

Platform
└── Users
    └── Memberships
        └── Organizations
            ├── Members
            ├── Projects
            │   ├── API Keys
            │   ├── Usage
            │   ├── Logs
            │   ├── Limits
            │   └── Secrets
            ├── Billing
            └── Settings