/**
 * Load channels from the full channel dataset
 * @returns {Array} Array of channel objects, or empty array on error
 */
function loadChannels() {
  try {
    // Try to require the JSON directly (works in most Node.js environments)
    return require('../data/channels.full.json');
  } catch (requireError) {
    console.error('Failed to require channels.full.json, trying fs.readFileSync:', requireError.message);
    
    try {
      // Fallback to fs.readFileSync for environments where JSON require may fail
      const fs = require('fs');
      const path = require('path');
      const channelsPath = path.join(__dirname, '../data/channels.full.json');
      const data = fs.readFileSync(channelsPath, 'utf8');
      return JSON.parse(data);
    } catch (fsError) {
      console.error('Failed to load channels.full.json with fs.readFileSync:', fsError.message);
      return [];
    }
  }
}

module.exports = { loadChannels };
