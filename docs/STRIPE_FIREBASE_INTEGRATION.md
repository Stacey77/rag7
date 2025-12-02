# Stripe + Firebase Integration Guide

This guide describes the end-to-end integration between Stripe (payments) and Firebase (authentication, database, hosting) for managing premium channel subscriptions.

## Architecture Overview

```
┌─────────────────┐
│   Client App    │
│  (React/Web)    │
└────────┬────────┘
         │
         │ 1. User clicks "Upgrade to Gold"
         │
         ▼
┌─────────────────┐
│ Firebase Auth   │
│  (User Login)   │
└────────┬────────┘
         │
         │ 2. Call createCheckoutSession()
         │
         ▼
┌─────────────────────────┐
│ Firebase Cloud Function │
│ createCheckoutSession() │
└────────┬────────────────┘
         │
         │ 3. Create Stripe Checkout Session
         │    (with firebase_uid in metadata)
         │
         ▼
┌─────────────────┐
│ Stripe Checkout │
│  (Payment Page) │
└────────┬────────┘
         │
         │ 4. User completes payment
         │
         ▼
┌─────────────────────┐
│  Stripe Webhooks    │
│ (checkout.session   │
│     .completed)     │
└────────┬────────────┘
         │
         │ 5. Webhook triggers Firebase Function
         │
         ▼
┌──────────────────────────┐
│ Firebase Cloud Function  │
│  stripeWebhooks()        │
└────────┬─────────────────┘
         │
         │ 6. Write entitlement to Firestore
         │
         ▼
┌─────────────────────────┐
│   Firestore Database    │
│ users/{uid}/entitlements│
└────────┬────────────────┘
         │
         │ 7. Client listens to Firestore
         │    (real-time updates)
         │
         ▼
┌─────────────────┐
│   Client App    │
│  (Shows Gold    │
│   Channels)     │
└─────────────────┘
```

## Firestore Schema

### Recommended Structure

```
firestore/
├── users/
│   └── {firebase_uid}/
│       ├── profile/
│       │   ├── email: string
│       │   ├── displayName: string
│       │   └── created_at: timestamp
│       │
│       └── entitlements/
│           └── {stripe_subscription_id}/
│               ├── tier: "gold" | "free"
│               ├── status: "active" | "canceled" | "past_due" | "unpaid"
│               ├── stripe_customer_id: string
│               ├── stripe_subscription_id: string
│               ├── subscription_start_date: timestamp
│               ├── subscription_end_date: timestamp
│               ├── created_at: timestamp
│               └── updated_at: timestamp
│
├── products/
│   └── {stripe_product_id}/
│       ├── name: string (e.g., "Gold Membership")
│       ├── description: string
│       ├── tier: "gold"
│       ├── stripe_product_id: string
│       └── prices/
│           └── {stripe_price_id}/
│               ├── amount: number (in cents)
│               ├── currency: string
│               ├── interval: "month" | "year"
│               └── stripe_price_id: string
```

### Example Documents

#### User Entitlement (Active Subscription)

```javascript
// users/abc123/entitlements/sub_1234567890
{
  tier: "gold",
  status: "active",
  stripe_customer_id: "cus_ABC123",
  stripe_subscription_id: "sub_1234567890",
  subscription_start_date: Timestamp(2024-01-01),
  subscription_end_date: Timestamp(2024-02-01),
  created_at: Timestamp(2024-01-01 10:30:00),
  updated_at: Timestamp(2024-01-01 10:30:00)
}
```

## Implementation Flow

### 1. Client-Side: Create Checkout Session

When user clicks "Upgrade to Gold", call a Firebase Cloud Function to create a Stripe Checkout Session:

```javascript
// src/utils/createCheckout.js
import { getFunctions, httpsCallable } from 'firebase/functions';
import { getAuth } from 'firebase/auth';

export async function createGoldCheckout() {
  const functions = getFunctions();
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    throw new Error('User must be logged in');
  }

  const createCheckoutSession = httpsCallable(functions, 'createCheckoutSession');
  
  const { data } = await createCheckoutSession({
    priceId: 'price_1234567890', // Your Stripe Price ID for Gold tier
    successUrl: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancelUrl: `${window.location.origin}/channels`,
  });

  // Redirect to Stripe Checkout
  window.location.href = data.url;
}
```

### 2. Backend: Create Checkout Session Function

Create a Firebase Cloud Function that creates Stripe Checkout Sessions:

```javascript
// functions/createCheckoutSession.js
const functions = require('firebase-functions');
const stripe = require('stripe')(functions.config().stripe.secret_key);
const admin = require('firebase-admin');

exports.createCheckoutSession = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated',
      'User must be authenticated'
    );
  }

  const { priceId, successUrl, cancelUrl } = data;
  const userId = context.auth.uid;

  // Get or create Stripe customer
  let customerId;
  const userDoc = await admin.firestore()
    .collection('users')
    .doc(userId)
    .get();

  if (userDoc.exists && userDoc.data().stripe_customer_id) {
    customerId = userDoc.data().stripe_customer_id;
  } else {
    const customer = await stripe.customers.create({
      email: context.auth.token.email,
      metadata: {
        firebase_uid: userId, // CRITICAL: Link Stripe customer to Firebase user
      },
    });
    customerId = customer.id;

    // Save customer ID to Firestore
    await admin.firestore()
      .collection('users')
      .doc(userId)
      .set({ stripe_customer_id: customerId }, { merge: true });
  }

  // Create Checkout Session
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    success_url: successUrl,
    cancel_url: cancelUrl,
    metadata: {
      firebase_uid: userId, // Also add to session metadata for redundancy
    },
  });

  return { url: session.url };
});
```

### 3. Stripe Dashboard: Create Products and Prices

1. Go to [Stripe Dashboard > Products](https://dashboard.stripe.com/products)
2. Click "Add product"
3. Fill in:
   - **Name**: "Gold Membership"
   - **Description**: "Access to all premium channels"
   - **Pricing**: $9.99/month (or your price)
   - **Billing period**: Monthly
4. Save and copy the **Price ID** (starts with `price_`)
5. Use this Price ID in your `createCheckoutSession` function

### 4. Webhook Handler: Process Subscription Events

The webhook handler (see `functions/stripe-webhooks/index.js`) automatically:

1. Receives events from Stripe
2. Verifies webhook signature (security)
3. Extracts Firebase UID from customer metadata
4. Writes entitlement to Firestore

### 5. Client-Side: Listen to Entitlements

Use real-time Firestore listeners to instantly show premium content:

```javascript
// src/hooks/useUserEntitlements.js
import { useState, useEffect } from 'react';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, onSnapshot, query, where } from 'firebase/firestore';

export function useUserEntitlements() {
  const [entitlements, setEntitlements] = useState({ tier: 'free', loading: true });

  useEffect(() => {
    const auth = getAuth();
    const db = getFirestore();

    const unsubscribeAuth = onAuthStateChanged(auth, (user) => {
      if (!user) {
        setEntitlements({ tier: 'free', loading: false });
        return;
      }

      // Listen to user's entitlements in real-time
      const entitlementsRef = collection(db, 'users', user.uid, 'entitlements');
      const q = query(entitlementsRef, where('status', '==', 'active'));

      const unsubscribeFirestore = onSnapshot(q, (snapshot) => {
        const hasGold = snapshot.docs.some((doc) => {
          const data = doc.data();
          // Check if subscription is still valid
          return (
            data.tier === 'gold' &&
            data.subscription_end_date?.toDate() > new Date()
          );
        });

        setEntitlements({
          tier: hasGold ? 'gold' : 'free',
          loading: false,
        });
      });

      return () => unsubscribeFirestore();
    });

    return () => unsubscribeAuth();
  }, []);

  return entitlements;
}
```

## Security: Firestore Rules

Protect user data with Firestore security rules:

```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read their own profile and entitlements
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      
      // Only Cloud Functions can write user data
      allow write: if false;
      
      match /entitlements/{entitlementId} {
        allow read: if request.auth != null && request.auth.uid == userId;
        allow write: if false; // Only webhooks (via Admin SDK) can write
      }
    }
    
    // Everyone can read products and prices
    match /products/{productId} {
      allow read: if true;
      allow write: if false; // Only admins via Admin SDK
      
      match /prices/{priceId} {
        allow read: if true;
        allow write: if false;
      }
    }
  }
}
```

**Deploy rules:**
```bash
firebase deploy --only firestore:rules
```

## Mapping Stripe Customer to Firebase UID

**Critical**: Always include the Firebase UID in customer metadata to link Stripe customers with Firebase users.

### When Creating Checkout Session:

```javascript
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  // ...
  metadata: {
    firebase_uid: userId, // Add Firebase UID here
  },
});
```

### When Creating Customer:

```javascript
const customer = await stripe.customers.create({
  email: user.email,
  metadata: {
    firebase_uid: user.uid, // Add Firebase UID here
  },
});
```

### In Webhook Handler:

```javascript
// Retrieve customer to get Firebase UID
const customer = await stripe.customers.retrieve(subscription.customer);
const firebaseUid = customer.metadata.firebase_uid;

if (!firebaseUid) {
  console.error('No firebase_uid in customer metadata!');
  return;
}

// Now write to Firestore using firebaseUid
await db.collection('users').doc(firebaseUid)
  .collection('entitlements').doc(subscription.id)
  .set({ /* ... */ });
```

## Testing the Integration

### 1. Use Stripe Test Mode

- Use test keys: `sk_test_...` and `pk_test_...`
- Use test cards: `4242 4242 4242 4242` (Visa), `4000 0025 0000 3155` (3D Secure)
- All test data is isolated from production

### 2. Test with Stripe CLI

Forward webhooks to your local development environment:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks
stripe listen --forward-to http://localhost:5001/YOUR_PROJECT/us-central1/stripeWebhooks/webhook

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
```

### 3. End-to-End Test Flow

1. ✅ User logs in with Firebase Auth
2. ✅ User clicks "Upgrade to Gold"
3. ✅ `createCheckoutSession()` function creates Stripe session
4. ✅ User redirected to Stripe Checkout
5. ✅ Use test card `4242 4242 4242 4242` to complete payment
6. ✅ Stripe sends `checkout.session.completed` webhook
7. ✅ Webhook function writes to Firestore
8. ✅ Client detects new entitlement via real-time listener
9. ✅ Premium channels unlock immediately

### 4. Verify Firestore Data

Check that entitlements are created correctly:

```bash
# Firebase console
https://console.firebase.google.com/project/YOUR_PROJECT/firestore

# Or via Firebase CLI
firebase firestore:get users/USER_ID/entitlements/SUBSCRIPTION_ID
```

## Production Checklist

Before going live:

- [ ] **Enable webhook signature verification** (see `functions/README.md`)
- [ ] Switch to live Stripe keys (`sk_live_...`, `pk_live_...`)
- [ ] Configure production webhook endpoint in Stripe Dashboard
- [ ] Deploy Firestore security rules
- [ ] Test with real payment methods (use small amounts)
- [ ] Set up monitoring and alerts for failed webhooks
- [ ] Review Stripe's [Going Live Checklist](https://stripe.com/docs/keys#test-live-modes)
- [ ] Enable Stripe Radar for fraud prevention
- [ ] Set up customer portal for subscription management

## Handling Edge Cases

### Customer Cancels Subscription

Stripe sends `customer.subscription.deleted` webhook:
- Webhook handler updates entitlement status to "canceled"
- Client checks `subscription_end_date` and revokes access after period ends

### Payment Fails on Renewal

Stripe sends `invoice.payment_failed` webhook:
- Subscription enters "past_due" status
- Optionally notify user via email (use Firebase Extensions: Trigger Email)
- After retry attempts, subscription may be canceled

### Customer Updates Payment Method

Stripe sends `customer.subscription.updated` webhook:
- No action needed if subscription remains active
- Update `subscription_end_date` if period changed

### Refunds

Stripe sends `charge.refunded` webhook:
- Manually handle if needed
- Consider revoking access immediately or at period end

## Customer Portal

Use Stripe Customer Portal to let users manage subscriptions:

```javascript
// functions/createPortalSession.js
exports.createPortalSession = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const userId = context.auth.uid;
  const userDoc = await admin.firestore().collection('users').doc(userId).get();
  const customerId = userDoc.data()?.stripe_customer_id;

  if (!customerId) {
    throw new functions.https.HttpsError('not-found', 'No Stripe customer found');
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: data.returnUrl || `${data.origin}/account`,
  });

  return { url: session.url };
});
```

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Subscriptions Documentation](https://stripe.com/docs/billing/subscriptions/overview)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Cloud Firestore](https://firebase.google.com/docs/firestore)
- [Firebase Cloud Functions](https://firebase.google.com/docs/functions)
- [Stripe Webhooks Best Practices](https://stripe.com/docs/webhooks/best-practices)

## Support

If you encounter issues:

1. Check Firebase Functions logs: `firebase functions:log`
2. Check Stripe webhook delivery attempts in Dashboard
3. Verify environment variables are set correctly
4. Test webhook signature verification locally with Stripe CLI
5. Review Firestore security rules

## Next Steps

1. Complete implementation of TODOs in source files
2. Set up Stripe Products and Prices in Dashboard
3. Configure webhook endpoint in Stripe Dashboard
4. Test end-to-end flow in test mode
5. Enable signature verification before production
6. Deploy to production with live keys
