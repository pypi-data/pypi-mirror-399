# Alpha CLI API Reference

This document describes the backend API endpoints for Alpha CLI.

## Base URL

```
Production: https://api.alpha.dev/v1
```

## Authentication

API requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: alpha_live_xxx" https://api.alpha.dev/v1/auth/validate
```

Or as a Bearer token:

```bash
curl -H "Authorization: Bearer alpha_live_xxx" https://api.alpha.dev/v1/auth/validate
```

## Rate Limits

| User Type | Requests/Minute |
|-----------|-----------------|
| Anonymous | 20 |
| Free | 100 |
| Premium | 1000 |

Rate limit headers are returned with each response:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Endpoints

### Health Check

```http
GET /
```

Returns API status information.

**Response:**
```json
{
  "name": "Alpha CLI Backend",
  "version": "v1",
  "status": "healthy"
}
```

---

### Validate API Key

```http
POST /v1/auth/validate
```

Validates an API key and returns the user's subscription status.

**Headers:**
- `X-API-Key`: API key to validate

**Response:**
```json
{
  "status": "premium",
  "email": "user@example.com",
  "subscriptionEnd": "2025-02-28T00:00:00Z"
}
```

**Status Values:**
- `anonymous`: No API key provided
- `free`: Valid key, no subscription
- `premium`: Valid key + active subscription
- `expired`: Valid key, subscription lapsed
- `invalid`: Invalid or revoked key

---

### Cross-Reference Scan

```http
POST /v1/scan
```

Cross-references congressional trades with prediction markets.

**Headers:**
- `X-API-Key`: Required

**Request Body:**
```json
{
  "days": 30,
  "ticker": "NVDA",
  "party": "R"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| days | integer | 30 | Days to look back (1-365) |
| ticker | string | null | Filter by stock ticker |
| party | string | null | Filter by party (R or D) |

**Response:**
```json
{
  "crossReferences": [
    {
      "congressTrade": {
        "transactionDate": "2025-12-15",
        "disclosureDate": "2025-12-18",
        "ticker": "NVDA",
        "assetDescription": "NVIDIA Corporation",
        "tradeType": "purchase",
        "amount": "$50,001 - $100,000",
        "representative": "Nancy Pelosi",
        "party": "D"
      },
      "relatedMarkets": [
        {
          "platform": "kalshi",
          "ticker": "KXNVDA-Q4-EARNINGS",
          "title": "Will NVIDIA beat Q4 earnings?",
          "yesPrice": 0.65,
          "noPrice": 0.36,
          "volume": 50000,
          "relevanceScore": 0.95,
          "relevanceType": "direct"
        }
      ]
    }
  ],
  "generatedAt": "2025-12-29T12:00:00Z",
  "cacheTtl": 900,
  "isStale": false
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "code": "E401_INVALID_KEY",
  "message": "Invalid API key. Run `alpha login` to authenticate.",
  "retryAfter": 60
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| E401_INVALID_KEY | 401 | Invalid or missing API key |
| E401_EXPIRED_KEY | 401 | API key has expired |
| E403_PREMIUM_REQUIRED | 403 | Feature requires premium subscription |
| E429_RATE_LIMITED | 429 | Rate limit exceeded |
| E500_INTERNAL | 500 | Internal server error |
| E503_KALSHI | 503 | Kalshi API unavailable |
| E503_CONGRESS | 503 | Congress data unavailable |

---

## Webhooks

### Stripe Webhook

```http
POST /webhooks/stripe
```

Receives Stripe webhook events for subscription management.

**Headers:**
- `Stripe-Signature`: Stripe signature header

**Events Handled:**
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`
