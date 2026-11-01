/**
 * vcard.js – vCard 3.0 generator and download helper
 */

'use strict';

function generateVCard() {
  const vcard = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    'FN:Stacey Williams',
    'N:Williams;Stacey;;;',
    'TITLE:Certified Service Technician',
    'ORG:Mercedes-Benz of Collierville',
    'TEL;TYPE=WORK,VOICE:+19014943990',
    'EMAIL;TYPE=WORK:stacey.williams@mbcollierville.com',
    'ADR;TYPE=WORK:;;1088 W. Poplar Ave;Collierville;TN;;USA',
    'URL:https://www.mbcollierville.com',
    'END:VCARD',
  ].join('\r\n');

  const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'StaceyWilliams.vcf';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  if (typeof showToast === 'function') {
    showToast('📇 Contact saved!');
  }
}
