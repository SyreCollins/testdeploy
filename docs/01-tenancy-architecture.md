# Tenancy & Ownership Architecture

## Overview

The platform is built around a multi-tenant architecture.

The Organization is the primary ownership boundary.

Every resource in the system belongs to an Organization, either directly or through a Project.

```
User
└── Membership
    └── Organization
        ├── Members
        ├── Projects
        ├── Billing
        └── Settings
```

---

# Core Hierarchy

```mermaid
flowchart TD

    USER[User]

    USER --> MEMBERSHIP[Organization Membership]

    MEMBERSHIP --> ORG[Organization]

    ORG --> MEMBERS[Members]
    ORG --> BILLING[Billing]
    ORG --> SETTINGS[Settings]
    ORG --> AUDIT[Audit Logs]

    ORG --> PROJECT[Projects]

    PROJECT --> APIKEY[API Keys]
    PROJECT --> LOGS[Request Logs]
    PROJECT --> USAGE[Usage Metrics]
    PROJECT --> LIMITS[Rate Limits]
    PROJECT --> SECRETS[Secrets]
    PROJECT --> WEBHOOKS[Webhooks]
```

---

# Organization Structure

```mermaid
flowchart TD

    ORG[Organization]

    ORG --> MEMBERS[Members]

    MEMBERS --> OWNER[Owner]
    MEMBERS --> ADMIN[Admin]
    MEMBERS --> DEVELOPER[Developer]
    MEMBERS --> VIEWER[Viewer]

    ORG --> PROJECTS[Projects]

    PROJECTS --> PROD[Production]
    PROJECTS --> DEV[Development]
    PROJECTS --> STAGING[Staging]
```

---

# Complete Ownership Model

```mermaid
flowchart TD

    USER[User]

    USER --> MEMBERSHIP[Membership]

    MEMBERSHIP --> ORG[Organization]

    ORG --> PROJECT[Project]

    PROJECT --> APIKEY[API Key]

    APIKEY --> REQUEST[AI Request]

    REQUEST --> ROUTER[Routing Engine]

    ROUTER --> OPENAI[OpenAI]
    ROUTER --> CLAUDE[Anthropic]
    ROUTER --> GEMINI[Gemini]
    ROUTER --> GROQ[Groq]
    ROUTER --> OTHERS[Other Providers]

    REQUEST --> USAGE[Usage]

    USAGE --> BILLING[Organization Billing]

    REQUEST --> LOGS[Audit Logs]
```

---

# Resource Ownership Rules

| Resource | Owner |
|----------|-------|
| User | Platform |
| Membership | Organization |
| Organization | User(s) |
| Project | Organization |
| API Key | Project |
| Usage | Project |
| Logs | Project |
| Billing | Organization |

---

# Design Principles

- Every user automatically receives one Personal Organization.
- Organizations own Projects.
- Projects own API Keys.
- API Keys generate Usage.
- Billing belongs to Organizations.
- Users never directly own API Keys.
- Permissions are granted through Memberships.