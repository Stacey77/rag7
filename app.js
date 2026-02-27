/**
 * Main Application Logic
 * Handles business card interactions and PWA functionality
 */

class BusinessCardApp {
    constructor() {
        this.deferredPrompt = null;
        this.theme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    /**
     * Initialize application
     */
    init() {
        // Apply saved theme
        this.applyTheme();

        // Bind event listeners
        this.bindEvents();

        // Setup PWA install prompt
        this.setupPWA();

        // Initialize copy functionality
        this.initCopyButtons();

        // Initialize animations
        this.initAnimations();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Download vCard
        const downloadBtn = document.getElementById('download-vcard');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadVCard());
        }

        // Share card
        const shareBtn = document.getElementById('share-card');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareCard());
        }

        // Theme toggle
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Install PWA
        const installBtn = document.getElementById('install-pwa');
        if (installBtn) {
            installBtn.addEventListener('click', () => this.installPWA());
        }
    }

    /**
     * Initialize copy buttons
     */
    initCopyButtons() {
        const copyButtons = document.querySelectorAll('.copy-btn');
        
        copyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const textToCopy = btn.dataset.copy;
                this.copyToClipboard(textToCopy);
            });
        });
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!');
        } catch (error) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                document.execCommand('copy');
                this.showToast('Copied to clipboard!');
            } catch (err) {
                this.showToast('Failed to copy', 'error');
            }
            
            document.body.removeChild(textarea);
        }
    }

    /**
     * Download vCard
     */
    downloadVCard() {
        const vcard = this.generateVCard();
        const blob = new Blob([vcard], { type: 'text/vcard' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Stacey-Williams-Contact.vcf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        this.showToast('Contact saved!');
    }

    /**
     * Generate vCard content
     */
    generateVCard() {
        return `BEGIN:VCARD
VERSION:3.0
FN:Stacey Williams
N:Williams;Stacey;;;
TITLE:Certified Service Technician
ORG:Mercedes Benz Of Collierville
TEL;TYPE=WORK,VOICE:(901) 555-5555
EMAIL;TYPE=WORK:stacey.williams@mbofcollierville.com
URL:https://www.mbofcollierville.com
ADR;TYPE=WORK:;;850 W Poplar Ave;Collierville;TN;38017;USA
NOTE:Certified Mercedes-Benz Service Technician specializing in all Mercedes-Benz models
END:VCARD`;
    }

    /**
     * Share card using Web Share API
     */
    async shareCard() {
        const shareData = {
            title: 'Stacey Williams - Digital Business Card',
            text: 'Certified Service Technician at Mercedes Benz Of Collierville',
            url: window.location.href
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
                this.showToast('Card shared!');
            } else {
                // Fallback: copy link to clipboard
                await this.copyToClipboard(window.location.href);
                this.showToast('Link copied to clipboard!');
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error sharing:', error);
                this.showToast('Failed to share', 'error');
            }
        }
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
        this.showToast(`${this.theme === 'dark' ? 'Dark' : 'Light'} theme activated`);
    }

    /**
     * Apply theme
     */
    applyTheme() {
        const root = document.documentElement;
        
        if (this.theme === 'light') {
            root.style.setProperty('--bg-primary', '#ffffff');
            root.style.setProperty('--bg-secondary', '#f5f5f5');
            root.style.setProperty('--text-primary', '#1a1a1a');
            root.style.setProperty('--text-secondary', '#666666');
            root.style.setProperty('--card-bg', 'linear-gradient(145deg, #ffffff, #f5f5f5)');
            document.body.style.background = 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)';
        } else {
            root.style.setProperty('--bg-primary', '#1a1a1a');
            root.style.setProperty('--bg-secondary', '#2d2d2d');
            root.style.setProperty('--text-primary', '#ffffff');
            root.style.setProperty('--text-secondary', '#999999');
            root.style.setProperty('--card-bg', 'linear-gradient(145deg, #2a2a2a, #1f1f1f)');
            document.body.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)';
        }
    }

    /**
     * Setup PWA installation
     */
    setupPWA() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            
            // Show install button
            const installBtn = document.getElementById('install-pwa');
            if (installBtn) {
                installBtn.style.display = 'block';
            }
        });

        // Listen for app installed event
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed');
            this.deferredPrompt = null;
            
            const installBtn = document.getElementById('install-pwa');
            if (installBtn) {
                installBtn.style.display = 'none';
            }
            
            this.showToast('App installed successfully!');
        });

        // Check if already running as PWA
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('Running as PWA');
        }
    }

    /**
     * Install PWA
     */
    async installPWA() {
        if (!this.deferredPrompt) {
            this.showToast('App already installed or not available', 'info');
            return;
        }

        // Show install prompt
        this.deferredPrompt.prompt();

        // Wait for user response
        const { outcome } = await this.deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('User accepted installation');
        } else {
            console.log('User dismissed installation');
        }

        this.deferredPrompt = null;
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.className = `toast toast-${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    /**
     * Initialize animations
     */
    initAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observe contact items
        const contactItems = document.querySelectorAll('.contact-item');
        contactItems.forEach(item => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(item);
        });

        // Add visible class after a delay to trigger animations
        setTimeout(() => {
            contactItems.forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('visible');
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }, 300);
    }

    /**
     * Track analytics event (placeholder)
     */
    trackEvent(category, action, label) {
        // Integrate with analytics service if needed
        console.log('Event:', category, action, label);
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new BusinessCardApp();
    });
} else {
    new BusinessCardApp();
}

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('App is online');
});

window.addEventListener('offline', () => {
    console.log('App is offline - using cached content');
});
