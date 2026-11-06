/**
 * Utility to load channel data from channels.full.json
 * Provides fallback mechanisms for different runtime environments
 */

const fs = require('fs');
const path = require('path');

/**
 * Load channels from the JSON file
 * @returns {Array} Array of channel objects, or empty array on error
 */
function loadChannels() {
  try {
    // Primary method: Use require for JSON (works in most Node.js environments)
    try {
      const channels = require('../data/channels.full.json');
      return channels;
    } catch (requireError) {
      // Fallback: Use fs.readFileSync for environments where require may fail
      console.warn('require() failed, falling back to fs.readFileSync:', requireError.message);
      
      const channelsPath = path.join(__dirname, '../data/channels.full.json');
      const rawData = fs.readFileSync(channelsPath, 'utf8');
      const channels = JSON.parse(rawData);
      return channels;
    }
  } catch (error) {
    // Log error and return empty array to prevent crashes
    console.error('Error loading channels:', error.message);
    return [];
  }
}

// CommonJS export
module.exports = { loadChannels };
