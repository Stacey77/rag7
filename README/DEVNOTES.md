# Developer Notes & Credentials Checklist

This document outlines the credentials, environment variables, and deployment steps required for the RAG7 project.

## Required Credentials & Environment Variables

### Stripe (Payment Processing)

#### Test Environment
- **STRIPE_TEST_SECRET**: Stripe test secret key (starts with `sk_test_`)
- **STRIPE_TEST_PUBLISHABLE**: Stripe test publishable key (starts with `pk_test_`)
- **STRIPE_WEBHOOK_SECRET**: Webhook signing secret for test mode (starts with `whsec_`)

#### Production Environment
- **STRIPE_LIVE_SECRET**: Stripe live secret key (starts with `sk_live_`)
- **STRIPE_LIVE_PUBLISHABLE**: Stripe live publishable key (starts with `pk_live_`)
- **STRIPE_WEBHOOK_SECRET**: Webhook signing secret for live mode (starts with `whsec_`)

**How to Obtain:**
1. Create account at https://dashboard.stripe.com
2. Navigate to Developers → API keys
3. Copy test/live keys
4. For webhook secret: Developers → Webhooks → Add endpoint → Copy signing secret

### Firebase (Backend Services)

- **FIREBASE_SERVICE_ACCOUNT**: Firebase service account JSON (base64 encoded)
- **FIREBASE_PROJECT_ID**: Firebase project identifier

**How to Obtain:**
1. Go to Firebase Console: https://console.firebase.google.com
2. Select project → Project Settings (gear icon)
3. Service Accounts tab → Generate new private key
4. Download JSON file
5. Base64 encode for CI: `cat serviceAccount.json | base64 -w 0`
6. Project ID is visible in Project Settings → General

**Firebase Functions Config:**
```bash
# Set for deployment
firebase functions:config:set stripe.secret_key="sk_test_..."
firebase functions:config:set stripe.webhook_secret="whsec_..."
```

### Android Signing (Optional - for APK generation)

- **ANDROID_KEYSTORE**: Keystore file (base64 encoded)
- **KEY_ALIAS**: Alias name in keystore
- **KEYSTORE_PASSWORD**: Password for keystore
- **KEY_PASSWORD**: Password for key

**How to Generate:**
```bash
# Generate new keystore
keytool -genkey -v -keystore release.keystore \
  -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# Base64 encode for CI
cat release.keystore | base64 -w 0
```

## CI/CD Configuration

### GitHub Actions Secrets

Add these secrets in GitHub repository settings (Settings → Secrets and variables → Actions):

```
STRIPE_TEST_SECRET
STRIPE_TEST_PUBLISHABLE
STRIPE_LIVE_SECRET
STRIPE_LIVE_PUBLISHABLE
STRIPE_WEBHOOK_SECRET
FIREBASE_SERVICE_ACCOUNT
FIREBASE_PROJECT_ID
ANDROID_KEYSTORE (optional)
KEY_ALIAS (optional)
KEYSTORE_PASSWORD (optional)
KEY_PASSWORD (optional)
```

### Example CI Configuration

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Firebase Service Account
        run: |
          echo "${{ secrets.FIREBASE_SERVICE_ACCOUNT }}" | base64 -d > serviceAccount.json
          export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/serviceAccount.json"
      
      - name: Deploy Firebase Functions
        run: |
          npm install -g firebase-tools
          firebase functions:config:set \
            stripe.secret_key="${{ secrets.STRIPE_LIVE_SECRET }}" \
            stripe.webhook_secret="${{ secrets.STRIPE_WEBHOOK_SECRET }}"
          firebase deploy --only functions --project ${{ secrets.FIREBASE_PROJECT_ID }}
```

## Maintainer Checklist

### Initial Setup

- [ ] **Confirm gold-tier channel ids**: Verify IDs 26, 33, 36, 40 are correct or provide additional gold-tier channels
- [ ] **Stripe Access**:
  - [ ] Invite maintainer to Stripe account, OR
  - [ ] Provide test API keys (`sk_test_...`, `pk_test_...`)
  - [ ] Provide live API keys when ready for production
- [ ] **Firebase Access**:
  - [ ] Invite maintainer as Firebase project editor, OR
  - [ ] Provide service account JSON with appropriate permissions
  - [ ] Grant Cloud Functions deployment permissions
  - [ ] Grant Firestore read/write permissions
- [ ] **CI Signing** (if APK builds are needed):
  - [ ] Provide Android keystore, OR
  - [ ] Provide signing credentials (alias, passwords), OR
  - [ ] Grant CI access to signing service

### Stripe Product Configuration

- [ ] Create products in Stripe Dashboard:
  - [ ] Gold Subscription (monthly & yearly)
  - [ ] Silver Subscription (monthly & yearly)
- [ ] Note down price IDs:
  - [ ] `price_gold_monthly`: $________/month
  - [ ] `price_gold_yearly`: $________/year
  - [ ] `price_silver_monthly`: $________/month
  - [ ] `price_silver_yearly`: $________/year
- [ ] Update price IDs in code (document location when implemented)

### Webhook Configuration

- [ ] Deploy webhook function to Firebase
- [ ] Copy Cloud Function URL (e.g., `https://us-central1-PROJECT.cloudfunctions.net/stripeWebhook/webhook`)
- [ ] Add webhook endpoint in Stripe Dashboard:
  - [ ] URL: [Function URL]
  - [ ] Events: `invoice.*`, `customer.subscription.*`
  - [ ] Copy webhook signing secret
  - [ ] Update Firebase functions config with webhook secret

### Testing Checklist

- [ ] **Unit Tests**: Run existing test suite
- [ ] **Integration Tests**:
  - [ ] Create test user
  - [ ] Subscribe with test card (`4242 4242 4242 4242`)
  - [ ] Verify subscription appears in Firestore
  - [ ] Verify entitlement updates
  - [ ] Check channel access gating works
  - [ ] Test subscription cancellation
  - [ ] Test payment failure handling
- [ ] **End-to-End Test**:
  - [ ] Full user journey from signup to paid subscription
  - [ ] Verify all webhook events are processed
  - [ ] Check logs for errors

## Deployment Process

### Staging Deployment

1. **Open Draft PR**:
   ```bash
   git checkout -b feature/billing-integration
   # (files already added in this PR)
   git push origin feature/billing-integration
   # Open as Draft PR in GitHub
   ```

2. **Configure Staging Environment**:
   ```bash
   # Select staging Firebase project
   firebase use staging
   
   # Set test credentials
   firebase functions:config:set \
     stripe.secret_key="sk_test_..." \
     stripe.webhook_secret="whsec_test_..."
   
   # Deploy functions
   firebase deploy --only functions
   ```

3. **Verify Staging**:
   - Test with Stripe test cards
   - Check webhook processing
   - Verify Firestore updates
   - Test client-side gating

4. **Review Draft PR**:
   - Request code review
   - Address feedback
   - Update documentation as needed

### Production Promotion

1. **Pre-Production Checklist**:
   - [ ] All tests passing
   - [ ] Code review approved
   - [ ] Staging environment verified
   - [ ] Production credentials obtained
   - [ ] Backup plan documented

2. **Configure Production Environment**:
   ```bash
   # Select production Firebase project
   firebase use production
   
   # Set live credentials
   firebase functions:config:set \
     stripe.secret_key="sk_live_..." \
     stripe.webhook_secret="whsec_live_..."
   
   # Deploy functions
   firebase deploy --only functions
   ```

3. **Update Stripe Webhook**:
   - Add production webhook URL in Stripe Dashboard (live mode)
   - Verify webhook is active
   - Test with small real transaction

4. **Monitor Production**:
   - Watch Cloud Functions logs
   - Monitor Stripe Dashboard for successful payments
   - Check error rates
   - Set up alerts for failures

5. **Merge PR**:
   - Convert from Draft to Ready for Review
   - Get final approval
   - Merge to main branch
   - Tag release version

## Rollback Procedure

If issues arise in production:

1. **Immediate Rollback**:
   ```bash
   # Revert to previous function version
   firebase functions:rollback
   ```

2. **Disable Webhook** (if needed):
   - Pause webhook in Stripe Dashboard
   - Prevents new events from processing

3. **Investigate**:
   - Check Cloud Functions logs
   - Review Stripe webhook attempts
   - Identify root cause

4. **Fix and Redeploy**:
   - Fix issue in code
   - Test in staging
   - Deploy to production
   - Re-enable webhook

## Support and Resources

### Documentation
- Stripe API: https://stripe.com/docs/api
- Firebase: https://firebase.google.com/docs
- Firestore: https://firebase.google.com/docs/firestore
- Cloud Functions: https://firebase.google.com/docs/functions

### Contact
- **Stripe Support**: https://support.stripe.com
- **Firebase Support**: https://firebase.google.com/support

### Internal
- **Team Lead**: [Name/Email]
- **DevOps**: [Name/Email]
- **Security**: [Name/Email]

## Security Notes

### Secret Management
- **Never commit secrets** to version control
- Use Firebase Functions config or Secret Manager
- Rotate keys periodically (every 6-12 months)
- Immediately rotate if compromised

### Access Control
- Limit Stripe dashboard access to essential team members
- Use role-based access in Firebase
- Enable 2FA for all team accounts
- Review access permissions quarterly

### Compliance
- Follow PCI DSS guidelines (Stripe handles card data)
- Ensure GDPR compliance for EU users
- Document data retention policies
- Regular security audits

## TODO: Manual Configuration Required

After this PR is merged, the following manual steps are required:

1. **Stripe Product Setup**: Create products and prices in Stripe Dashboard
2. **Webhook Secret Insertion**: Configure webhook secret in Firebase functions config
3. **Firebase Deployment**: Deploy Cloud Functions with proper permissions
4. **Stream Licensing**: Replace placeholder streams with licensed feed URLs
5. **Channel Data Review**: Verify channel metadata accuracy
6. **Security Rules**: Update Firestore security rules as documented
7. **CI Pipeline**: Configure GitHub Actions with required secrets

## Next Steps

After obtaining access and credentials:

1. Review this checklist and mark items as completed
2. Follow "Staging Deployment" process
3. Test thoroughly in staging
4. Schedule production deployment with team
5. Update this document with actual values (where appropriate)
6. Document any issues or learnings for future reference
