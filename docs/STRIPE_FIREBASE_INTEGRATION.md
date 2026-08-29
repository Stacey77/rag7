# Stripe + Firebase Integration Guide

This document outlines the integration between Stripe (payment processing) and Firebase (backend services) for managing subscriptions and entitlements in the RAG7 application.

## Architecture Overview

```
Client App -> Cloud Function (Create Checkout Session) -> Stripe Checkout
                                                              |
                                                              v
                                                        Payment Success
                                                              |
                                                              v
                                              Stripe Webhook -> Cloud Function
                                                              |
                                                              v
                                                        Update Firestore
                                                              |
                                                              v
                                              Client Reads Entitlements
```

## Firestore Schema

### 1. User Document: `/users/{uid}`

Basic user profile information.

```json
{
  "uid": "firebase-user-id",
  "email": "user@example.com",
  "stripeCustomerId": "cus_...",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 2. Subscription Document: `/users/{uid}/subscriptions/{subscriptionId}`

Tracks active and past subscriptions for each user.

```json
{
  "subscriptionId": "sub_...",
  "status": "active",
  "priceId": "price_...",
  "productId": "prod_...",
  "currentPeriodStart": "2024-01-01T00:00:00Z",
  "currentPeriodEnd": "2024-02-01T00:00:00Z",
  "cancelAtPeriodEnd": false,
  "lastPaymentStatus": "succeeded",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

**Status Values:**
- `active`: Subscription is active and in good standing
- `past_due`: Payment failed, retrying
- `canceled`: Subscription was canceled
- `unpaid`: Payment failed after retries
- `trialing`: In free trial period

### 3. Entitlement Document: `/entitlements/{uid}`

User's current access tier (denormalized for fast reads).

```json
{
  "uid": "firebase-user-id",
  "tier": "gold",
  "grantedAt": "2024-01-01T00:00:00Z",
  "expiresAt": "2024-02-01T00:00:00Z",
  "source": "subscription",
  "metadata": {
    "subscriptionId": "sub_...",
    "priceId": "price_..."
  }
}
```

**Tier Values:**
- `free`: Default tier, no payment required
- `silver`: Mid-tier subscription
- `gold`: Premium tier subscription

## Integration Flow

### 1. Customer Creation

When a user signs up, create a Stripe customer and link it to Firebase:

**Client → Cloud Function:**
```javascript
// Cloud Function: createStripeCustomer
exports.createStripeCustomer = functions.auth.user().onCreate(async (user) => {
  const customer = await stripe.customers.create({
    email: user.email,
    metadata: {
      firebaseUid: user.uid  // CRITICAL: Store Firebase UID for mapping
    }
  });
  
  await admin.firestore().collection('users').doc(user.uid).set({
    stripeCustomerId: customer.id,
    email: user.email,
    createdAt: admin.firestore.FieldValue.serverTimestamp()
  });
});
```

### 2. Checkout Session Creation

When user clicks "Upgrade to Gold":

**Client → Cloud Function:**
```javascript
// Cloud Function: createCheckoutSession
exports.createCheckoutSession = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  const userId = context.auth.uid;
  const userDoc = await admin.firestore().collection('users').doc(userId).get();
  const customerId = userDoc.data().stripeCustomerId;
  
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    payment_method_types: ['card'],
    line_items: [{
      price: data.priceId, // e.g., 'price_gold_monthly'
      quantity: 1
    }],
    mode: 'subscription',
    success_url: 'https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}',
    cancel_url: 'https://yourapp.com/cancel'
  });
  
  return { sessionId: session.id };
});
```

**Client Implementation:**
```javascript
// React/JavaScript client
import { getFunctions, httpsCallable } from 'firebase/functions';
import { loadStripe } from '@stripe/stripe-js';

async function handleUpgradeClick() {
  const functions = getFunctions();
  const createCheckoutSession = httpsCallable(functions, 'createCheckoutSession');
  
  const { data } = await createCheckoutSession({ priceId: 'price_gold_monthly' });
  
  const stripe = await loadStripe('pk_test_...');
  await stripe.redirectToCheckout({ sessionId: data.sessionId });
}
```

### 3. Payment Processing

Stripe handles the entire payment flow:
- Collects payment details
- Processes payment
- Creates subscription
- Redirects to success URL

### 4. Webhook Handling

Stripe sends webhook events to your Cloud Function:

**Stripe → Cloud Function (`functions/stripe-webhooks/index.js`):**

Key events to handle:
- `customer.subscription.created`: Create subscription record
- `customer.subscription.updated`: Update subscription status
- `customer.subscription.deleted`: Cancel subscription
- `invoice.payment_succeeded`: Mark payment as successful
- `invoice.payment_failed`: Handle failed payment

**Implementation details in `functions/stripe-webhooks/index.js`**

### 5. Entitlement Updates

When subscription changes, update entitlements:

```javascript
async function updateEntitlements(firebaseUid, subscription) {
  const priceId = subscription.items.data[0].price.id;
  const tier = determineTierFromPriceId(priceId);
  
  await admin.firestore().collection('entitlements').doc(firebaseUid).set({
    uid: firebaseUid,
    tier: tier,
    grantedAt: admin.firestore.FieldValue.serverTimestamp(),
    expiresAt: new Date(subscription.current_period_end * 1000),
    source: 'subscription',
    metadata: {
      subscriptionId: subscription.id,
      priceId: priceId
    }
  }, { merge: true });
}

function determineTierFromPriceId(priceId) {
  // Map Stripe price IDs to tiers
  const tierMap = {
    'price_gold_monthly': 'gold',
    'price_gold_yearly': 'gold',
    'price_silver_monthly': 'silver',
    'price_silver_yearly': 'silver'
  };
  return tierMap[priceId] || 'free';
}
```

### 6. Client-Side Entitlement Checks

Client reads entitlements in real-time:

```javascript
import { getFirestore, doc, onSnapshot } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

function useUserEntitlements() {
  const [entitlement, setEntitlement] = useState(null);
  const [loading, setLoading] = useState(true);
  const auth = getAuth();
  
  useEffect(() => {
    if (!auth.currentUser) {
      setLoading(false);
      return;
    }
    
    const db = getFirestore();
    const entitlementRef = doc(db, 'entitlements', auth.currentUser.uid);
    
    const unsubscribe = onSnapshot(entitlementRef, (doc) => {
      setEntitlement(doc.exists() ? doc.data() : { tier: 'free' });
      setLoading(false);
    });
    
    return () => unsubscribe();
  }, [auth.currentUser]);
  
  return { ...entitlement, loading };
}
```

## Stripe Product Setup

Create products and prices in Stripe Dashboard:

### Products

1. **Gold Tier**
   - Name: "Gold Subscription"
   - Description: "Access to premium gold-tier channels"
   
2. **Silver Tier**
   - Name: "Silver Subscription"
   - Description: "Access to mid-tier channels"

### Prices

1. **Gold Monthly**: `price_gold_monthly` - $19.99/month
2. **Gold Yearly**: `price_gold_yearly` - $199.99/year
3. **Silver Monthly**: `price_silver_monthly` - $9.99/month
4. **Silver Yearly**: `price_silver_yearly` - $99.99/year

## Metadata Mapping

**CRITICAL**: Always include `firebaseUid` in Stripe customer metadata:

```javascript
const customer = await stripe.customers.create({
  email: user.email,
  metadata: {
    firebaseUid: user.uid  // Essential for mapping Stripe → Firebase
  }
});
```

This allows webhook handlers to identify which Firebase user to update.

## Security Considerations

### 1. Webhook Signature Verification

**Always verify webhook signatures** to ensure events are from Stripe:

```javascript
const event = stripe.webhooks.constructEvent(
  req.body,
  req.headers['stripe-signature'],
  process.env.STRIPE_WEBHOOK_SECRET
);
```

### 2. Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read their own data
    match /users/{userId} {
      allow read: if request.auth.uid == userId;
      allow write: if false; // Only Cloud Functions can write
    }
    
    match /users/{userId}/subscriptions/{subId} {
      allow read: if request.auth.uid == userId;
      allow write: if false; // Only Cloud Functions can write
    }
    
    match /entitlements/{userId} {
      allow read: if request.auth.uid == userId;
      allow write: if false; // Only Cloud Functions can write
    }
  }
}
```

### 3. Client-Side Entitlement Checks

Client-side checks (like `ChannelLock.stubs.jsx`) provide UX but are **not security**.

**Always enforce entitlements server-side:**
- Video stream URLs should be generated by Cloud Functions
- Functions should verify entitlements before returning stream URLs
- Use signed URLs or tokens with expiration

### 4. Environment Variables

**Never commit secrets to code**:
- Use Firebase Functions config: `firebase functions:config:set`
- Or use Secret Manager for sensitive data
- Access via `process.env` in functions

## Testing

### 1. Stripe Test Mode

Use test API keys for development:
- `sk_test_...` (secret key)
- `pk_test_...` (publishable key)

Test card numbers:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Auth required: `4000 0025 0000 3155`

### 2. Local Testing with Stripe CLI

```bash
# Forward webhooks to local function
stripe listen --forward-to http://localhost:5001/project-id/us-central1/stripeWebhook/webhook

# Trigger test events
stripe trigger customer.subscription.created
```

### 3. Integration Testing

1. Create test user in Firebase
2. Subscribe with test card
3. Verify Firestore updates
4. Check entitlement in client
5. Test channel access gating

## Monitoring and Alerts

1. **Firebase Console**: Monitor function invocations and errors
2. **Stripe Dashboard**: Track successful/failed payments
3. **Cloud Logging**: Set up log-based alerts for critical errors
4. **Metrics**: Track subscription conversions, churn rate

## Troubleshooting

### Issue: Subscription created but no entitlement

**Cause**: Webhook not received or failed to process

**Solution**:
1. Check webhook configuration in Stripe Dashboard
2. Verify function URL is correct
3. Check function logs for errors
4. Ensure `firebaseUid` is in customer metadata

### Issue: Payment succeeded but user doesn't see access

**Cause**: Client not refreshing entitlements

**Solution**:
1. Ensure client is subscribed to Firestore real-time updates
2. Check Firestore security rules allow read access
3. Verify entitlement document exists in Firestore

### Issue: Webhook signature verification fails

**Cause**: Incorrect webhook secret or raw body parsing

**Solution**:
1. Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
2. Ensure using `bodyParser.raw({ type: 'application/json' })`
3. Don't parse body before verification

## Additional Resources

- [Stripe Subscriptions Guide](https://stripe.com/docs/billing/subscriptions/overview)
- [Firebase Cloud Functions](https://firebase.google.com/docs/functions)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Stripe Webhooks Best Practices](https://stripe.com/docs/webhooks/best-practices)
