/**
 * Knowledge Base for AI Agent
 * Contains local knowledge for offline AI responses
 */

const KnowledgeBase = {
    // Business Information
    business: {
        name: "Mercedes Benz Of Collierville",
        technician: "Stacey Williams",
        title: "Certified Service Technician",
        phone: "(901) 555-5555",
        email: "stacey.williams@mbofcollierville.com",
        website: "https://www.mbofcollierville.com",
        address: "850 W Poplar Ave, Collierville, TN 38017",
        hours: {
            monday: "7:00 AM - 6:00 PM",
            tuesday: "7:00 AM - 6:00 PM",
            wednesday: "7:00 AM - 6:00 PM",
            thursday: "7:00 AM - 6:00 PM",
            friday: "7:00 AM - 6:00 PM",
            saturday: "8:00 AM - 4:00 PM",
            sunday: "Closed"
        }
    },

    // Services Offered
    services: [
        {
            name: "Oil Change Service",
            description: "Complete oil and filter change using Mercedes-Benz approved synthetic oil",
            duration: "30-45 minutes",
            category: "maintenance"
        },
        {
            name: "Brake Service",
            description: "Comprehensive brake inspection, pad replacement, and rotor resurfacing",
            duration: "1-2 hours",
            category: "safety"
        },
        {
            name: "Engine Diagnostics",
            description: "Advanced computer diagnostics using Mercedes-Benz Star Diagnostic System",
            duration: "1-2 hours",
            category: "diagnostics"
        },
        {
            name: "Tire Service",
            description: "Tire rotation, balancing, alignment, and replacement",
            duration: "1 hour",
            category: "maintenance"
        },
        {
            name: "Battery Service",
            description: "Battery testing, replacement, and electrical system diagnostics",
            duration: "30-60 minutes",
            category: "electrical"
        },
        {
            name: "Transmission Service",
            description: "Transmission fluid change and inspection",
            duration: "1-2 hours",
            category: "maintenance"
        },
        {
            name: "A/C Service",
            description: "Air conditioning system diagnostics and refrigerant recharge",
            duration: "1 hour",
            category: "comfort"
        },
        {
            name: "Pre-Purchase Inspection",
            description: "Comprehensive vehicle inspection before purchase",
            duration: "2-3 hours",
            category: "inspection"
        }
    ],

    // Frequently Asked Questions
    faqs: [
        {
            question: "What are your service hours?",
            answer: "We're open Monday-Friday 7:00 AM - 6:00 PM, Saturday 8:00 AM - 4:00 PM, and closed on Sundays.",
            keywords: ["hours", "open", "closed", "schedule", "time"]
        },
        {
            question: "Do you work on all Mercedes-Benz models?",
            answer: "Yes! As a certified Mercedes-Benz service technician, I work on all Mercedes-Benz models including sedans, SUVs, coupes, and AMG performance vehicles.",
            keywords: ["models", "vehicles", "cars", "types", "amg"]
        },
        {
            question: "How do I schedule an appointment?",
            answer: "You can schedule an appointment by calling us at (901) 555-5555, emailing stacey.williams@mbofcollierville.com, or visiting our website at mbofcollierville.com.",
            keywords: ["appointment", "schedule", "booking", "book"]
        },
        {
            question: "Do you provide loaner vehicles?",
            answer: "Yes, we offer complimentary loaner vehicles for qualifying service appointments. Please mention this when scheduling your appointment.",
            keywords: ["loaner", "rental", "car", "vehicle", "borrow"]
        },
        {
            question: "What payment methods do you accept?",
            answer: "We accept all major credit cards, debit cards, cash, and financing options are available for larger repairs.",
            keywords: ["payment", "pay", "cost", "price", "financing", "credit"]
        },
        {
            question: "Do you offer warranty on repairs?",
            answer: "Yes, all our repairs come with a comprehensive warranty. Mercedes-Benz parts have a manufacturer warranty, and our labor is guaranteed.",
            keywords: ["warranty", "guarantee", "coverage"]
        },
        {
            question: "Can you perform warranty work?",
            answer: "Absolutely! We are an authorized Mercedes-Benz service center and can perform all warranty-covered repairs.",
            keywords: ["warranty work", "covered", "authorized"]
        },
        {
            question: "How often should I service my Mercedes?",
            answer: "Mercedes-Benz recommends service every 10,000 miles or once a year, whichever comes first. However, specific maintenance intervals may vary by model.",
            keywords: ["maintenance", "schedule", "interval", "often", "frequency"]
        }
    ],

    // Common issues and solutions
    commonIssues: [
        {
            issue: "Check Engine Light",
            urgency: "medium",
            response: "A check engine light can indicate various issues. I recommend scheduling a diagnostic appointment so we can properly identify the problem with our Mercedes-Benz Star Diagnostic System."
        },
        {
            issue: "Brake Warning",
            urgency: "high",
            response: "Brake issues should be addressed immediately for your safety. Please call us right away at (901) 555-5555 to schedule an urgent appointment."
        },
        {
            issue: "Oil Change Due",
            urgency: "low",
            response: "Regular oil changes are important for engine longevity. We can typically accommodate oil changes within 24 hours. Would you like to schedule an appointment?"
        },
        {
            issue: "Tire Pressure Warning",
            urgency: "medium",
            response: "Low tire pressure can affect handling and fuel efficiency. You can stop by anytime during business hours for a quick tire pressure check and adjustment."
        }
    ],

    // AI Response Templates
    responses: {
        greeting: [
            "Hello! I'm here to help you with any questions about Mercedes-Benz service. What can I assist you with?",
            "Hi there! How can I help you today with your Mercedes-Benz service needs?",
            "Welcome! I'm Stacey's AI assistant. What would you like to know?"
        ],
        
        appointment: [
            "I'd be happy to help you schedule a service appointment! You can call us at (901) 555-5555 or email stacey.williams@mbofcollierville.com. What type of service do you need?",
            "Let's get your Mercedes scheduled for service! The best way to book is by calling (901) 555-5555. What service are you interested in?"
        ],
        
        location: [
            "We're located at 850 W Poplar Ave, Collierville, TN 38017. You can find directions at https://maps.google.com/?q=850+W+Poplar+Ave,+Collierville,+TN+38017",
            "Our service center is at 850 W Poplar Ave in Collierville, TN. We're easy to find just off the main road!"
        ],
        
        contact: [
            "You can reach us at (901) 555-5555 or email stacey.williams@mbofcollierville.com. We're also available through our website at mbofcollierville.com.",
            "Feel free to contact us! Phone: (901) 555-5555, Email: stacey.williams@mbofcollierville.com"
        ],
        
        unknown: [
            "I'm not sure about that specific question, but I'd be happy to connect you with Stacey directly. You can call (901) 555-5555 or email stacey.williams@mbofcollierville.com.",
            "That's a great question! For detailed information, please contact us at (901) 555-5555. We're here to help!",
            "I don't have specific information about that, but our service team can help! Call us at (901) 555-5555."
        ],
        
        thanks: [
            "You're welcome! Is there anything else I can help you with?",
            "Happy to help! Let me know if you need anything else.",
            "My pleasure! Feel free to ask if you have more questions."
        ]
    },

    // Intent Detection Keywords
    intents: {
        greeting: ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"],
        hours: ["hours", "open", "closed", "schedule", "time", "when"],
        services: ["service", "services", "what do you do", "offer", "provide", "work"],
        appointment: ["appointment", "schedule", "book", "booking", "reserve"],
        location: ["where", "location", "address", "directions", "find you", "map"],
        contact: ["contact", "call", "email", "phone", "reach"],
        price: ["cost", "price", "how much", "expensive", "cheap", "affordable"],
        urgent: ["urgent", "emergency", "asap", "immediately", "right now", "help"],
        thanks: ["thank", "thanks", "appreciate", "grateful"],
        models: ["model", "vehicle", "car", "amg", "sedan", "suv", "coupe"],
        warranty: ["warranty", "guarantee", "coverage", "covered"]
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeBase;
}
