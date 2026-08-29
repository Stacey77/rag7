/**
 * ChannelLock.stubs.jsx
 * 
 * React component demonstrating client-side gating for premium channels.
 * This is a STUB implementation using mock data for demonstration purposes.
 * 
 * TODO: Replace mock useUserEntitlements with real Firestore-backed entitlement checks
 * TODO: Connect "Upgrade to Gold" CTA to actual Stripe Checkout flow
 */

import React from 'react';

/**
 * Mock hook for user entitlements
 * 
 * TODO: Replace this with a real hook that:
 * 1. Reads from Firestore /entitlements/{uid} collection
 * 2. Subscribes to real-time updates when subscription changes
 * 3. Handles authentication state (returns null tier when not logged in)
 * 
 * Example real implementation:
 * const useUserEntitlements = () => {
 *   const [entitlement, setEntitlement] = useState(null);
 *   const { user } = useAuth();
 *   
 *   useEffect(() => {
 *     if (!user) return;
 *     const unsubscribe = firestore
 *       .collection('entitlements')
 *       .doc(user.uid)
 *       .onSnapshot(doc => setEntitlement(doc.data()));
 *     return unsubscribe;
 *   }, [user]);
 *   
 *   return entitlement;
 * };
 */
const useUserEntitlements = () => {
  // Mock entitlement - replace with real Firestore query
  return {
    tier: 'silver',  // Mock: user has silver tier
    validUntil: new Date('2025-12-31'),
  };
};

/**
 * ChannelLock component
 * 
 * Renders a lock overlay for channels that require a higher tier subscription
 * 
 * @param {Object} props
 * @param {Object} props.channel - Channel object with tier property
 * @param {React.ReactNode} props.children - Channel content to potentially lock
 */
const ChannelLock = ({ channel, children }) => {
  const userEntitlement = useUserEntitlements();
  
  // Determine if user has access to this channel
  const isLocked = channel.tier === 'gold' && userEntitlement?.tier !== 'gold';
  
  if (!isLocked) {
    // User has access, render channel content normally
    return <>{children}</>;
  }
  
  // User doesn't have access, show lock overlay
  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100%',
    }}>
      {/* Blurred/dimmed background content */}
      <div style={{
        filter: 'blur(8px)',
        opacity: 0.3,
        pointerEvents: 'none',
      }}>
        {children}
      </div>
      
      {/* Lock overlay */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '2rem',
        textAlign: 'center',
      }}>
        {/* Lock icon */}
        <div style={{
          fontSize: '3rem',
          marginBottom: '1rem',
        }}>
          🔒
        </div>
        
        {/* Message */}
        <h2 style={{ marginBottom: '1rem' }}>
          Premium Channel
        </h2>
        <p style={{ marginBottom: '1.5rem', maxWidth: '400px' }}>
          This channel requires a Gold tier subscription.
          Upgrade now to unlock this and other premium channels.
        </p>
        
        {/* Upgrade CTA */}
        <button
          onClick={() => {
            // TODO: Replace with actual Stripe Checkout flow
            // Example:
            // const response = await fetch('/api/create-checkout-session', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify({ priceId: 'price_gold_monthly' })
            // });
            // const { sessionId } = await response.json();
            // const stripe = await stripePromise;
            // await stripe.redirectToCheckout({ sessionId });
            
            alert('TODO: Implement Stripe Checkout flow for Gold tier upgrade');
          }}
          style={{
            backgroundColor: '#FFD700',
            color: '#000',
            border: 'none',
            padding: '0.75rem 2rem',
            fontSize: '1rem',
            fontWeight: 'bold',
            borderRadius: '4px',
            cursor: 'pointer',
            transition: 'transform 0.2s',
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          Upgrade to Gold
        </button>
      </div>
    </div>
  );
};

export default ChannelLock;
