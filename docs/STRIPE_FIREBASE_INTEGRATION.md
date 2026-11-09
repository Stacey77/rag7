# Stripe + Firebase Integration Guide

This document outlines the integration architecture for subscription billing using Stripe and Firebase.

## Architecture Overview

```
Client App → Firebase Function → Stripe Checkout → Stripe Webhooks → Firestore → Client App
```

### Flow Diagram

1. **User initiates checkout**: Client calls Firebase Function to create checkout session
2. **Checkout session created**: Function returns Stripe Checkout URL
3. **User completes payment**: Stripe processes payment and triggers webhooks
4. **Webhook updates Firestore**: Function updates subscription and entitlement records
5. **Client reads entitlements**: App queries Firestore for user's current tier

## Firestore Schema

### /users/{uid}

User profile and account information.

```json
{
  "email": "user@example.com",
  "displayName": "John Doe",
  "stripeCustomerId": "cus_...",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### /users/{uid}/subscriptions/{subId}

Individual subscription records (user can have multiple subscriptions).

```json
{
  "subscriptionId": "sub_...",
  "priceId": "price_...",
  "productId": "prod_...",
  "status": "active",
  "tier": "gold",
  "currentPeriodStart": "2024-01-01T00:00:00Z",
  "currentPeriodEnd": "2024-02-01T00:00:00Z",
  "cancelAtPeriodEnd": false,
  "lastPayment": "2024-01-01T00:00:00Z",
  "amountPaid": 1999,
  "currency": "usd",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### /entitlements/{uid}

User's current access level (computed from active subscriptions).

```json
{
  "userId": "firebase-uid-123",
  "tier": "gold",
  "validUntil": "2024-02-01T00:00:00Z",
  "features": ["premium_channels", "hd_streaming", "offline_download"],
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

## Stripe Customer Metadata

To link Stripe customers with Firebase users, store the Firebase UID in Stripe customer metadata:

```javascript
const customer = await stripe.customers.create({
  email: user.email,
  metadata: {
    firebaseUid: user.uid
  }
});
```

This allows webhook handlers to map Stripe events to the correct Firebase user.

## Implementation Flow

### 1. Create Checkout Session (Client → Function)

**Client Side:**

```javascript
// Call Firebase Function to create checkout session
const createCheckout = httpsCallable(functions, 'createCheckoutSession');
const result = await createCheckout({ priceId: 'price_gold_tier' });

// Redirect to Stripe Checkout
window.location.href = result.data.url;
```

**Function Side (functions/createCheckout/index.js):**

```javascript
exports.createCheckoutSession = functions.https.onCall(async (data, context) => {
  // Verify user is authenticated
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'Must be logged in');
  }
  
  const uid = context.auth.uid;
  const { priceId } = data;
  
  // Get or create Stripe customer
  let customerId;
  const userDoc = await db.collection('users').doc(uid).get();
  
  if (userDoc.exists && userDoc.data().stripeCustomerId) {
    customerId = userDoc.data().stripeCustomerId;
  } else {
    const customer = await stripe.customers.create({
      email: context.auth.token.email,
      metadata: { firebaseUid: uid }
    });
    customerId = customer.id;
    
    await db.collection('users').doc(uid).set({
      stripeCustomerId: customerId
    }, { merge: true });
  }
  
  // Create checkout session
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.DOMAIN}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.DOMAIN}/cancel`,
    metadata: { firebaseUid: uid }
  });
  
  return { url: session.url };
});
```

### 2. Stripe Processes Payment

User completes payment on Stripe-hosted checkout page. Stripe handles:
- Payment collection
- 3D Secure authentication
- Subscription creation
- Automatic invoicing

### 3. Webhook Updates Firestore

See `functions/stripe-webhooks/index.js` for webhook implementation.

Key events:
- `customer.subscription.created`: Create subscription record
- `invoice.payment_succeeded`: Mark subscription as active, update entitlements
- `customer.subscription.updated`: Update subscription details
- `invoice.payment_failed`: Mark as past_due, handle grace period
- `customer.subscription.deleted`: Downgrade entitlements

### 4. Client Reads Entitlements

**React Hook Example:**

```javascript
import { doc, onSnapshot } from 'firebase/firestore';
import { useEffect, useState } from 'react';

function useUserEntitlements(uid) {
  const [entitlement, setEntitlement] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (!uid) return;
    
    const entitlementRef = doc(db, 'entitlements', uid);
    const unsubscribe = onSnapshot(entitlementRef, (snap) => {
      setEntitlement(snap.exists() ? snap.data() : null);
      setLoading(false);
    });
    
    return unsubscribe;
  }, [uid]);
  
  return { entitlement, loading };
}
```

## Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read their own profile
    match /users/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if request.auth != null && request.auth.uid == uid;
      
      // Users can read their own subscriptions
      match /subscriptions/{subId} {
        allow read: if request.auth != null && request.auth.uid == uid;
        allow write: if false; // Only functions can write
      }
    }
    
    // Users can only read their own entitlements
    match /entitlements/{uid} {
      allow read: if request.auth != null && request.auth.uid == uid;
      allow write: if false; // Only functions can write
    }
  }
}
```

## Tier Configuration

Define subscription tiers and their access levels:

```javascript
const TIER_CONFIG = {
  free: {
    level: 0,
    features: ['basic_channels', 'sd_streaming']
  },
  silver: {
    level: 1,
    features: ['basic_channels', 'hd_streaming', 'some_premium_channels']
  },
  gold: {
    level: 2,
    features: ['all_channels', 'hd_streaming', 'uhd_streaming', 'offline_download', 'concurrent_streams_5']
  }
};
```

Map Stripe price IDs to tiers:

```javascript
const PRICE_TO_TIER = {
  'price_silver_monthly': 'silver',
  'price_silver_yearly': 'silver',
  'price_gold_monthly': 'gold',
  'price_gold_yearly': 'gold'
};
```

## Security Notes

### Critical Security Requirements

1. **Webhook Signature Verification**: ALWAYS verify webhook signatures to prevent fake events
2. **Server-Side Validation**: NEVER trust client-side tier claims - always read from Firestore
3. **Firestore Rules**: Ensure only Cloud Functions can write entitlements
4. **Environment Variables**: Store all secrets in Firebase Functions config, never in code
5. **Customer Mapping**: Always use `metadata.firebaseUid` to map Stripe customers to Firebase users

### Best Practices

- Use idempotency keys for Stripe API calls to prevent duplicate charges
- Implement proper error handling and logging
- Set up monitoring and alerts for payment failures
- Provide clear user communication about subscription status
- Implement grace periods for failed payments
- Test thoroughly with Stripe test mode before going live

## Testing

### Test Cards (Stripe Test Mode)

- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

### Test Webhooks

Use Stripe CLI to trigger test events:

```bash
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

## Production Checklist

- [ ] Stripe account verified and live mode enabled
- [ ] Products and prices created in Stripe Dashboard
- [ ] Webhook endpoint configured with live signing secret
- [ ] Firebase Functions deployed with production credentials
- [ ] Firestore security rules deployed
- [ ] Environment variables set for production
- [ ] Test checkout flow end-to-end
- [ ] Monitor webhook delivery and function logs
- [ ] Set up error alerting
- [ ] Document recovery procedures for failed webhooks

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Firebase Functions Documentation](https://firebase.google.com/docs/functions)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
