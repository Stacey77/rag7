# Stripe + Firebase Integration Guide

This document outlines the integration architecture between Stripe (payment processing) and Firebase (backend services) for subscription-based channel access.

## Overview

The integration enables:
- Subscription management through Stripe
- User entitlement tracking in Firestore
- Automated webhook processing to sync subscription state
- Client-side access control based on subscription tiers

## Architecture Flow

```
┌─────────┐      ┌──────────────┐      ┌────────┐      ┌──────────┐
│ Client  │─────>│ Cloud        │─────>│ Stripe │─────>│ Stripe   │
│ App     │      │ Function     │      │ API    │      │ Checkout │
└─────────┘      └──────────────┘      └────────┘      └──────────┘
     ↑                                                        │
     │                                                        ↓
     │           ┌──────────────┐      ┌────────┐      ┌──────────┐
     └───────────│  Firestore   │<─────│ Cloud  │<─────│ Webhook  │
                 │  Entitle-    │      │Function│      │ Event    │
                 │  ments       │      └────────┘      └──────────┘
                 └──────────────┘
```

### Flow Steps

1. **Client** requests subscription checkout session via Cloud Function
2. **Cloud Function** creates Stripe Checkout Session with customer metadata
3. **Stripe Checkout** handles payment UI and processing
4. **Stripe Webhooks** notify our webhook endpoint about events
5. **Webhook Function** processes events and updates Firestore
6. **Client** reads entitlements from Firestore in real-time

## Firestore Schema

### Collection: `/users/{uid}`

User profile and metadata.

```json
{
  "email": "user@example.com",
  "displayName": "John Doe",
  "stripeCustomerId": "cus_XXXXXXXXXX",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### Collection: `/users/{uid}/subscriptions/{subscriptionId}`

Individual subscription records.

```json
{
  "subscriptionId": "sub_XXXXXXXXXX",
  "status": "active",
  "tier": "gold",
  "priceId": "price_XXXXXXXXXX",
  "productId": "prod_XXXXXXXXXX",
  "currentPeriodStart": "2024-01-01T00:00:00Z",
  "currentPeriodEnd": "2024-02-01T00:00:00Z",
  "cancelAtPeriodEnd": false,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-15T00:00:00Z"
}
```

### Collection: `/entitlements/{uid}`

Denormalized entitlement data for fast client reads.

```json
{
  "tier": "gold",
  "validUntil": "2024-02-01T00:00:00Z",
  "subscriptionId": "sub_XXXXXXXXXX",
  "status": "active",
  "features": ["premium_channels", "hd_streaming", "offline_downloads"],
  "updatedAt": "2024-01-15T00:00:00Z"
}
```

**Why denormalize?** The `/entitlements/{uid}` collection provides a single document read for client access control, avoiding the need to query subcollections.

## Stripe Customer Metadata Mapping

When creating a Stripe Customer, include Firebase UID in metadata:

```javascript
const customer = await stripe.customers.create({
  email: user.email,
  metadata: {
    firebaseUid: user.uid,  // CRITICAL: Map Stripe customer to Firebase user
  },
});
```

This mapping allows webhook handlers to update the correct Firestore documents when Stripe events occur.

## Recommended Implementation Flow

### 1. Create Checkout Session (Client → Cloud Function)

**Client Code:**
```javascript
const createCheckoutSession = async (priceId) => {
  const response = await fetch('/api/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priceId }),
  });
  const { sessionId } = await response.json();
  
  const stripe = await loadStripe('YOUR_PUBLISHABLE_KEY');
  await stripe.redirectToCheckout({ sessionId });
};
```

**Cloud Function:**
```javascript
exports.createCheckoutSession = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'Must be logged in');
  }
  
  const { priceId } = data;
  const uid = context.auth.uid;
  const user = await admin.auth().getUser(uid);
  
  // Get or create Stripe customer
  let customerId = await getStripeCustomerId(uid);
  if (!customerId) {
    const customer = await stripe.customers.create({
      email: user.email,
      metadata: { firebaseUid: uid },
    });
    customerId = customer.id;
    await admin.firestore().collection('users').doc(uid).update({
      stripeCustomerId: customerId,
    });
  }
  
  // Create checkout session
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    mode: 'subscription',
    success_url: 'https://yourapp.com/success',
    cancel_url: 'https://yourapp.com/cancel',
  });
  
  return { sessionId: session.id };
});
```

### 2. Process Webhook Events

See `functions/stripe-webhooks/index.js` for webhook implementation.

Key events to handle:
- `customer.subscription.created` - Initialize subscription in Firestore
- `invoice.payment_succeeded` - Activate/renew entitlements
- `invoice.payment_failed` - Handle failed payments
- `customer.subscription.updated` - Update tier, status changes
- `customer.subscription.deleted` - Revoke entitlements

### 3. Client-Side Entitlement Checks

**React Hook:**
```javascript
const useUserEntitlements = () => {
  const [entitlements, setEntitlements] = useState(null);
  const { user } = useAuth();
  
  useEffect(() => {
    if (!user) return;
    
    const unsubscribe = firestore
      .collection('entitlements')
      .doc(user.uid)
      .onSnapshot(doc => {
        setEntitlements(doc.data());
      });
    
    return unsubscribe;
  }, [user]);
  
  return entitlements;
};
```

**Component Usage:**
```javascript
import ChannelLock from './components/ChannelLock.stubs';

const ChannelPlayer = ({ channel }) => {
  return (
    <ChannelLock channel={channel}>
      <VideoPlayer src={channel.stream} />
    </ChannelLock>
  );
};
```

## Security Considerations

### Webhook Signature Verification

**ALWAYS** verify webhook signatures to prevent spoofing:

```javascript
const event = stripe.webhooks.constructEvent(
  req.body,
  req.headers['stripe-signature'],
  process.env.STRIPE_WEBHOOK_SECRET
);
```

### Firestore Security Rules

Protect entitlement data with proper security rules:

```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read their own entitlements
    match /entitlements/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;  // Only Cloud Functions can write
    }
    
    // Users can read their own subscriptions
    match /users/{uid}/subscriptions/{subId} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false;  // Only Cloud Functions can write
    }
  }
}
```

### Environment Variables

- **NEVER** commit secrets to source control
- Use Firebase Functions config for secrets
- Use different keys for test/production environments
- Rotate webhook secrets periodically

## Subscription Tiers

Define tiers based on Stripe Products/Prices:

| Tier   | Price ID           | Features                                    |
|--------|-------------------|---------------------------------------------|
| Free   | N/A               | Basic channels, SD quality                  |
| Silver | `price_silver_*`  | Premium channels, HD quality                |
| Gold   | `price_gold_*`    | All channels, HD + 4K, offline downloads    |

Map price IDs to tiers in webhook handlers:

```javascript
const TIER_MAPPING = {
  'price_silver_monthly': 'silver',
  'price_silver_yearly': 'silver',
  'price_gold_monthly': 'gold',
  'price_gold_yearly': 'gold',
};

const tier = TIER_MAPPING[subscription.items.data[0].price.id] || 'free';
```

## Testing

### Test Mode

1. Use Stripe test mode (keys starting with sk_test_ and pk_test_)
2. Use test card: `4242 4242 4242 4242`
3. Use Stripe CLI to trigger webhook events locally

### Webhook Testing

```bash
stripe listen --forward-to https://YOUR_FUNCTION_URL/webhook
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
```

## Production Checklist

- [ ] Switch to live Stripe keys (starts with sk_live_ and pk_live_)
- [ ] Update webhook endpoint URL in Stripe Dashboard
- [ ] Configure production webhook secret
- [ ] Set up Firestore Security Rules
- [ ] Enable Firestore backup and point-in-time recovery
- [ ] Set up monitoring and alerting for failed payments
- [ ] Test subscription flows in production environment
- [ ] Document customer support procedures for subscription issues

## Troubleshooting

### Webhooks Not Received

- Verify webhook URL is correct and publicly accessible
- Check Stripe Dashboard → Webhooks for delivery status
- Review Cloud Function logs: `firebase functions:log`

### Entitlements Not Updating

- Check webhook signature verification passes
- Verify customer metadata includes `firebaseUid`
- Check Firestore permissions and rules
- Review Cloud Function logs for errors

### Payment Fails but Subscription Created

- This is normal - Stripe may retry
- Handle `invoice.payment_failed` to notify user
- Implement grace period logic if desired

## References

- [Stripe API Documentation](https://stripe.com/docs/api)
- [Firebase Cloud Functions](https://firebase.google.com/docs/functions)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Best Practices](https://stripe.com/docs/webhooks/best-practices)
