// ──────────────────────────────────────────────
// Clerk Webhook
// ──────────────────────────────────────────────

export interface ClerkWebhookEvent {
  type: string;
  object: string;
  data: Record<string, unknown>;
}

export interface ClerkWebhookRequest {
  event: ClerkWebhookEvent;
}

export interface ClerkWebhookResponse {
  received: boolean;
}