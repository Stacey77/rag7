# Developer Notes - Credentials and CI Configuration

This document provides a checklist for maintainers to configure required credentials and environment variables for CI/CD, development, and production deployment.

## Required Credentials

### Stripe Credentials

#### Test Environment
- **STRIPE_TEST_SECRET**: Stripe test secret key (starts with `sk_test_`)
  - Source: Stripe Dashboard → Developers → API keys → Test mode
  - Used for: Development and staging environments
  
- **STRIPE_TEST_PUBLISHABLE**: Stripe test publishable key (starts with `pk_test_`)
  - Source: Stripe Dashboard → Developers → API keys → Test mode
  - Used for: Client-side checkout initialization in test mode

#### Production Environment
- **STRIPE_LIVE_SECRET**: Stripe live secret key (starts with `sk_live_`)
  - Source: Stripe Dashboard → Developers → API keys → Live mode
  - Used for: Production payment processing
  - ⚠️ **CRITICAL**: Never commit this to version control

- **STRIPE_LIVE_PUBLISHABLE**: Stripe live publishable key (starts with `pk_live_`)
  - Source: Stripe Dashboard → Developers → API keys → Live mode
  - Used for: Client-side checkout initialization in production

#### Webhook Secret
- **STRIPE_WEBHOOK_SECRET**: Webhook signing secret (starts with `whsec_`)
  - Source: Stripe Dashboard → Developers → Webhooks → Select endpoint → Signing secret
  - Used for: Verifying webhook authenticity
  - Note: Different secrets for test and live mode webhooks

### Firebase Credentials

- **FIREBASE_SERVICE_ACCOUNT**: Service account JSON (base64 encoded)
  - Source: Firebase Console → Project Settings → Service Accounts → Generate new private key
  - Format: Base64-encoded JSON string
  - Used for: Firebase Admin SDK initialization, Firestore access, Cloud Functions deployment
  - Encoding: `cat service-account.json | base64`
  - ⚠️ **CRITICAL**: Never commit raw JSON to version control

- **FIREBASE_PROJECT_ID**: Firebase project identifier
  - Source: Firebase Console → Project Settings → Project ID
  - Example: `my-app-12345`
  - Used for: Firebase initialization, deployment targeting

### Android Build Credentials (Optional)

Required only if building signed Android APKs:

- **ANDROID_KEYSTORE**: Android keystore file (base64 encoded)
  - Source: Generate with `keytool` or existing keystore
  - Format: Base64-encoded binary keystore file
  - Encoding: `cat keystore.jks | base64`
  
- **KEY_ALIAS**: Keystore key alias
  - Example: `my-app-release-key`
  
- **KEYSTORE_PASSWORD**: Password for the keystore
  
- **KEY_PASSWORD**: Password for the specific key

## CI/CD Environment Variable Configuration

### GitHub Actions Secrets

Configure in: Repository Settings → Secrets and variables → Actions

```yaml
# Stripe credentials
STRIPE_TEST_SECRET: sk_test_...
STRIPE_TEST_PUBLISHABLE: pk_test_...
STRIPE_LIVE_SECRET: sk_live_...
STRIPE_LIVE_PUBLISHABLE: pk_live_...
STRIPE_WEBHOOK_SECRET: whsec_...

# Firebase credentials
FIREBASE_SERVICE_ACCOUNT: <base64-encoded-json>
FIREBASE_PROJECT_ID: my-app-12345

# Android credentials (optional)
ANDROID_KEYSTORE: <base64-encoded-keystore>
KEY_ALIAS: my-app-release-key
KEYSTORE_PASSWORD: ***
KEY_PASSWORD: ***
```

### Firebase Functions Configuration

For Firebase Cloud Functions, set via Firebase CLI:

```bash
# Development/Test
firebase use dev  # Switch to dev project
firebase functions:config:set \
  stripe.secret_key="sk_test_..." \
  stripe.webhook_secret="whsec_..."

# Production
firebase use prod  # Switch to prod project
firebase functions:config:set \
  stripe.secret_key="sk_live_..." \
  stripe.webhook_secret="whsec_..."
```

View current config:
```bash
firebase functions:config:get
```

## Deployment Steps

### Initial Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/Stacey77/rag7.git
   cd rag7
   ```

2. **Install dependencies**
   ```bash
   npm install
   cd functions && npm install && cd ..
   ```

3. **Configure Firebase**
   ```bash
   firebase login
   firebase use --add  # Select your project
   ```

### Staging Deployment

1. **Set test credentials**
   ```bash
   firebase functions:config:set \
     stripe.secret_key="$STRIPE_TEST_SECRET" \
     stripe.webhook_secret="$STRIPE_WEBHOOK_SECRET"
   ```

2. **Deploy to staging**
   ```bash
   firebase use staging
   firebase deploy --only functions
   ```

3. **Configure Stripe webhook**
   - Get function URL from deploy output
   - Add webhook endpoint in Stripe Dashboard (test mode)
   - Update `STRIPE_WEBHOOK_SECRET` if needed

4. **Verify deployment**
   - Test checkout flow with test card
   - Verify webhook events are received
   - Check Firestore for subscription records
   - Confirm entitlements are updated

### Production Deployment

1. **Verify staging works**
   - Complete end-to-end testing
   - Verify all webhook events
   - Check error handling

2. **Set production credentials**
   ```bash
   firebase use production
   firebase functions:config:set \
     stripe.secret_key="$STRIPE_LIVE_SECRET" \
     stripe.webhook_secret="$STRIPE_WEBHOOK_SECRET"
   ```

3. **Deploy to production**
   ```bash
   firebase deploy --only functions
   ```

4. **Configure Stripe webhook (live mode)**
   - Add webhook endpoint with production URL
   - Copy new signing secret
   - Update function config if secret changed

5. **Production verification**
   - Monitor Firebase Functions logs
   - Check Stripe Dashboard for events
   - Verify Firestore updates
   - Test with small transaction first

## Opening Draft PR

### Step 1: Push Changes

```bash
git checkout -b feature/stripe-firebase-integration
git add .
git commit -m "Add channel dataset and Stripe + Firebase billing integration stubs"
git push origin feature/stripe-firebase-integration
```

### Step 2: Create Draft PR

Via GitHub CLI:
```bash
gh pr create --draft --title "Add channel dataset and Stripe + Firebase billing integration" \
  --body-file .github/PR_TEMPLATE.md
```

Or via GitHub UI:
- Go to repository → Pull Requests → New Pull Request
- Select branch: `feature/stripe-firebase-integration`
- Click "Create pull request"
- Check "Create as draft"

### Step 3: Add Checklist to PR Description

Include this checklist in the PR body:

```markdown
## Maintainer Checklist

- [ ] Confirm gold-tier channel ids (26, 33, 36, 40) or provide additional IDs to mark gold
- [ ] Provide Stripe test keys or invite a Stripe user so products/prices can be created
- [ ] Provide Firebase service account or grant deployer permissions for functions and Firestore
- [ ] Provide CI signing access or keystore for APK generation if you want a signed build
- [ ] Review code for security issues (no hardcoded secrets)
- [ ] Test checkout flow in Stripe test mode
- [ ] Verify webhook signature verification is enabled
- [ ] Deploy functions to staging and verify
- [ ] Configure Firestore security rules
- [ ] Set up monitoring and alerting
```

## Security Reminders

### DO NOT Commit
- ❌ Service account JSON files
- ❌ Stripe secret keys
- ❌ Webhook signing secrets
- ❌ Keystore files or passwords
- ❌ `.env` files with real credentials

### DO Commit
- ✅ Example `.env.example` files (with placeholder values)
- ✅ Documentation about required credentials
- ✅ Code that reads from `process.env`
- ✅ Setup scripts (without credentials)

### Credential Rotation

If credentials are exposed:
1. **Immediately revoke** in respective dashboard
2. **Generate new credentials**
3. **Update** in CI/CD and Firebase config
4. **Redeploy** functions with new credentials
5. **Test** to ensure functionality

## Troubleshooting

### Webhook not receiving events
- Check Stripe Dashboard → Webhooks → Delivery attempts
- Verify function URL is correct
- Check Firebase Functions logs for errors
- Ensure webhook secret matches

### Payment succeeded but entitlements not updated
- Check Firebase Functions logs for errors
- Verify customer metadata includes `firebaseUid`
- Check Firestore security rules allow function writes
- Verify Firebase Admin SDK is initialized

### Function deployment fails
- Check Firebase billing is enabled
- Verify service account has necessary permissions
- Ensure all dependencies are in `package.json`
- Check Node.js version compatibility

## Next Steps After PR Approval

1. **Stripe Product Setup**
   - Create products and prices in Stripe Dashboard
   - Note price IDs for client integration
   - Configure billing intervals (monthly/yearly)

2. **Frontend Integration**
   - Implement checkout button/flow
   - Add entitlement checks to UI
   - Handle checkout success/cancel pages
   - Display subscription management

3. **Backend Completion**
   - Implement TODO sections in webhook handlers
   - Add customer portal session creation
   - Implement subscription cancellation flow
   - Add usage metering (if needed)

4. **Testing & Monitoring**
   - End-to-end testing with test cards
   - Load testing webhook handlers
   - Set up error monitoring (Sentry, etc.)
   - Configure alerts for failed payments

5. **Documentation**
   - API documentation for checkout functions
   - User guide for subscription management
   - Internal runbook for common issues
   - Disaster recovery procedures

## Contact & Support

For access to credentials:
- Stripe: Contact project owner for Dashboard invite
- Firebase: Request IAM permissions for project
- CI/CD: Request repository admin access for secrets

## References

- [Stripe API Documentation](https://stripe.com/docs/api)
- [Firebase Functions Setup](https://firebase.google.com/docs/functions/get-started)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Android App Signing](https://developer.android.com/studio/publish/app-signing)
