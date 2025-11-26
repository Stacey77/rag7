/**
 * Stripe Webhooks Handler for Firebase Cloud Functions
 * 
 * This Express app receives and processes Stripe webhook events to update
 * user entitlements in Firestore based on subscription changes.
 * 
 * SECURITY CRITICAL:
 * - ALWAYS verify webhook signatures in production
 * - NEVER skip signature verification
 * - Use environment variables for secrets (never hardcode)
 * 
 * Environment Variables Required:
 * - STRIPE_SECRET_KEY: Your Stripe secret key (sk_test_... or sk_live_...)
 * - STRIPE_WEBHOOK_SECRET: Webhook signing secret from Stripe Dashboard (whsec_...)
 * 
 * Deploy with:
 *   firebase functions:config:set stripe.secret_key="sk_test_..." stripe.webhook_secret="whsec_..."
 *   firebase deploy --only functions:stripeWebhooks
 */

const express = require('express');
const bodyParser = require('body-parser');

// Initialize Stripe with secret key from environment
// TODO: Ensure STRIPE_SECRET_KEY is set in Firebase Functions config
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY || '');

// Initialize Firebase Admin SDK (for Firestore writes)
// TODO: Initialize Firebase Admin SDK here
// const admin = require('firebase-admin');
// admin.initializeApp();
// const db = admin.firestore();

const app = express();

/**
 * Webhook endpoint - MUST use raw body for signature verification
 * 
 * CRITICAL: We need the raw body buffer to verify Stripe signatures.
 * Express body parsers consume the stream, so we use verify callback
 * to save the raw body for signature verification.
 */
app.post('/webhook', 
  bodyParser.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

    let event;

    try {
      // TODO: UNCOMMENT THIS IN PRODUCTION - Verify webhook signature
      // This is CRITICAL for security - prevents attackers from spoofing webhooks
      /*
      if (!webhookSecret) {
        console.error('STRIPE_WEBHOOK_SECRET not configured!');
        return res.status(500).send('Webhook secret not configured');
      }

      event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        webhookSecret
      );
      */

      // TEMPORARY: Parse body directly (UNSAFE - remove in production!)
      // This is only for initial testing without signature verification
      event = JSON.parse(req.body.toString());
      console.warn('WARNING: Webhook signature verification is disabled! Enable before production.');

    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Log the event type for debugging
    console.log('Received Stripe webhook event:', event.type, 'ID:', event.id);

    // Handle different event types
    try {
      switch (event.type) {
        case 'checkout.session.completed':
          await handleCheckoutSessionCompleted(event.data.object);
          break;

        case 'customer.subscription.created':
        case 'customer.subscription.updated':
          await handleSubscriptionChange(event.data.object);
          break;

        case 'customer.subscription.deleted':
          await handleSubscriptionDeleted(event.data.object);
          break;

        case 'invoice.payment_succeeded':
          await handleInvoicePaymentSucceeded(event.data.object);
          break;

        case 'invoice.payment_failed':
          await handleInvoicePaymentFailed(event.data.object);
          break;

        default:
          console.log(`Unhandled event type: ${event.type}`);
      }

      // Return a 200 response to acknowledge receipt of the event
      res.json({ received: true });

    } catch (error) {
      console.error('Error processing webhook:', error);
      res.status(500).send('Webhook processing error');
    }
  }
);

/**
 * Handle successful checkout session completion
 * 
 * TODO: Implement this function to:
 * 1. Extract customer ID and subscription ID from session
 * 2. Get Firebase UID from customer metadata (customer.metadata.firebase_uid)
 * 3. Create entitlement record in Firestore
 * 
 * Firestore structure:
 *   users/{firebase_uid}/entitlements/{subscription_id}
 *     - tier: "gold"
 *     - status: "active"
 *     - stripe_customer_id: "cus_..."
 *     - stripe_subscription_id: "sub_..."
 *     - subscription_start_date: Timestamp
 *     - subscription_end_date: Timestamp
 *     - created_at: Timestamp
 */
async function handleCheckoutSessionCompleted(session) {
  console.log('Checkout session completed:', session.id);
  
  // TODO: Implement Firestore write
  /*
  const customerId = session.customer;
  const subscriptionId = session.subscription;
  
  // Get customer to extract Firebase UID from metadata
  const customer = await stripe.customers.retrieve(customerId);
  const firebaseUid = customer.metadata.firebase_uid;
  
  if (!firebaseUid) {
    console.error('No firebase_uid in customer metadata:', customerId);
    return;
  }

  // Get subscription details
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  
  // Write entitlement to Firestore
  await db.collection('users').doc(firebaseUid)
    .collection('entitlements').doc(subscriptionId)
    .set({
      tier: 'gold', // TODO: Map from subscription.items.data[0].price.product
      status: subscription.status,
      stripe_customer_id: customerId,
      stripe_subscription_id: subscriptionId,
      subscription_start_date: admin.firestore.Timestamp.fromDate(
        new Date(subscription.current_period_start * 1000)
      ),
      subscription_end_date: admin.firestore.Timestamp.fromDate(
        new Date(subscription.current_period_end * 1000)
      ),
      created_at: admin.firestore.FieldValue.serverTimestamp(),
    });
  
  console.log('Entitlement created for user:', firebaseUid);
  */
}

/**
 * Handle subscription creation or update
 * 
 * TODO: Update entitlement status in Firestore based on subscription changes
 */
async function handleSubscriptionChange(subscription) {
  console.log('Subscription changed:', subscription.id, 'Status:', subscription.status);
  
  // TODO: Update Firestore entitlement record
  /*
  const customer = await stripe.customers.retrieve(subscription.customer);
  const firebaseUid = customer.metadata.firebase_uid;
  
  if (!firebaseUid) {
    console.error('No firebase_uid in customer metadata');
    return;
  }

  await db.collection('users').doc(firebaseUid)
    .collection('entitlements').doc(subscription.id)
    .set({
      status: subscription.status,
      subscription_end_date: admin.firestore.Timestamp.fromDate(
        new Date(subscription.current_period_end * 1000)
      ),
      updated_at: admin.firestore.FieldValue.serverTimestamp(),
    }, { merge: true });
  */
}

/**
 * Handle subscription deletion (cancellation)
 * 
 * TODO: Mark entitlement as inactive in Firestore
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('Subscription deleted:', subscription.id);
  
  // TODO: Update Firestore to mark entitlement as inactive
  /*
  const customer = await stripe.customers.retrieve(subscription.customer);
  const firebaseUid = customer.metadata.firebase_uid;
  
  if (!firebaseUid) return;

  await db.collection('users').doc(firebaseUid)
    .collection('entitlements').doc(subscription.id)
    .update({
      status: 'canceled',
      updated_at: admin.firestore.FieldValue.serverTimestamp(),
    });
  */
}

/**
 * Handle successful invoice payment
 * 
 * TODO: Update subscription end date on successful renewal
 */
async function handleInvoicePaymentSucceeded(invoice) {
  console.log('Invoice payment succeeded:', invoice.id);
  
  // TODO: Update Firestore with new billing period
  /*
  const subscriptionId = invoice.subscription;
  if (!subscriptionId) return;
  
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const customer = await stripe.customers.retrieve(subscription.customer);
  const firebaseUid = customer.metadata.firebase_uid;
  
  if (!firebaseUid) return;

  await db.collection('users').doc(firebaseUid)
    .collection('entitlements').doc(subscriptionId)
    .update({
      subscription_end_date: admin.firestore.Timestamp.fromDate(
        new Date(subscription.current_period_end * 1000)
      ),
      last_payment_date: admin.firestore.FieldValue.serverTimestamp(),
    });
  */
}

/**
 * Handle failed invoice payment
 * 
 * TODO: Optionally notify user or mark subscription as past_due
 */
async function handleInvoicePaymentFailed(invoice) {
  console.log('Invoice payment failed:', invoice.id);
  
  // TODO: Handle payment failure (e.g., send notification, update status)
}

// Health check endpoint
app.get('/', (req, res) => {
  res.send('Stripe Webhooks Handler - OK');
});

// Export the Express app as a Firebase Cloud Function
// Firebase will automatically handle the server setup
module.exports = app;

/**
 * DEPLOYMENT NOTES:
 * 
 * 1. Set environment variables:
 *    firebase functions:config:set \
 *      stripe.secret_key="sk_test_..." \
 *      stripe.webhook_secret="whsec_..."
 * 
 * 2. Update functions/index.js to import and export this function:
 *    const stripeWebhooks = require('./stripe-webhooks');
 *    exports.stripeWebhooks = functions.https.onRequest(stripeWebhooks);
 * 
 * 3. Deploy:
 *    firebase deploy --only functions:stripeWebhooks
 * 
 * 4. Configure Stripe webhook:
 *    - Go to Stripe Dashboard > Developers > Webhooks
 *    - Add endpoint: https://us-central1-YOUR_PROJECT.cloudfunctions.net/stripeWebhooks/webhook
 *    - Select events: checkout.session.completed, customer.subscription.*, invoice.payment_*
 *    - Copy webhook signing secret to functions config
 * 
 * 5. BEFORE PRODUCTION: Uncomment signature verification code (line 60-70)
 */
