/**
 * Stripe Webhooks Handler for Firebase Cloud Functions
 * 
 * This Express app receives and processes Stripe webhook events.
 * It updates Firestore with subscription and payment information.
 * 
 * SECURITY NOTES:
 * - ALWAYS verify webhook signatures using stripe.webhooks.constructEvent
 * - NEVER trust webhook data without signature verification
 * - Use environment variables for secrets (NEVER commit real secrets)
 * 
 * Environment Variables Required:
 * - STRIPE_SECRET_KEY: Your Stripe secret key (sk_test_... or sk_live_...)
 * - STRIPE_WEBHOOK_SECRET: Webhook signing secret from Stripe Dashboard (whsec_...)
 */

const express = require('express');
const bodyParser = require('body-parser');

// Initialize Stripe with secret key from environment
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();

// IMPORTANT: Use raw body parser for Stripe webhook signature verification
// Stripe requires the raw request body to verify signatures
app.use(bodyParser.raw({ type: 'application/json' }));

/**
 * Stripe Webhook Endpoint
 * 
 * Receives events from Stripe and updates Firestore accordingly
 */
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    // TODO: Uncomment and implement signature verification
    // This is CRITICAL for security - do not skip in production!
    /*
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      webhookSecret
    );
    */
    
    // TEMPORARY: Parse body directly (ONLY for development/testing)
    // Remove this in production and use constructEvent above
    event = JSON.parse(req.body.toString());
    
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  console.log('Received webhook event:', event.type);

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

    // Return 200 to acknowledge receipt
    res.json({ received: true });

  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

/**
 * Handle successful invoice payment
 * 
 * TODO: Implement Firestore update logic
 * - Get firebaseUid from customer.metadata
 * - Update /users/{uid}/subscriptions/{subId} with payment info
 * - Update /entitlements/{uid} with tier and validUntil
 */
async function handleInvoicePaymentSucceeded(invoice) {
  console.log('Invoice payment succeeded:', invoice.id);
  
  // TODO: Extract Firebase UID from customer metadata
  // const customer = await stripe.customers.retrieve(invoice.customer);
  // const firebaseUid = customer.metadata.firebaseUid;
  
  // TODO: Update Firestore
  // const admin = require('firebase-admin');
  // const db = admin.firestore();
  // 
  // await db.collection('users').doc(firebaseUid)
  //   .collection('subscriptions').doc(invoice.subscription)
  //   .set({
  //     status: 'active',
  //     lastPayment: new Date(invoice.created * 1000),
  //     amount: invoice.amount_paid,
  //     currency: invoice.currency,
  //   }, { merge: true });
  //
  // // Update entitlements based on subscription tier
  // await db.collection('entitlements').doc(firebaseUid).set({
  //   tier: 'gold', // Determine from subscription product/price
  //   validUntil: new Date(invoice.period_end * 1000),
  //   updatedAt: new Date(),
  // });
}

/**
 * Handle failed invoice payment
 * 
 * TODO: Implement Firestore update and user notification
 */
async function handleInvoicePaymentFailed(invoice) {
  console.log('Invoice payment failed:', invoice.id);
  
  // TODO: Update subscription status to 'payment_failed'
  // TODO: Optionally downgrade entitlements or show grace period
  // TODO: Send notification to user about failed payment
}

/**
 * Handle subscription created
 * 
 * TODO: Create subscription record in Firestore
 */
async function handleSubscriptionCreated(subscription) {
  console.log('Subscription created:', subscription.id);
  
  // TODO: Extract Firebase UID from customer.metadata
  // TODO: Create /users/{uid}/subscriptions/{subId} document
  // TODO: Set initial entitlements based on subscription tier
}

/**
 * Handle subscription updated
 * 
 * TODO: Update subscription record and entitlements
 */
async function handleSubscriptionUpdated(subscription) {
  console.log('Subscription updated:', subscription.id);
  
  // TODO: Update subscription status, tier changes, etc.
  // TODO: Handle tier upgrades/downgrades
}

/**
 * Handle subscription deleted/cancelled
 * 
 * TODO: Update subscription record and revoke entitlements
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('Subscription deleted:', subscription.id);
  
  // TODO: Mark subscription as cancelled
  // TODO: Update entitlements (either immediate or at period_end)
  // TODO: Consider grace period handling
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'stripe-webhooks' });
});

// Export the Express app for Firebase Cloud Functions
// Usage in Firebase: exports.stripeWebhook = functions.https.onRequest(app);
module.exports = app;
