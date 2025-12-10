# Firebase Cloud Functions - Deployment Guide

This directory contains Firebase Cloud Functions for handling Stripe webhooks and billing integration.

## Prerequisites

1. **Firebase CLI**: Install globally
   ```bash
   npm install -g firebase-tools
   ```

2. **Firebase Project**: Initialize or select your Firebase project
   ```bash
   firebase login
   firebase use <your-project-id>
   ```

3. **Stripe Account**: Create a Stripe account and obtain API keys
   - Test mode keys for development: `sk_test_...` and `pk_test_...`
   - Live mode keys for production: `sk_live_...` and `pk_live_...`

## Environment Configuration

Firebase Cloud Functions use environment configuration to securely store API keys and secrets.

### Set Stripe Configuration

```bash
# Set Stripe secret key (use test key for development)
firebase functions:config:set stripe.secret_key="sk_test_YOUR_STRIPE_SECRET_KEY"

# Set Stripe webhook secret (obtain from Stripe Dashboard -> Developers -> Webhooks)
firebase functions:config:set stripe.webhook_secret="whsec_YOUR_WEBHOOK_SECRET"
```

### Verify Configuration

```bash
firebase functions:config:get
```

Expected output:
```json
{
  "stripe": {
    "secret_key": "sk_test_...",
    "webhook_secret": "whsec_..."
  }
}
```

## Webhook Signature Verification

**CRITICAL**: Always verify webhook signatures in production to prevent unauthorized access.

The webhook handler in `stripe-webhooks/index.js` uses `stripe.webhooks.constructEvent()` to verify signatures. This ensures that webhook events are genuinely from Stripe.

### Obtaining Webhook Secret

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/webhooks)
2. Click "Add endpoint" or select existing endpoint
3. Set endpoint URL to your Cloud Function URL: `https://us-central1-<project-id>.cloudfunctions.net/stripeWebhook/webhook`
4. Select events to listen for:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the "Signing secret" (starts with `whsec_`)

## Deployment

### Full Deployment Sequence

```bash
# 1. Set environment variables (do this once or when secrets change)
firebase functions:config:set \
  stripe.secret_key="sk_test_YOUR_KEY" \
  stripe.webhook_secret="whsec_YOUR_SECRET"

# 2. Deploy all functions
firebase deploy --only functions

# 3. Note the deployed function URL
# Example: https://us-central1-your-project.cloudfunctions.net/stripeWebhook
```

### Deploy Only Specific Functions

```bash
# Deploy only the stripe webhook function
firebase deploy --only functions:stripeWebhook
```

## Function URL

After deployment, your webhook endpoint will be available at:
```
https://us-central1-<project-id>.cloudfunctions.net/stripeWebhook/webhook
```

Configure this URL in your Stripe Dashboard as the webhook endpoint.

## Testing Webhooks Locally

Use Stripe CLI to test webhooks during development:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local function
stripe listen --forward-to http://localhost:5001/<project-id>/us-central1/stripeWebhook/webhook

# Trigger test events
stripe trigger invoice.payment_succeeded
```

## Firestore Security Rules

Ensure your Firestore security rules protect subscription and entitlement data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read their own subscription data
    match /users/{userId}/subscriptions/{subscriptionId} {
      allow read: if request.auth.uid == userId;
      allow write: if false; // Only Cloud Functions can write
    }
    
    // Users can only read their own entitlements
    match /entitlements/{userId} {
      allow read: if request.auth.uid == userId;
      allow write: if false; // Only Cloud Functions can write
    }
  }
}
```

## Monitoring and Logs

View function logs in Firebase Console or via CLI:

```bash
# View recent logs
firebase functions:log

# Stream logs in real-time
firebase functions:log --only stripeWebhook
```

## Troubleshooting

### Error: "Webhook secret not configured"
- Ensure `firebase functions:config:set stripe.webhook_secret="whsec_..."` was run
- Redeploy functions after setting config

### Error: "Webhook signature verification failed"
- Verify the webhook secret matches the one in Stripe Dashboard
- Check that the raw body is being passed to `stripe.webhooks.constructEvent()`

### Error: "Function not found"
- Ensure functions are deployed: `firebase deploy --only functions`
- Check function name matches the one configured in Stripe

## Security Best Practices

1. **Never commit secrets**: Always use environment config or Secret Manager
2. **Verify signatures**: Always verify webhook signatures in production
3. **Use HTTPS**: Cloud Functions automatically use HTTPS
4. **Restrict CORS**: Only allow requests from Stripe IPs if possible
5. **Monitor logs**: Regularly check logs for suspicious activity
6. **Use test mode**: Test thoroughly with Stripe test keys before going live

## Production Checklist

Before deploying to production:

- [ ] Replace test keys with live keys
- [ ] Update webhook endpoint URL in Stripe Dashboard (live mode)
- [ ] Deploy with live configuration
- [ ] Test end-to-end subscription flow
- [ ] Monitor logs for errors
- [ ] Set up alerts for critical errors
- [ ] Document runbook for common issues

## Additional Resources

- [Firebase Cloud Functions Documentation](https://firebase.google.com/docs/functions)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Node.js Library](https://github.com/stripe/stripe-node)
