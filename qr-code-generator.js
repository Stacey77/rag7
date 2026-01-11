// Simple QR Code Generator
// Using qrcode library from CDN or implementing a basic version

// Load QR Code library from CDN
(function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js';
    script.async = true;
    script.onerror = function() {
        console.warn('QR Code library failed to load from CDN');
        // Fallback to basic placeholder
        createFallbackQR();
    };
    document.head.appendChild(script);
})();

function createFallbackQR() {
    // Simple fallback if external library fails to load
    const canvas = document.getElementById('qrCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 200, 200);
    
    // Draw a simple grid pattern as placeholder
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    
    const gridSize = 10;
    for (let i = 0; i <= 200; i += gridSize) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, 200);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(200, i);
        ctx.stroke();
    }
    
    // Add text
    ctx.fillStyle = '#1a1a1a';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Contact vCard', 100, 100);
    ctx.font = '10px Arial';
    ctx.fillText('QR Code Preview', 100, 115);
}
