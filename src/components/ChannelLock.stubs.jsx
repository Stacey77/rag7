/**
 * ChannelLock - Client-side gating stub component
 * 
 * Demonstrates how to check user entitlements and render a lock overlay
 * with an "Upgrade to Gold" CTA for premium channels.
 * 
 * TODO: Replace the mock useUserEntitlements() hook with real Firestore-backed
 * entitlement checks that query the user's subscription status from your
 * Firestore database.
 * 
 * Example Firestore query:
 * - Collection: users/{uid}/entitlements
 * - Check for active subscription with tier: "gold"
 * - Verify subscription_end_date > current date
 */

import React, { useState, useEffect } from 'react';

/**
 * Mock hook for user entitlements
 * 
 * TODO: Replace this with a real implementation that:
 * 1. Gets the current Firebase Auth user
 * 2. Queries Firestore: db.collection('users').doc(uid).collection('entitlements')
 * 3. Checks for active gold tier subscription
 * 4. Returns { tier: 'gold' | 'free', loading, error }
 * 
 * Example real implementation:
 * 
 * import { useAuth } from '../hooks/useAuth';
 * import { db } from '../firebase';
 * 
 * function useUserEntitlements() {
 *   const { user } = useAuth();
 *   const [entitlements, setEntitlements] = useState({ tier: 'free', loading: true });
 *   
 *   useEffect(() => {
 *     if (!user) {
 *       setEntitlements({ tier: 'free', loading: false });
 *       return;
 *     }
 *     
 *     const unsubscribe = db
 *       .collection('users')
 *       .doc(user.uid)
 *       .collection('entitlements')
 *       .where('status', '==', 'active')
 *       .onSnapshot(snapshot => {
 *         const hasGold = snapshot.docs.some(doc => {
 *           const data = doc.data();
 *           return data.tier === 'gold' && 
 *                  data.subscription_end_date?.toDate() > new Date();
 *         });
 *         setEntitlements({ 
 *           tier: hasGold ? 'gold' : 'free', 
 *           loading: false 
 *         });
 *       });
 *     
 *     return () => unsubscribe();
 *   }, [user]);
 *   
 *   return entitlements;
 * }
 */
function useUserEntitlements() {
  const [entitlements, setEntitlements] = useState({ tier: 'free', loading: true });

  useEffect(() => {
    // Mock: Simulate API call delay
    const timer = setTimeout(() => {
      // Mock: Return free tier for demo purposes
      // In production, this would query Firestore for the user's actual entitlements
      setEntitlements({ tier: 'free', loading: false });
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return entitlements;
}

/**
 * ChannelLock component
 * 
 * Wraps channel content and displays a lock overlay for premium channels
 * when the user doesn't have the required tier.
 * 
 * @param {Object} props
 * @param {Object} props.channel - Channel object with { id, name, tier, ... }
 * @param {React.ReactNode} props.children - Content to display when unlocked
 */
export function ChannelLock({ channel, children }) {
  const { tier: userTier, loading } = useUserEntitlements();

  // Show loading state
  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}>Loading...</div>
      </div>
    );
  }

  // Check if channel requires gold tier
  const requiresGold = channel.tier === 'gold';
  const hasAccess = !requiresGold || userTier === 'gold';

  // If user has access, render content normally
  if (hasAccess) {
    return <>{children}</>;
  }

  // Otherwise, show lock overlay
  return (
    <div style={styles.lockedContainer}>
      {/* Blurred background content */}
      <div style={styles.blurredContent}>
        {children}
      </div>
      
      {/* Lock overlay */}
      <div style={styles.overlay}>
        <div style={styles.lockCard}>
          <div style={styles.lockIcon}>🔒</div>
          <h2 style={styles.lockTitle}>Premium Channel</h2>
          <p style={styles.lockMessage}>
            {channel.name} requires a Gold subscription to access.
          </p>
          <button 
            style={styles.upgradeButton}
            onClick={() => handleUpgradeClick(channel)}
          >
            Upgrade to Gold
          </button>
          <p style={styles.benefitsText}>
            ✨ Unlock all premium channels<br />
            🎬 Ad-free streaming<br />
            📺 4K quality available
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Handle upgrade button click
 * 
 * TODO: Replace this with real Stripe Checkout flow:
 * 1. Call your Firebase Function to create a Stripe Checkout Session
 * 2. Redirect user to Stripe Checkout
 * 3. Handle success/cancel redirects
 * 
 * Example implementation:
 * 
 * import { getFunctions, httpsCallable } from 'firebase/functions';
 * 
 * async function handleUpgradeClick(channel) {
 *   try {
 *     const functions = getFunctions();
 *     const createCheckoutSession = httpsCallable(functions, 'createCheckoutSession');
 *     
 *     const { data } = await createCheckoutSession({
 *       priceId: 'price_xxxxx', // Your Stripe Price ID for gold tier
 *       successUrl: window.location.origin + '/success',
 *       cancelUrl: window.location.origin + '/channels/' + channel.id,
 *     });
 *     
 *     window.location.href = data.url; // Redirect to Stripe Checkout
 *   } catch (error) {
 *     console.error('Error creating checkout session:', error);
 *     alert('Unable to start checkout. Please try again.');
 *   }
 * }
 */
function handleUpgradeClick(channel) {
  // Mock implementation - just log for now
  console.log('Upgrade clicked for channel:', channel.id);
  alert('Upgrade flow not yet implemented. See TODO comments in ChannelLock.stubs.jsx');
  
  // TODO: Implement real Stripe Checkout flow (see comment above)
}

// Inline styles for demo purposes
// TODO: Move to CSS modules or styled-components in production
const styles = {
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '200px',
  },
  spinner: {
    fontSize: '18px',
    color: '#666',
  },
  lockedContainer: {
    position: 'relative',
    minHeight: '400px',
  },
  blurredContent: {
    filter: 'blur(8px)',
    pointerEvents: 'none',
    userSelect: 'none',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
  },
  lockCard: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '400px',
    textAlign: 'center',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
  },
  lockIcon: {
    fontSize: '48px',
    marginBottom: '16px',
  },
  lockTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '12px',
    color: '#333',
  },
  lockMessage: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '24px',
  },
  upgradeButton: {
    backgroundColor: '#FFD700',
    color: '#000',
    border: 'none',
    borderRadius: '8px',
    padding: '14px 32px',
    fontSize: '18px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginBottom: '20px',
    transition: 'transform 0.2s',
  },
  benefitsText: {
    fontSize: '14px',
    color: '#666',
    lineHeight: '1.6',
  },
};

export default ChannelLock;
