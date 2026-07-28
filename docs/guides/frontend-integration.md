# Frontend Integration Guide

## Overview

Clerk handles all authentication UI (login, signup, org switching, user management). Your frontend uses Clerk's SDK, and the Zam AI backend validates the JWTs Clerk issues. This guide walks through the full integration.

```
Browser/Frontend (Clerk SDK)          Clerk Cloud              Zam AI Backend
       │                                  │                         │
       │── User signs up ──────────────►  │                         │
       │                                  │── webhook: user.created─►│
       │                                  │                         │── creates User + default Org
       │                                  │                         │
       │── User creates org ───────────►  │                         │
       │                                  │── webhook: org.created─►│── creates Organization row
       │                                  │── webhook: membership──►│── creates User-Org link
       │                                  │                         │
       │── Clerk issues JWT ────────────  │                         │
       │                                  │                         │
       │── API call (Bearer JWT) ──────────────────────────────────►│
       │                                  │                         │── validates JWT
       │                                  │                         │── resolves org by clerk_org_id
       │                                  │                         │── routes request
```

---

## Part 1: Clerk Dashboard Setup

### 1.1 Configure Webhook

In your Clerk Dashboard, go to **Webhooks** and create a new endpoint:

| Field | Value |
|---|---|
| **Endpoint URL** | `https://testdeploy-pyb7.onrender.com/v1/auth/webhook` |
| **Subscribe to events** | `user.created`, `user.updated`, `organization.created`, `organization.updated`, `organization_membership.created` |

Clerk will give you a **Signing Secret** (starts with `whsec_`). Add this to the backend's `.env`:

```
ZAM_AI_CLERK_WEBHOOK_SECRET=whsec_your_signing_secret_here
```

### 1.2 Create JWT Template

In Clerk Dashboard, go to **JWT Templates** and create a new template (or customize the default). Make sure the template includes these claims:

```json
{
  "sub": "{{user.id}}",
  "org_id": "{{org.id}}",
  "sid": "{{session.id}}"
}
```

The `org_id` claim is **critical** — our backend uses it to resolve which organization the request belongs to.

Copy the **Issuer URL** from the JWT template (looks like `https://your-clerk-domain.clerk.accounts.dev`) and add to the backend's `.env`:

```
ZAM_AI_CLERK_SECRET_KEY=sk_test_xxxx
ZAM_AI_CLERK_PUBLISHABLE_KEY=pk_test_xxxx
```

### 1.3 Info I Need From You

To fill in the frontend code below, I need:

```
Clerk Publishable Key:    pk_test_xxxx
Backend API URL:          https://testdeploy-pyb7.onrender.com
```

---

## Part 2: Frontend — Clerk Setup

### 2.1 Install Clerk SDK

```bash
npm install @clerk/clerk-react
```

### 2.2 Wrap Your App

```tsx
import { ClerkProvider } from "@clerk/clerk-react";

const CLERK_PUBLISHABLE_KEY = "pk_test_xxxx";  // ← from Clerk Dashboard

function App() {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <YourApp />
    </ClerkProvider>
  );
}
```

### 2.3 Sign-Up / Sign-In

Clerk provides pre-built components:

```tsx
import { SignUp, SignIn, useUser } from "@clerk/clerk-react";

function SignUpPage() {
  return <SignUp />;
}

function SignInPage() {
  return <SignIn />;
}
```

Or use custom hooks for headless auth:

```tsx
import { useSignIn } from "@clerk/clerk-react";

function CustomSignIn() {
  const { signIn, isLoaded } = useSignIn();
  // build your own UI with signIn.authenticateWithRedirect(...)
}
```

---

## Part 3: Frontend — Org Management

### 3.1 Create an Organization

Use Clerk's `useOrganizationList` hook:

```tsx
import { useOrganizationList } from "@clerk/clerk-react";

function CreateOrgButton() {
  const { createOrganization } = useOrganizationList();

  async function handleCreate() {
    await createOrganization({ name: "My Org" });
    // Clerk creates the org + sends webhooks to our backend
    // Backend auto-creates the Organization row and User membership
  }

  return <button onClick={handleCreate}>Create Organization</button>;
}
```

### 3.2 Switch Active Organization

```tsx
import { useOrganizationList } from "@clerk/clerk-react";

function OrgSwitcher() {
  const { setActive, organizationList } = useOrganizationList();

  return (
    <select onChange={(e) => setActive({ organization: e.target.value })}>
      {organizationList.map((org) => (
        <option key={org.id} value={org.id}>{org.name}</option>
      ))}
    </select>
  );
}
```

When the user switches orgs, Clerk re-issues the JWT with the new `org_id` claim. All subsequent API calls will be scoped to that org.

---

## Part 4: Frontend — Calling the API

### 4.1 Get the Auth Token

```tsx
import { useAuth } from "@clerk/clerk-react";

function ApiClient() {
  const { getToken } = useAuth();

  async function callApi(endpoint: string, options?: RequestInit) {
    const token = await getToken({ template: "zam-ai" });

    const response = await fetch(`https://testdeploy-pyb7.onrender.com${endpoint}`, {
      ...options,
      headers: {
        ...options?.headers,
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || "Request failed");
    }

    return response.json();
  }

  return { callApi };
}
```

### 4.2 Check Health (No Auth Required)

```ts
const health = await callApi("/v1/health");
// { status: "ok", service: "zam-ai-core-api", version: "0.1.0", ... }
```

### 4.3 Get Your Organization Details

```ts
const org = await callApi("/v1/organizations/me");
// {
//   id: 1,
//   clerk_org_id: "org_xxxx",
//   name: "My Org",
//   slug: "my-org",
//   plan: "free",
//   is_active: true,
//   created_at: "2026-07-28T...",
//   member_count: 3,
//   project_count: 1
// }
```

### 4.4 Manage Projects

```ts
// List projects
const projects = await callApi("/v1/organizations/me/projects");
// { projects: [{ id: 1, name: "Production", slug: "prod", ... }] }

// Create a project
const project = await callApi("/v1/organizations/me/projects", {
  method: "POST",
  body: JSON.stringify({ name: "My Project", slug: "my-project" }),
});
```

### 4.5 Manage API Keys

```ts
// List keys
const keys = await callApi("/v1/organizations/me/api-keys");
// { keys: [{ id: "abc123", label: "My Key", prefix: "zam_abc...", ... }] }

// Create a key
const newKey = await callApi("/v1/organizations/me/api-keys", {
  method: "POST",
  body: JSON.stringify({ label: "My Key" }),
});
// ⚠ The full key value is only returned ONCE at creation time

// Rotate a key (generates new key value)
await callApi(`/v1/organizations/me/api-keys/${keyId}/rotate`, {
  method: "POST",
});

// Revoke a key
await callApi(`/v1/organizations/me/api-keys/${keyId}/revoke`, {
  method: "POST",
});
```

### 4.6 Check Usage

```ts
const usage = await callApi("/v1/organizations/me/usage?from=2026-07-01&to=2026-07-28");
// {
//   organization_id: 1,
//   from_date: "2026-07-01",
//   to_date: "2026-07-28",
//   endpoints: [{ endpoint: "/v1/ai/medical-qa", request_count: 42, ... }],
//   totals: { total_requests: 42, total_prompt_tokens: 1200, total_completion_tokens: 3400 }
// }
```

---

## Part 5: End-to-End Walkthrough

Here's the complete flow a new user goes through:

### Step 1: User Signs Up

```
Action:                    User fills sign-up form (Clerk UI)
Backend receives:          Webhook `user.created`
Backend does:              Creates User row + default Organization + membership
Frontend sees:             User is signed in, no org selected yet
```

### Step 2: User Creates an Organization

```
Action:                    User clicks "Create Organization" (your UI via Clerk SDK)
Backend receives:          Webhook `organization.created` + `organization_membership.created`
Backend does:              Creates Organization row + User membership link
Frontend sees:             Org appears in org switcher
```

### Step 3: User Creates a Project

```
Action:                    User fills "Create Project" form
Frontend calls:            POST /v1/organizations/me/projects   (with Bearer JWT)
Backend does:              Looks up org from JWT, creates Project row
Frontend sees:             Project appears in dashboard
```

### Step 4: User Creates an API Key

```
Action:                    User clicks "Generate API Key"
Frontend calls:            POST /v1/organizations/me/api-keys  (with Bearer JWT)
Backend does:              Creates key tied to the org, returns full key value
Frontend shows:            The key ONCE, with copy button + warning to save it
```

### Step 5: Use the API Key

The generated key can be used for server-to-server calls without Clerk:

```bash
curl -H "X-Zam-AI-Key: zam_abc123..." https://testdeploy-pyb7.onrender.com/v1/ai/medical-qa
```

---

## Part 6: Endpoints Reference

### Public (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/health` | Health check |
| POST | `/v1/auth/webhook` | Clerk webhook receiver |

### Auth Required (Bearer JWT or X-Zam-AI-Key)

#### Organization

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/organizations/me` | Current org details |
| GET | `/v1/organizations/me/usage` | Org usage stats |

#### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/organizations/me/projects` | List projects |
| POST | `/v1/organizations/me/projects` | Create project |
| GET | `/v1/organizations/me/projects/{id}` | Project detail |
| PATCH | `/v1/organizations/me/projects/{id}` | Update project |
| DELETE | `/v1/organizations/me/projects/{id}` | Delete project |

#### API Keys

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/organizations/me/api-keys` | List keys |
| POST | `/v1/organizations/me/api-keys` | Create key |
| POST | `/v1/organizations/me/api-keys/{id}/rotate` | Rotate key |
| POST | `/v1/organizations/me/api-keys/{id}/revoke` | Revoke key |

#### AI Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/ai/medical-qa` | Medical Q&A |
| POST | `/v1/ai/interactions/check` | Drug interaction check |
| POST | `/v1/ai/drug-info` | Drug information |
| POST | `/v1/ai/symptom-guidance` | Symptom guidance |
| POST | `/v1/ai/contraindications/check` | Contraindication check |
| POST | `/v1/ai/dosage/verify` | Dosage verification |
| POST | `/v1/ai/prescriptions/explain` | Prescription explanation |
| POST | `/v1/ai/chat` | Chat with intent routing |

---

## Part 7: Error Handling

All errors return a consistent JSON structure:

```json
{
  "request_id": "req_abc123",
  "status": "error",
  "error": {
    "code": "authentication_failed",
    "message": "Invalid or expired authentication token.",
    "retryable": false,
    "details": {}
  }
}
```

Common error codes:

| Code | Meaning | Retryable |
|------|---------|-----------|
| `authentication_failed` | Missing/invalid token | No |
| `authorization_failed` | No permission for this resource | No |
| `not_found` | Resource doesn't exist | No |
| `rate_limit_exceeded` | Too many requests | Yes (wait) |
| `validation_error` | Invalid request body | No (fix request) |
| `internal_error` | Server error | Yes |

---

## Appendix: Environment Variables (Backend)

These go in the backend's `.env` file:

```env
# Clerk
ZAM_AI_CLERK_SECRET_KEY=sk_test_xxxx
ZAM_AI_CLERK_PUBLISHABLE_KEY=pk_test_xxxx
ZAM_AI_CLERK_WEBHOOK_SECRET=whsec_xxxx

# Bootstrap org ID (for admin keys created at startup)
ZAM_AI_BOOTSTRAP_ORGANIZATION_ID=1
```

---

## What I Need From You

To make this guide concrete (no placeholders), please provide:

1. **Clerk Publishable Key** — from Clerk Dashboard → API Keys
2. **Backend deployed URL** — the Render/Cloud Run URL
3. **JWT template name** — if you created a custom template (otherwise the default "default" is used)
4. **Any Clerk domain** — so I can verify the JWT issuer URL format

Paste them and I'll update the guide with real values.