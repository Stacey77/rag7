# Firebase Cloud Functions - Deployment Guide

This directory contains Firebase Cloud Functions for handling Stripe webhooks and other backend operations.

## Functions Overview

### `stripeWebhooks`
Express app that receives Stripe webhook events and updates user entitlements in Firestore.

**Endpoint**: `https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/stripeWebhooks/webhook`

**Handles events**:
- `checkout.session.completed` - New subscription via Checkout
- `customer.subscription.created` - Subscription created
- `customer.subscription.updated` - Subscription updated (renewal, plan change)
- `customer.subscription.deleted` - Subscription canceled
- `invoice.payment_succeeded` - Payment successful
- `invoice.payment_failed` - Payment failed

## Prerequisites

1. **Firebase Project**: Ensure you have a Firebase project set up
2. **Firebase CLI**: Install with `npm install -g firebase-tools`
3. **Stripe Account**: Test or live account with API keys
4. **Node.js**: Version 14 or higher

## Setup Instructions

### 1. Initialize Firebase Functions (if not already done)

```bash
firebase init functions
```

Select:
- JavaScript or TypeScript
- Install dependencies with npm

### 2. Install Dependencies

```bash
cd functions
npm install express body-parser stripe firebase-admin
```

### 3. Configure Environment Variables

Firebase Functions use `functions:config` to store environment variables.

#### Set Stripe Keys

```bash
# Test mode (for development)
firebase functions:config:set \
  stripe.secret_key="sk_test_YOUR_TEST_KEY" \
  stripe.webhook_secret="whsec_YOUR_WEBHOOK_SECRET"

# Production mode (for live deployment)
firebase functions:config:set \
  stripe.secret_key="sk_live_YOUR_LIVE_KEY" \
  stripe.webhook_secret="whsec_YOUR_LIVE_WEBHOOK_SECRET"
```

#### View Current Config

```bash
firebase functions:config:get
```

#### Access in Code

```javascript
const functions = require('firebase-functions');
const stripeKey = functions.config().stripe.secret_key;
const webhookSecret = functions.config().stripe.webhook_secret;
```

### 4. Update functions/index.js

Add the webhook function to your main functions/index.js:

```javascript
const functions = require('firebase-functions');
const stripeWebhooks = require('./stripe-webhooks');

// Export the webhook handler
exports.stripeWebhooks = functions.https.onRequest(stripeWebhooks);
```

### 5. Deploy Functions

#### Deploy all functions:
```bash
firebase deploy --only functions
```

#### Deploy specific function:
```bash
firebase deploy --only functions:stripeWebhooks
```

### 6. Configure Stripe Webhook

After deployment, you'll get a function URL like:
```
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/stripeWebhooks
```

1. Go to [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter webhook URL: `https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/stripeWebhooks/webhook`
   - **Important**: Add `/webhook` to the end of your function URL
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the "Signing secret" (starts with `whsec_`)
6. Update your Firebase config:
   ```bash
   firebase functions:config:set stripe.webhook_secret="whsec_..."
   firebase deploy --only functions:stripeWebhooks
   ```

## Security Considerations

### ⚠️ CRITICAL: Webhook Signature Verification

**NEVER deploy to production without verifying webhook signatures!**

The current code has signature verification **disabled by default** for initial testing. Before going live:

1. **Enable signature verification** in `stripe-webhooks/index.js`:
   - Uncomment lines 60-70 (the `stripe.webhooks.constructEvent` block)
   - Remove or comment out the unsafe `JSON.parse(req.body.toString())` line

2. **Ensure `STRIPE_WEBHOOK_SECRET` is set**:
   ```bash
   firebase functions:config:get stripe.webhook_secret
   ```

3. **Test with Stripe CLI** before deploying:
   ```bash
   stripe listen --forward-to http://localhost:5000/YOUR_PROJECT/us-central1/stripeWebhooks/webhook
   stripe trigger checkout.session.completed
   ```

### Why Signature Verification Matters

Without signature verification, attackers could:
- Spoof webhook events to grant themselves premium subscriptions
- Forge payment success events without actually paying
- Delete other users' subscriptions
- Access your system for free

**The security of your payment system depends on webhook verification!**

### Other Security Best Practices

1. **Use environment variables** for all secrets (never hardcode)
2. **Restrict Firestore access** with security rules
3. **Use HTTPS only** (Firebase Functions enforces this)
4. **Log webhook events** for audit trail
5. **Validate Firebase UID** in customer metadata
6. **Rate limit** webhook endpoint if needed

## Testing Locally

### 1. Install Firebase Emulator

```bash
firebase init emulators
# Select "Functions" emulator
```

### 2. Set Local Environment Variables

Create `.runtimeconfig.json` in the functions directory:

```json
{
  "stripe": {
    "secret_key": "sk_test_YOUR_TEST_KEY",
    "webhook_secret": "whsec_YOUR_WEBHOOK_SECRET"
  }
}
```

**⚠️ Add `.runtimeconfig.json` to `.gitignore` immediately!**

### 3. Start Emulators

```bash
firebase emulators:start --only functions
```

### 4. Test with Stripe CLI

```bash
# Forward webhooks to local emulator
stripe listen --forward-to http://localhost:5001/YOUR_PROJECT/us-central1/stripeWebhooks/webhook

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
```

## Monitoring and Logs

### View Function Logs

```bash
# All functions
firebase functions:log

# Specific function
firebase functions:log --only stripeWebhooks

# Tail logs (real-time)
firebase functions:log --only stripeWebhooks --follow
```

### Firebase Console

View logs in the Firebase Console:
- Go to [Firebase Console](https://console.firebase.google.com/)
- Select your project
- Navigate to Functions > Logs

### Stripe Dashboard

Monitor webhook deliveries:
- Go to [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/webhooks)
- Click on your endpoint
- View delivery attempts, responses, and errors

## Troubleshooting

### Webhook Returns 500 Error

Check:
1. Environment variables are set correctly
2. Firebase Admin SDK is initialized
3. Firestore security rules allow function to write
4. Check function logs for specific error

### Signature Verification Fails

Possible causes:
1. Wrong webhook secret configured
2. Body parser consuming raw body (use `bodyParser.raw()`)
3. Webhook secret from wrong endpoint (test vs live)

### Customer Metadata Missing firebase_uid

Ensure your Checkout Session includes metadata:

```javascript
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  // ... other params
  metadata: {
    firebase_uid: user.uid
  }
});
```

Or set it on the customer:

```javascript
await stripe.customers.update(customerId, {
  metadata: { firebase_uid: user.uid }
});
```

## Cost Considerations

Firebase Cloud Functions pricing:
- **Free tier**: 2M invocations/month, 400K GB-seconds
- **Paid**: $0.40 per million invocations after free tier

Typical webhook function costs:
- ~50ms execution time
- ~256MB memory
- Low volume: Free tier sufficient
- High volume: ~$0.40 per million webhooks

Monitor usage in [Firebase Console > Usage and Billing](https://console.firebase.google.com/project/_/usage).

## Next Steps

1. ✅ Set up environment variables
2. ✅ Deploy functions
3. ✅ Configure Stripe webhook
4. ⚠️ **Enable signature verification** (before production!)
5. ✅ Test with Stripe CLI
6. ✅ Monitor logs and webhook deliveries
7. ✅ Set up Firestore security rules
8. ✅ Implement createCheckoutSession function (client-side)

## Additional Resources

- [Firebase Cloud Functions Documentation](https://firebase.google.com/docs/functions)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Node.js Library](https://github.com/stripe/stripe-node)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
