import React from 'react';

/**
 * Mock hook for user entitlements
 * 
 * TODO: Replace this mock with actual Firestore-backed entitlement checks
 * In production, this should:
 * 1. Read from Firestore /entitlements/{uid} collection
 * 2. Use Firebase Auth to get current user's uid
 * 3. Return the user's actual subscription tier from Firestore
 * 4. Handle loading states and errors appropriately
 * 
 * Example Firestore query:
 * const entitlementRef = doc(db, 'entitlements', auth.currentUser.uid);
 * const entitlementSnap = await getDoc(entitlementRef);
 * return entitlementSnap.data();
 */
function useUserEntitlements() {
  // Mock implementation - returns a sample entitlement
  return {
    tier: 'silver', // User has silver tier access
    userId: 'mock-user-123',
    validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // Valid for 30 days
  };
}

/**
 * ChannelLock component
 * 
 * Demonstrates client-side gating for premium content.
 * If a channel requires gold tier and the user doesn't have it,
 * displays a lock overlay with an upgrade CTA.
 * 
 * Props:
 * @param {Object} channel - Channel object with id, name, tier properties
 * @param {React.ReactNode} children - Content to render when unlocked
 * 
 * TODO: Connect to actual payment flow
 * - Link "Upgrade to Gold" button to Stripe Checkout
 * - Create checkout session via Firebase Function
 * - Redirect user to Stripe-hosted checkout page
 */
export default function ChannelLock({ channel, children }) {
  const userEntitlement = useUserEntitlements();
  
  // Check if channel requires gold tier
  const requiresGold = channel.tier === 'gold';
  const hasGoldAccess = userEntitlement.tier === 'gold';
  
  // If channel requires gold and user doesn't have it, show lock overlay
  if (requiresGold && !hasGoldAccess) {
    return (
      <div style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: '200px'
      }}>
        {/* Blurred content underneath */}
        <div style={{
          filter: 'blur(10px)',
          pointerEvents: 'none',
          opacity: 0.5
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
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '20px',
          textAlign: 'center'
        }}>
          {/* Lock Icon */}
          <div style={{
            fontSize: '48px',
            marginBottom: '20px'
          }}>
            🔒
          </div>
          
          {/* Message */}
          <h2 style={{ margin: '0 0 10px 0' }}>
            Premium Content
          </h2>
          <p style={{ margin: '0 0 20px 0', maxWidth: '400px' }}>
            {channel.name} is a gold-tier channel. Upgrade to access premium content.
          </p>
          
          {/* CTA Button */}
          <button
            onClick={() => {
              // TODO: Implement actual checkout flow
              // 1. Call Firebase Function to create Stripe Checkout Session
              // 2. Redirect to Stripe Checkout
              // Example:
              // const response = await fetch('/api/create-checkout-session', {
              //   method: 'POST',
              //   body: JSON.stringify({ priceId: 'price_gold_tier' })
              // });
              // const { url } = await response.json();
              // window.location.href = url;
              
              alert('Upgrade flow not yet implemented. Connect to Stripe Checkout here.');
            }}
            style={{
              backgroundColor: '#FFD700',
              color: '#000',
              border: 'none',
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: 'bold',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'opacity 0.2s'
            }}
            onMouseOver={(e) => e.target.style.opacity = '0.8'}
            onMouseOut={(e) => e.target.style.opacity = '1'}
          >
            Upgrade to Gold
          </button>
          
          {/* Additional info */}
          <p style={{
            marginTop: '20px',
            fontSize: '12px',
            color: '#aaa'
          }}>
            Current tier: {userEntitlement.tier}
          </p>
        </div>
      </div>
    );
  }
  
  // User has access, render children normally
  return <>{children}</>;
}
