# Firebase Cloud Functions - Deployment Guide

This directory contains Firebase Cloud Functions for the Stripe integration.

## Prerequisites

1. **Firebase CLI**: Install the Firebase CLI if you haven't already
   ```bash
   npm install -g firebase-tools
   ```

2. **Firebase Project**: Ensure you have a Firebase project set up
   ```bash
   firebase login
   firebase init functions  # If not already initialized
   ```

3. **Stripe Account**: Set up a Stripe account and obtain your API keys

## Environment Configuration

Firebase Cloud Functions use environment configuration for sensitive data like API keys.

### Required Environment Variables

Set the following configuration values using the Firebase CLI:

```bash
# Stripe Secret Key (from Stripe Dashboard → Developers → API Keys)
firebase functions:config:set stripe.secret_key="<your_stripe_secret_key>"

# Stripe Webhook Secret (from Stripe Dashboard → Developers → Webhooks)
firebase functions:config:set stripe.webhook_secret="<your_webhook_secret>"
```

### Verify Configuration

Check your current configuration:

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

## Complete Setup Sequence

Follow these steps for initial setup:

```bash
# 1. Set environment variables
firebase functions:config:set stripe.secret_key="<your_stripe_secret_key>"
firebase functions:config:set stripe.webhook_secret="<your_webhook_secret>"

# 2. Install dependencies
cd functions
npm install

# 3. Deploy functions
firebase deploy --only functions

# 4. Note the deployed function URL (e.g., https://us-central1-PROJECT.cloudfunctions.net/stripeWebhook)

# 5. Configure webhook in Stripe Dashboard:
#    - Go to Stripe Dashboard → Developers → Webhooks
#    - Add endpoint with your function URL + /webhook path
#    - Select events to listen for: invoice.*, customer.subscription.*
#    - Copy the signing secret and update your config:
firebase functions:config:set stripe.webhook_secret="<your_new_webhook_secret>"
firebase deploy --only functions
```

## Security Checklist

- [ ] **NEVER** commit real API keys or secrets to source control
- [ ] **ALWAYS** verify webhook signatures using `stripe.webhooks.constructEvent`
- [ ] Use test keys (starts with sk_test_) during development
- [ ] Use live keys (starts with sk_live_) only in production with proper security
- [ ] Enable Firebase Functions environment variables encryption
- [ ] Set up Firebase Security Rules for Firestore collections
- [ ] Implement proper IAM permissions for function deployment

## Webhook Events

The function handles the following Stripe webhook events:

- `invoice.payment_succeeded` - Updates Firestore when payment succeeds
- `invoice.payment_failed` - Handles failed payments
- `customer.subscription.created` - Creates subscription record
- `customer.subscription.updated` - Updates subscription (tier changes, etc.)
- `customer.subscription.deleted` - Handles cancellations

## Testing Webhooks Locally

You can test webhooks locally using the Stripe CLI:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local function
stripe listen --forward-to localhost:5001/PROJECT_ID/us-central1/stripeWebhook/webhook

# Trigger test events
stripe trigger invoice.payment_succeeded
```

## Troubleshooting

### Function Deployment Fails

- Check that you have the correct Firebase project selected: `firebase use PROJECT_ID`
- Verify you have deployment permissions: `firebase projects:list`
- Check Node.js version compatibility in `functions/package.json`

### Webhook Signature Verification Fails

- Ensure you're using the correct webhook secret from the Stripe Dashboard
- Verify the secret matches the endpoint URL
- Check that you're using `bodyParser.raw()` and not parsing JSON before verification

### Configuration Not Loading

- Verify configuration: `firebase functions:config:get`
- After updating config, redeploy: `firebase deploy --only functions`
- Check Firebase logs: `firebase functions:log`

## Additional Resources

- [Firebase Cloud Functions Documentation](https://firebase.google.com/docs/functions)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Node.js Library](https://github.com/stripe/stripe-node)
