# Developer Notes & Checklist

This document contains the developer checklist for setting up the complete end-to-end RAG7 application with Stripe payments and Firebase backend.

## Overview

This project requires several external services and credentials to be fully operational:

- **Stripe**: Payment processing for premium subscriptions
- **Firebase**: Authentication, Firestore database, Cloud Functions, and hosting
- **Android/iOS**: Building and signing mobile applications (if applicable)

## Credentials & Access Required

### 1. Stripe Access

#### Required Keys

| Key | Environment Variable | Where to Find | Notes |
|-----|---------------------|---------------|-------|
| Secret Key (Test) | `STRIPE_SECRET_KEY` | [Stripe Dashboard > Developers > API keys](https://dashboard.stripe.com/test/apikeys) | Starts with `sk_test_` |
| Publishable Key (Test) | `STRIPE_PUBLISHABLE_KEY` | [Stripe Dashboard > Developers > API keys](https://dashboard.stripe.com/test/apikeys) | Starts with `pk_test_` |
| Webhook Secret (Test) | `STRIPE_WEBHOOK_SECRET` | [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/test/webhooks) | Starts with `whsec_` (after creating endpoint) |

#### Setup Steps

1. Create a Stripe account at https://stripe.com
2. Navigate to Developers > API keys
3. Copy "Publishable key" and "Secret key" for test mode
4. Create Gold membership product:
   - Go to Products > Add product
   - Name: "Gold Membership"
   - Price: $9.99/month (or your preferred price)
   - Save and copy the Price ID (starts with `price_`)
5. Deploy webhook function (see below)
6. Configure webhook endpoint in Stripe Dashboard
7. Copy webhook signing secret

#### Stripe Product Configuration

Create products in Stripe Dashboard:

```
Product: Gold Membership
- Price ID: price_XXXXXXXXXXXX (monthly)
- Amount: $9.99 USD
- Billing cycle: Monthly
- Metadata: { tier: "gold" }
```

### 2. Firebase Access

#### Required Credentials

| Credential | Environment Variable | Where to Find | Format |
|-----------|---------------------|---------------|--------|
| Project ID | `FIREBASE_PROJECT_ID` | [Firebase Console > Project Settings](https://console.firebase.google.com/project/_/settings/general) | Plain text (e.g., `my-project-123`) |
| Service Account | `FIREBASE_SERVICE_ACCOUNT` | [Firebase Console > Project Settings > Service Accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts) | Base64-encoded JSON |

#### Setup Steps

1. Create Firebase project at https://console.firebase.google.com
2. Enable Authentication:
   - Go to Authentication > Sign-in method
   - Enable Email/Password and any other providers you need
3. Enable Firestore:
   - Go to Firestore Database > Create database
   - Start in production mode (you'll add security rules)
   - Deploy security rules from `docs/STRIPE_FIREBASE_INTEGRATION.md`
4. Enable Cloud Functions:
   - Go to Functions > Get started
   - Upgrade to Blaze plan (pay-as-you-go, required for external API calls)
5. Generate service account:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save JSON file securely
   - For CI: `cat service-account.json | base64 > service-account.base64`
   - Set `FIREBASE_SERVICE_ACCOUNT` environment variable to base64 content

#### Firebase Project Configuration

```javascript
// Web app config (public - can be committed)
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "my-project.firebaseapp.com",
  projectId: "my-project-123",
  storageBucket: "my-project-123.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

### 3. Android Signing (for APK generation)

#### Required for Signed Builds

| Credential | Environment Variable | Notes |
|-----------|---------------------|-------|
| Keystore File | `ANDROID_KEYSTORE` | Base64-encoded keystore file OR path to keystore |
| Keystore Password | `ANDROID_KEYSTORE_PASSWORD` | Password for keystore |
| Key Alias | `ANDROID_KEY_ALIAS` | Alias of the key in keystore |
| Key Password | `ANDROID_KEY_PASSWORD` | Password for the key |

#### Setup Steps

1. Generate keystore (if you don't have one):
   ```bash
   keytool -genkeypair -v \
     -keystore rag7-release.keystore \
     -alias rag7-key \
     -keyalg RSA \
     -keysize 2048 \
     -validity 10000
   ```

2. For CI, encode keystore:
   ```bash
   cat rag7-release.keystore | base64 > rag7-release.keystore.base64
   ```

3. Store passwords securely in CI environment variables

#### Alternative: CI Signing Services

Instead of managing keystores, consider using:
- **Google Play App Signing** (recommended for Play Store)
- **Fastlane Match** (for iOS and Android)
- **Azure DevOps Secure Files** (if using Azure Pipelines)

### 4. iOS Signing (for IPA generation, if applicable)

#### Required for Signed Builds

| Credential | Environment Variable | Notes |
|-----------|---------------------|-------|
| Certificate | `IOS_CERTIFICATE` | Base64-encoded .p12 certificate |
| Provisioning Profile | `IOS_PROVISIONING_PROFILE` | Base64-encoded .mobileprovision file |
| Certificate Password | `IOS_CERTIFICATE_PASSWORD` | Password for .p12 certificate |

## Environment Variables Reference

### Required for Development

```bash
# Stripe (Test Mode)
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Firebase
export FIREBASE_PROJECT_ID="my-project-123"
```

### Required for CI/CD

```bash
# Stripe
STRIPE_SECRET_KEY="sk_test_..." or "sk_live_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..." or "pk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Firebase
FIREBASE_PROJECT_ID="my-project-123"
FIREBASE_SERVICE_ACCOUNT="<base64-encoded JSON>"

# Android (if building APK)
ANDROID_KEYSTORE="<base64-encoded keystore>"
ANDROID_KEYSTORE_PASSWORD="your-password"
ANDROID_KEY_ALIAS="rag7-key"
ANDROID_KEY_PASSWORD="your-key-password"

# iOS (if building IPA)
IOS_CERTIFICATE="<base64-encoded .p12>"
IOS_PROVISIONING_PROFILE="<base64-encoded .mobileprovision>"
IOS_CERTIFICATE_PASSWORD="your-password"
```

### Setting in CI (GitHub Actions Example)

Go to: Repository Settings > Secrets and variables > Actions > New repository secret

Add each environment variable as a secret.

In your workflow file:

```yaml
env:
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
  STRIPE_PUBLISHABLE_KEY: ${{ secrets.STRIPE_PUBLISHABLE_KEY }}
  FIREBASE_PROJECT_ID: ${{ secrets.FIREBASE_PROJECT_ID }}
  # ... etc
```

## Build Steps

### Local Development

#### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

#### 2. Set Environment Variables

Create `.env.local` (add to `.gitignore`):

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
FIREBASE_PROJECT_ID=my-project-123
```

#### 3. Run Development Server

```bash
npm run dev
# or
yarn dev
```

#### 4. Test Firebase Functions Locally

```bash
cd functions
npm install

# Start emulators
firebase emulators:start --only functions

# In another terminal, forward Stripe webhooks
stripe listen --forward-to http://localhost:5001/YOUR_PROJECT/us-central1/stripeWebhooks/webhook
```

### Production Deployment

#### 1. Deploy Firebase Functions

```bash
# Set environment variables
firebase functions:config:set \
  stripe.secret_key="sk_live_..." \
  stripe.webhook_secret="whsec_..."

# Deploy
firebase deploy --only functions
```

#### 2. Deploy Firestore Rules

```bash
firebase deploy --only firestore:rules
```

#### 3. Deploy Web App (if using Firebase Hosting)

```bash
npm run build
firebase deploy --only hosting
```

### Building APK/ZIP

#### Android APK

```bash
# Debug build (no signing required)
cd android
./gradlew assembleDebug

# Release build (requires signing)
./gradlew assembleRelease

# Output: android/app/build/outputs/apk/release/app-release.apk
```

#### iOS IPA

```bash
# Requires Xcode and iOS signing certificates
cd ios
pod install

# Build archive
xcodebuild archive \
  -workspace RAG7.xcworkspace \
  -scheme RAG7 \
  -archivePath build/RAG7.xcarchive

# Export IPA
xcodebuild -exportArchive \
  -archivePath build/RAG7.xcarchive \
  -exportPath build \
  -exportOptionsPlist ExportOptions.plist
```

#### Web ZIP

```bash
npm run build
cd build
zip -r ../rag7-web.zip .
```

## Complete Setup Checklist

Use this checklist to track your progress:

### Stripe Setup
- [ ] Create Stripe account
- [ ] Obtain test API keys (secret and publishable)
- [ ] Create "Gold Membership" product in Stripe Dashboard
- [ ] Copy Price ID for gold membership
- [ ] Update code with correct Price ID

### Firebase Setup
- [ ] Create Firebase project
- [ ] Enable Firebase Authentication
- [ ] Enable Cloud Firestore
- [ ] Create Firestore indexes (if needed)
- [ ] Deploy Firestore security rules
- [ ] Upgrade to Blaze plan (for Cloud Functions)
- [ ] Generate service account JSON
- [ ] Store service account securely

### Integration Wiring
- [ ] Deploy `createCheckoutSession` Cloud Function
- [ ] Deploy `stripeWebhooks` Cloud Function
- [ ] Configure Stripe webhook endpoint in Dashboard
- [ ] Copy webhook signing secret
- [ ] Update Firebase config with webhook secret
- [ ] Test webhook delivery with Stripe CLI
- [ ] **Enable webhook signature verification in production**

### Client Application
- [ ] Add Firebase config to client app
- [ ] Implement authentication UI
- [ ] Integrate `ChannelLock` component
- [ ] Implement `createCheckout` function
- [ ] Test user flow: signup > upgrade > access premium channels
- [ ] Handle success/cancel redirects from Stripe Checkout

### Testing
- [ ] Test with Stripe test cards (4242 4242 4242 4242)
- [ ] Verify entitlements are written to Firestore
- [ ] Test real-time entitlement updates
- [ ] Test subscription cancellation flow
- [ ] Test payment failure scenarios
- [ ] Test refund handling (if applicable)

### CI/CD (if applicable)
- [ ] Set up CI environment variables
- [ ] Configure Android signing (if building APK)
- [ ] Configure iOS signing (if building IPA)
- [ ] Test build pipeline
- [ ] Automate deployment to Firebase Hosting (if applicable)

### Production Readiness
- [ ] Switch to live Stripe keys (`sk_live_`, `pk_live_`)
- [ ] Configure production webhook endpoint
- [ ] **Enable webhook signature verification** (CRITICAL!)
- [ ] Set up monitoring and alerts
- [ ] Review Stripe Radar settings (fraud prevention)
- [ ] Test production flow end-to-end with real payment
- [ ] Set up customer support process for billing issues

### Security Review
- [ ] Verify no secrets are committed to repository
- [ ] Confirm Firestore security rules are deployed
- [ ] Verify webhook signature verification is enabled
- [ ] Test authentication flows
- [ ] Review user permissions and access controls
- [ ] Enable Cloud Functions VPC (if needed for additional security)

## Troubleshooting

### Common Issues

#### "Stripe webhook signature verification failed"
- Check that `STRIPE_WEBHOOK_SECRET` is set correctly
- Verify you're using the correct secret for test/live mode
- Ensure webhook endpoint URL is correct (includes `/webhook` path)

#### "Firebase functions:config not found"
- Run `firebase functions:config:set stripe.secret_key="..."`
- Verify project is set: `firebase use PROJECT_ID`

#### "Permission denied" when writing to Firestore
- Check Firestore security rules
- Verify Cloud Functions are using Admin SDK (bypasses rules)
- Check IAM permissions for service account

#### Build fails with "signing configuration not found"
- Verify keystore file exists and is readable
- Check that all signing environment variables are set
- For CI, verify base64 decoding is working

## Next Steps After Setup

1. Test the complete user flow in test mode
2. Create documentation for your team
3. Set up monitoring dashboards (Firebase Console, Stripe Dashboard)
4. Configure email notifications for failed payments
5. Implement customer support tools (Stripe Customer Portal)
6. Plan for scaling (Firebase quotas, Stripe rate limits)
7. Set up backup and disaster recovery

## Resources

- [Stripe API Reference](https://stripe.com/docs/api)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Firebase Emulator Suite](https://firebase.google.com/docs/emulator-suite)
- [Android App Signing](https://developer.android.com/studio/publish/app-signing)
- [iOS Code Signing](https://developer.apple.com/support/code-signing/)

## Support Contacts

If you get stuck, reach out to:

- **Stripe Support**: https://support.stripe.com
- **Firebase Support**: https://firebase.google.com/support
- **Team Lead**: [Add contact info]
- **DevOps**: [Add contact info]

---

**Last Updated**: 2024-01-01
**Maintainer**: Development Team
