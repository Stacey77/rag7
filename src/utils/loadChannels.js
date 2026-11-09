/**
 * Load channels from the channels.full.json dataset
 * 
 * Uses require() with a fallback to fs.readFileSync for environments
 * where JSON require may fail (e.g., some bundlers or runtime environments)
 * 
 * @returns {Array} Array of channel objects, or empty array on error
 */

function loadChannels() {
  try {
    // Primary method: use require for environments that support it
    const channels = require('../data/channels.full.json');
    return channels;
  } catch (requireError) {
    console.error('Failed to load channels via require(), attempting fs.readFileSync fallback:', requireError.message);
    
    try {
      // Fallback method: use fs.readFileSync
      const fs = require('fs');
      const path = require('path');
      const channelsPath = path.join(__dirname, '../data/channels.full.json');
      const channelsData = fs.readFileSync(channelsPath, 'utf8');
      const channels = JSON.parse(channelsData);
      return channels;
    } catch (fsError) {
      console.error('Failed to load channels via fs.readFileSync:', fsError.message);
      return [];
    }
  }
}

module.exports = loadChannels;
