// Netlify function: receives charity suggestion form data and writes to Airtable
exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
  const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID;
  const TABLE_ID = 'tblCxRg6DJV9z4nwQ'; // Charity Suggestions

  if (!AIRTABLE_API_KEY || !AIRTABLE_BASE_ID) {
    return { statusCode: 500, body: JSON.stringify({ error: 'Missing Airtable config' }) };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch {
    // fallback: try URL-encoded
    const params = new URLSearchParams(event.body);
    body = Object.fromEntries(params.entries());
  }

  const fields = {
    'Country': body.country_selected || '',
    'Charity Clicked': body.charity_clicked || '',
    'Custom Suggestion': body.custom_suggestion || '',
    'Email': body.user_email || '',
    'Submitted At': body.timestamp || new Date().toISOString()
  };

  // Remove empty optional fields
  if (!fields['Email']) delete fields['Email'];
  if (!fields['Custom Suggestion']) delete fields['Custom Suggestion'];
  if (!fields['Charity Clicked']) delete fields['Charity Clicked'];

  try {
    const res = await fetch(`https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${TABLE_ID}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${AIRTABLE_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ fields })
    });

    if (!res.ok) {
      const err = await res.text();
      console.error('Airtable error:', err);
      return { statusCode: 500, body: JSON.stringify({ error: 'Airtable write failed' }) };
    }

    return { statusCode: 200, body: JSON.stringify({ success: true }) };
  } catch (err) {
    console.error('Function error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: 'Internal error' }) };
  }
};
