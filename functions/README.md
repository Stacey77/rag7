# Firebase Functions - Stripe Webhooks

This directory contains Firebase Cloud Functions for handling Stripe webhook events.

## Overview

The webhook handler processes Stripe events (payments, subscriptions) and updates Firestore with the latest subscription and entitlement information.

## Prerequisites

1. **Stripe Account**: Create products and prices in Stripe Dashboard
2. **Firebase Project**: Set up with Cloud Functions and Firestore enabled
3. **Stripe Webhook**: Configure in Stripe Dashboard pointing to your function URL

## Environment Configuration

Firebase Functions uses a config system to store secrets securely.

### Set Stripe Keys

```bash
# Set Stripe secret key (from Stripe Dashboard -> Developers -> API keys)
firebase functions:config:set stripe.secret_key="sk_test_..."

# Set webhook signing secret (from Stripe Dashboard -> Developers -> Webhooks)
firebase functions:config:set stripe.webhook_secret="whsec_..."
```

### Verify Configuration

```bash
firebase functions:config:get
```

## Deployment

### Deploy All Functions

```bash
firebase deploy --only functions
```

### Deploy Specific Function

```bash
firebase deploy --only functions:stripeWebhook
```

## Webhook Setup in Stripe Dashboard

1. Go to **Stripe Dashboard** → **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your function URL: `https://[region]-[project-id].cloudfunctions.net/stripeWebhook/webhook`
4. Select events to listen to:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Signing secret** and set it in Firebase config (see above)

## Required TODOs Before Production

### 1. Signature Verification (CRITICAL)

Uncomment and test signature verification in `index.js`:

```javascript
event = stripe.webhooks.constructEvent(
  req.body,
  sig,
  webhookSecret
);
```

This prevents unauthorized webhook calls.

### 2. Firebase Admin SDK

Initialize Firebase Admin SDK in your function:

```javascript
const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();
```

### 3. Customer Metadata Mapping

When creating Stripe customers, include Firebase UID in metadata:

```javascript
const customer = await stripe.customers.create({
  email: user.email,
  metadata: {
    firebaseUid: user.uid
  }
});
```

### 4. Firestore Security Rules

Ensure users can only read their own entitlements:

```javascript
match /entitlements/{uid} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow write: if false; // Only functions can write
}
```

## Testing Locally

### Install Dependencies

```bash
cd functions/stripe-webhooks
npm install express body-parser stripe
```

### Run Locally with Stripe CLI

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/webhook

# Run function locally
STRIPE_SECRET_KEY=sk_test_... STRIPE_WEBHOOK_SECRET=whsec_... node index.js
```

### Test with Stripe CLI

```bash
stripe trigger invoice.payment_succeeded
stripe trigger customer.subscription.created
```

## Environment Variables Reference

| Variable | Source | Purpose |
|----------|--------|---------|
| `STRIPE_SECRET_KEY` | Stripe Dashboard → API keys | Authenticate API calls |
| `STRIPE_WEBHOOK_SECRET` | Stripe Dashboard → Webhooks | Verify webhook signatures |

## Deployment Sequence

```bash
# 1. Set environment variables
firebase functions:config:set \
  stripe.secret_key="sk_test_..." \
  stripe.webhook_secret="whsec_..."

# 2. Deploy functions
firebase deploy --only functions

# 3. Get function URL
firebase functions:config:get

# 4. Configure webhook endpoint in Stripe Dashboard with the URL
# 5. Test with Stripe CLI or Dashboard
```

## Monitoring

View logs in Firebase Console:

```bash
firebase functions:log --only stripeWebhook
```

Or in Google Cloud Console → Cloud Functions → Logs

## Security Checklist

- [ ] Webhook signatures are verified
- [ ] Environment variables contain no real secrets in code
- [ ] Firestore security rules prevent unauthorized access
- [ ] Customer metadata includes firebaseUid for mapping
- [ ] Error handling prevents information leakage
- [ ] Logs don't contain sensitive data

## Support

For issues or questions:
- Firebase Functions docs: https://firebase.google.com/docs/functions
- Stripe webhooks guide: https://stripe.com/docs/webhooks
