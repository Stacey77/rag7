const express = require('express');
const bodyParser = require('body-parser');

/**
 * Stripe Webhooks Handler for Firebase Cloud Functions
 * 
 * This Express app receives Stripe webhook events and updates Firestore accordingly.
 * 
 * Environment Variables Required:
 * - STRIPE_SECRET_KEY: Your Stripe secret key (sk_test_... or sk_live_...)
 * - STRIPE_WEBHOOK_SECRET: Your webhook signing secret (whsec_...)
 * 
 * Setup Instructions:
 * 1. Set Firebase functions config:
 *    firebase functions:config:set stripe.secret_key="sk_test_..." stripe.webhook_secret="whsec_..."
 * 2. Access in code via process.env (functions config is automatically exposed as env vars)
 * 3. Deploy: firebase deploy --only functions
 */

const app = express();

// Initialize Stripe with secret key from environment
// TODO: Ensure STRIPE_SECRET_KEY is set in Firebase functions config
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY || '');

// IMPORTANT: Use raw body parser for Stripe webhook signature verification
// Stripe requires the raw request body to verify webhook signatures
app.use(bodyParser.raw({ type: 'application/json' }));

/**
 * Stripe Webhook Endpoint
 * 
 * Receives and processes Stripe webhook events.
 * Verifies webhook signature for security.
 */
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    // TODO: Verify webhook signature
    // This is CRITICAL for security - do not skip this step in production
    if (!webhookSecret) {
      console.error('STRIPE_WEBHOOK_SECRET not set');
      return res.status(500).send('Webhook secret not configured');
    }

    // Construct the event from the raw body and signature
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Parse the event
  console.log(`Received webhook event: ${event.type}`);

  // Route events to appropriate handlers
  try {
    switch (event.type) {
      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(event.data.object);
        break;

      case 'invoice.payment_failed':
        await handleInvoicePaymentFailed(event.data.object);
        break;

      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object);
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    console.error(`Error handling event ${event.type}:`, error);
    res.status(500).send('Internal server error');
  }
});

/**
 * Handler: Invoice Payment Succeeded
 * 
 * TODO: Update Firestore when payment succeeds
 * 1. Get firebaseUid from customer metadata: invoice.customer -> customer.metadata.firebaseUid
 * 2. Update /users/{uid}/subscriptions/{subscriptionId} with payment status
 * 3. Update /entitlements/{uid} with new tier based on subscription
 */
async function handleInvoicePaymentSucceeded(invoice) {
  console.log('TODO: Handle invoice.payment_succeeded', invoice.id);
  
  // TODO Implementation:
  // const customer = await stripe.customers.retrieve(invoice.customer);
  // const firebaseUid = customer.metadata.firebaseUid;
  // 
  // if (!firebaseUid) {
  //   console.error('No firebaseUid in customer metadata');
  //   return;
  // }
  // 
  // const admin = require('firebase-admin');
  // const db = admin.firestore();
  // 
  // await db.collection('users').doc(firebaseUid)
  //   .collection('subscriptions').doc(invoice.subscription)
  //   .set({
  //     status: 'active',
  //     currentPeriodEnd: new Date(invoice.period_end * 1000),
  //     lastPaymentStatus: 'succeeded',
  //     updatedAt: admin.firestore.FieldValue.serverTimestamp()
  //   }, { merge: true });
}

/**
 * Handler: Invoice Payment Failed
 * 
 * TODO: Update Firestore when payment fails
 * Mark subscription as past_due and notify user
 */
async function handleInvoicePaymentFailed(invoice) {
  console.log('TODO: Handle invoice.payment_failed', invoice.id);
  
  // TODO Implementation:
  // Similar to handleInvoicePaymentSucceeded, but mark as failed
  // Consider sending notification to user via Cloud Messaging
}

/**
 * Handler: Subscription Created
 * 
 * TODO: Create subscription record in Firestore
 * Map Stripe customer to Firebase user via metadata.firebaseUid
 */
async function handleSubscriptionCreated(subscription) {
  console.log('TODO: Handle customer.subscription.created', subscription.id);
  
  // TODO Implementation:
  // const customer = await stripe.customers.retrieve(subscription.customer);
  // const firebaseUid = customer.metadata.firebaseUid;
  // 
  // await db.collection('users').doc(firebaseUid)
  //   .collection('subscriptions').doc(subscription.id)
  //   .set({
  //     subscriptionId: subscription.id,
  //     status: subscription.status,
  //     priceId: subscription.items.data[0].price.id,
  //     currentPeriodStart: new Date(subscription.current_period_start * 1000),
  //     currentPeriodEnd: new Date(subscription.current_period_end * 1000),
  //     createdAt: admin.firestore.FieldValue.serverTimestamp()
  //   });
  // 
  // // Update entitlements based on price ID
  // const tier = determineTierFromPriceId(subscription.items.data[0].price.id);
  // await db.collection('entitlements').doc(firebaseUid).set({ tier });
}

/**
 * Handler: Subscription Updated
 * 
 * TODO: Update subscription record in Firestore
 * Handle tier changes, cancellations, renewals
 */
async function handleSubscriptionUpdated(subscription) {
  console.log('TODO: Handle customer.subscription.updated', subscription.id);
  
  // TODO Implementation:
  // Update subscription status and entitlements
}

/**
 * Handler: Subscription Deleted
 * 
 * TODO: Remove or downgrade entitlements in Firestore
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('TODO: Handle customer.subscription.deleted', subscription.id);
  
  // TODO Implementation:
  // Remove gold tier, revert to free tier
  // await db.collection('entitlements').doc(firebaseUid).set({ tier: 'free' });
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'stripe-webhooks' });
});

module.exports = app;
