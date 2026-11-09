# Developer Notes - Credentials and Deployment Checklist

This document provides a comprehensive checklist for maintainers to configure credentials and environment variables required for CI/CD, deployments, and production operations.

## Required Credentials Overview

The following credentials are required to fully deploy and operate the application in staging and production environments.

### Stripe Credentials

Stripe provides separate test and live credentials. Use test credentials for development and staging, and live credentials only for production.

#### Test Mode (Development/Staging)

- **STRIPE_TEST_SECRET**: Secret key for Stripe API calls
  - Format: Starts with `sk_test_` followed by alphanumeric characters
  - Location: Stripe Dashboard → Developers → API Keys → Secret key (test mode)
  - Usage: Backend API calls, webhook signature verification

- **STRIPE_TEST_PUBLISHABLE**: Publishable key for client-side Stripe.js
  - Format: Starts with `pk_test_` followed by alphanumeric characters
  - Location: Stripe Dashboard → Developers → API Keys → Publishable key (test mode)
  - Usage: Client-side checkout, card tokenization

#### Live Mode (Production)

- **STRIPE_LIVE_SECRET**: Secret key for production Stripe API calls
  - Format: Starts with `sk_live_` followed by alphanumeric characters
  - Location: Stripe Dashboard → Developers → API Keys → Secret key (live mode)
  - Usage: Production backend API calls
  - ⚠️ **CRITICAL**: Protect this key - it can charge real money

- **STRIPE_LIVE_PUBLISHABLE**: Publishable key for production client-side
  - Format: Starts with `pk_live_` followed by alphanumeric characters
  - Location: Stripe Dashboard → Developers → API Keys → Publishable key (live mode)
  - Usage: Production client-side checkout

#### Webhook Secrets

- **STRIPE_WEBHOOK_SECRET**: Webhook endpoint signing secret
  - Format: Starts with `whsec_` followed by alphanumeric characters
  - Location: Stripe Dashboard → Developers → Webhooks → [Your endpoint] → Signing secret
  - Usage: Verify webhook authenticity
  - Note: Different secret for each webhook endpoint (test vs. live, staging vs. prod)

### Firebase Credentials

#### Service Account

- **FIREBASE_SERVICE_ACCOUNT**: Firebase Admin SDK service account JSON (base64 encoded)
  - Format: Base64-encoded JSON file
  - Location: Firebase Console → Project Settings → Service Accounts → Generate new private key
  - Usage: Server-side Firebase Admin SDK initialization, Firestore access
  - Encoding: `base64 -w 0 service-account.json > service-account-base64.txt`
  - ⚠️ **CRITICAL**: Contains private key - NEVER commit to source control

#### Project Configuration

- **FIREBASE_PROJECT_ID**: Firebase project identifier
  - Format: `your-project-id`
  - Location: Firebase Console → Project Settings → General → Project ID
  - Usage: Firebase initialization, function deployment

### Android Build Credentials (Optional)

Required only if building signed Android APKs.

- **ANDROID_KEYSTORE**: Android signing keystore file (base64 encoded)
  - Format: Base64-encoded .jks or .keystore file
  - Generation: `keytool -genkey -v -keystore release.keystore -alias release -keyalg RSA -keysize 2048 -validity 10000`
  - Encoding: `base64 -w 0 release.keystore > keystore-base64.txt`

- **KEY_ALIAS**: Alias of the key in the keystore
  - Example: `release`

- **KEYSTORE_PASSWORD**: Password for the keystore file
  - Set during keystore creation

- **KEY_PASSWORD**: Password for the specific key
  - Set during keystore creation

## Environment Variable Configuration

### CI/CD (GitHub Actions, GitLab CI, etc.)

Set these as repository secrets:

```
STRIPE_TEST_SECRET=<your_test_secret_key>
STRIPE_TEST_PUBLISHABLE=<your_test_publishable_key>
STRIPE_LIVE_SECRET=<your_live_secret_key>
STRIPE_LIVE_PUBLISHABLE=<your_live_publishable_key>
STRIPE_WEBHOOK_SECRET=<your_webhook_secret>
FIREBASE_SERVICE_ACCOUNT=<base64_encoded_json>
FIREBASE_PROJECT_ID=your-project-id
ANDROID_KEYSTORE=<base64_encoded_keystore>
KEY_ALIAS=release
KEYSTORE_PASSWORD=<password>
KEY_PASSWORD=<password>
```

### Firebase Cloud Functions

Set using Firebase CLI:

```bash
firebase functions:config:set \
  stripe.secret_key="<your_stripe_secret_key>" \
  stripe.webhook_secret="<your_webhook_secret>"
```

Verify:
```bash
firebase functions:config:get
```

### Local Development

Create a `.env` file (⚠️ **NEVER commit this file**):

```env
# Stripe Test Keys
STRIPE_TEST_SECRET=<your_test_secret_key>
STRIPE_TEST_PUBLISHABLE=<your_test_publishable_key>
STRIPE_WEBHOOK_SECRET=<your_webhook_secret>

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/service-account.json

# Android (optional)
ANDROID_KEYSTORE_PATH=/path/to/release.keystore
KEY_ALIAS=release
KEYSTORE_PASSWORD=...
KEY_PASSWORD=...
```

Add to `.gitignore`:
```
.env
.env.local
*.keystore
*.jks
service-account*.json
```

## Setup Steps

### 1. Open Draft Pull Request

This PR is intentionally opened as a **draft** to allow for credential configuration and review before merging.

**Steps:**
1. Review all files added in this PR
2. Verify no secrets are committed (use `git log -p` to review)
3. Add required credentials to CI/CD secrets
4. Configure Firebase functions environment variables
5. Mark PR as "Ready for review" once credentials are configured

### 2. Stripe Configuration

**Create Products and Prices:**

```bash
# Using Stripe CLI
stripe products create --name="Silver Tier" --description="Premium channels, HD streaming"
stripe prices create --product=prod_XXX --unit-amount=999 --currency=usd --recurring.interval=month

stripe products create --name="Gold Tier" --description="All channels, HD + 4K, offline downloads"
stripe prices create --product=prod_YYY --unit-amount=1999 --currency=usd --recurring.interval=month
```

**Configure Webhook:**

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://YOUR_FUNCTION_URL/webhook`
3. Select events:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy signing secret and add to Firebase config

### 3. Firebase Deployment

**Initial Setup:**

```bash
# Install dependencies
cd functions
npm install

# Set environment variables
firebase functions:config:set \
  stripe.secret_key="<your_stripe_secret_key>" \
  stripe.webhook_secret="<your_webhook_secret>"

# Deploy functions
firebase deploy --only functions
```

**Firestore Security Rules:**

Update `firestore.rules` to protect entitlements:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /entitlements/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;
    }
    match /users/{uid}/subscriptions/{subId} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;
    }
  }
}
```

Deploy rules:
```bash
firebase deploy --only firestore:rules
```

### 4. Staging Verification

Test the following in staging environment:

- [ ] User can create checkout session
- [ ] Stripe Checkout page loads correctly
- [ ] Test payment succeeds (use test card: 4242 4242 4242 4242)
- [ ] Webhook receives `invoice.payment_succeeded`
- [ ] Firestore entitlements update correctly
- [ ] Client app reflects new subscription tier
- [ ] Premium channels unlock for gold tier users
- [ ] Subscription management (upgrade, downgrade, cancel) works

### 5. Production Promotion

**Pre-production Checklist:**

- [ ] All staging tests pass
- [ ] Stripe products and prices created in live mode
- [ ] Live webhook endpoint configured
- [ ] Firebase functions config updated with live keys
- [ ] Firestore security rules deployed
- [ ] Monitoring and alerting configured
- [ ] Customer support team briefed on subscription flows

**Deployment:**

```bash
# Update to live Stripe keys
firebase functions:config:set \
  stripe.secret_key="<your_live_stripe_secret_key>" \
  stripe.webhook_secret="<your_live_webhook_secret>"

# Deploy with live configuration
firebase deploy --only functions

# Verify deployment
curl https://YOUR_PROD_FUNCTION_URL/health
```

**Post-deployment:**

- [ ] Verify webhook endpoint in Stripe Dashboard (live mode)
- [ ] Test with real card in production (small amount, then refund)
- [ ] Monitor Cloud Function logs for first few hours
- [ ] Set up alerts for failed webhooks or errors

## Maintenance Tasks

### Rotating Secrets

**Stripe Webhook Secret:**

1. Create new webhook endpoint in Stripe Dashboard
2. Update Firebase config with new secret
3. Deploy functions: `firebase deploy --only functions`
4. Delete old webhook endpoint after verifying new one works

**Firebase Service Account:**

1. Generate new service account key in Firebase Console
2. Update CI/CD secret with new base64-encoded JSON
3. Trigger new deployment
4. Revoke old service account key

### Monitoring

Set up alerts for:
- Failed webhook deliveries (Stripe Dashboard)
- Cloud Function errors (Firebase Console → Functions)
- Failed payment attempts (Stripe Dashboard → Payments)
- Firestore write errors (Firebase Console → Firestore)

## Troubleshooting

### Webhook Signature Verification Fails

- Verify `STRIPE_WEBHOOK_SECRET` matches the endpoint in Stripe Dashboard
- Check endpoint URL exactly matches (including trailing slash)
- Ensure `bodyParser.raw()` is used, not `bodyParser.json()`

### Entitlements Not Updating

- Check Cloud Function logs: `firebase functions:log`
- Verify customer metadata includes `firebaseUid`
- Check Firestore security rules allow function to write
- Verify webhook events are being delivered (Stripe Dashboard)

### Android Build Fails

- Verify keystore base64 decoding: `echo $ANDROID_KEYSTORE | base64 -d > test.keystore`
- Check keystore password and alias are correct
- Ensure keystore file is not corrupted

## Security Best Practices

- ✅ Store all secrets in environment variables or secure vaults
- ✅ Use different credentials for test, staging, and production
- ✅ Rotate secrets periodically (at least annually)
- ✅ Limit access to production credentials to essential personnel only
- ✅ Enable audit logging for credential access
- ✅ Use least-privilege access for service accounts
- ✅ Monitor for unauthorized access or unusual activity
- ❌ NEVER commit secrets to source control
- ❌ NEVER share secrets via email or chat
- ❌ NEVER use production credentials in development/testing

## Contact

For access to credentials or deployment permissions, contact:

- **Stripe Access**: [Project Owner] - for API keys and webhook configuration
- **Firebase Access**: [Project Owner] - for service account and deployer permissions
- **Android Signing**: [Build Team Lead] - for keystore access

---

**Last Updated**: 2024-12-25  
**Maintained By**: Development Team
