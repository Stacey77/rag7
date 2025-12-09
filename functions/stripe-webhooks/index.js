/**
 * Stripe Webhook Handler for Firebase Cloud Functions
 * 
 * This Express app receives and processes Stripe webhook events.
 * It updates Firestore with subscription and payment status changes.
 * 
 * Environment Variables Required:
 * - STRIPE_SECRET_KEY: Stripe API secret key (from Firebase config)
 * - STRIPE_WEBHOOK_SECRET: Stripe webhook signing secret (from Firebase config)
 * 
 * Deploy Instructions:
 * 1. Set Firebase Functions config:
 *    firebase functions:config:set stripe.secret_key="sk_test_..." stripe.webhook_secret="whsec_..."
 * 2. Deploy: firebase deploy --only functions
 * 
 * Security Notes:
 * - ALWAYS verify webhook signatures using stripe.webhooks.constructEvent
 * - NEVER trust unverified webhook data
 * - Map Stripe customers to Firebase users via metadata.firebaseUid
 */

const express = require('express');
const bodyParser = require('body-parser');

// Initialize Stripe (requires STRIPE_SECRET_KEY from environment)
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();

// IMPORTANT: Use raw body parser for webhook signature verification
// Stripe requires the raw request body to verify signatures
app.use(bodyParser.raw({ type: 'application/json' }));

/**
 * Main webhook endpoint
 * POST /webhook
 */
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  
  let event;
  
  try {
    // TODO: Verify webhook signature
    // This is CRITICAL for security - prevents attackers from sending fake webhooks
    // Uncomment and test the following code:
    /*
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      webhookSecret
    );
    */
    
    // TEMPORARY: Parse body directly (REMOVE IN PRODUCTION)
    // Only for initial testing - MUST verify signatures in production
    const bodyString = req.body.toString('utf8');
    event = JSON.parse(bodyString);
    
    console.log('Received webhook event:', event.type);
    
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  // Route event to appropriate handler
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
    
  } catch (err) {
    console.error('Error processing webhook:', err);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

/**
 * TODO: Implement handler for invoice.payment_succeeded
 * 
 * Actions:
 * 1. Get firebaseUid from customer metadata: invoice.customer.metadata.firebaseUid
 * 2. Update Firestore /users/{uid}/subscriptions/{subId} with payment status
 * 3. Update /entitlements/{uid} with new tier based on subscription
 * 4. Set validUntil timestamp based on subscription period
 */
async function handleInvoicePaymentSucceeded(invoice) {
  console.log('TODO: Handle invoice.payment_succeeded', invoice.id);
  
  // Example Firestore update:
  /*
  const admin = require('firebase-admin');
  const db = admin.firestore();
  
  // Get Firebase UID from Stripe customer metadata
  const customer = await stripe.customers.retrieve(invoice.customer);
  const firebaseUid = customer.metadata.firebaseUid;
  
  if (!firebaseUid) {
    console.error('No firebaseUid in customer metadata');
    return;
  }
  
  // Update subscription status
  await db.collection('users').doc(firebaseUid)
    .collection('subscriptions').doc(invoice.subscription)
    .set({
      status: 'active',
      lastPayment: invoice.created,
      amountPaid: invoice.amount_paid,
      currency: invoice.currency,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
  
  // Update entitlements
  await db.collection('entitlements').doc(firebaseUid).set({
    tier: 'gold', // Or derive from subscription price
    validUntil: new Date(invoice.period_end * 1000),
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  }, { merge: true });
  */
}

/**
 * TODO: Implement handler for invoice.payment_failed
 * 
 * Actions:
 * 1. Update subscription status to 'past_due'
 * 2. Consider downgrading entitlements after grace period
 * 3. Send notification to user (optional)
 */
async function handleInvoicePaymentFailed(invoice) {
  console.log('TODO: Handle invoice.payment_failed', invoice.id);
  
  // Example implementation:
  /*
  const customer = await stripe.customers.retrieve(invoice.customer);
  const firebaseUid = customer.metadata.firebaseUid;
  
  await db.collection('users').doc(firebaseUid)
    .collection('subscriptions').doc(invoice.subscription)
    .set({
      status: 'past_due',
      lastPaymentAttempt: invoice.created,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
  */
}

/**
 * TODO: Implement handler for customer.subscription.created
 */
async function handleSubscriptionCreated(subscription) {
  console.log('TODO: Handle customer.subscription.created', subscription.id);
  
  // Create subscription record in Firestore
  // Map customer to Firebase user via metadata.firebaseUid
}

/**
 * TODO: Implement handler for customer.subscription.updated
 */
async function handleSubscriptionUpdated(subscription) {
  console.log('TODO: Handle customer.subscription.updated', subscription.id);
  
  // Update subscription record
  // Update entitlements if tier changed
}

/**
 * TODO: Implement handler for customer.subscription.deleted
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('TODO: Handle customer.subscription.deleted', subscription.id);
  
  // Mark subscription as cancelled
  // Downgrade entitlements
  // Set validUntil to end of billing period
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Export for Firebase Functions
module.exports = app;

// For local testing (optional)
if (require.main === module) {
  const port = process.env.PORT || 3000;
  app.listen(port, () => {
    console.log(`Webhook server listening on port ${port}`);
  });
}
