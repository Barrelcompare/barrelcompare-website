// Returns vote tallies for a given country from Airtable
exports.handler = async function(event) {
  const country = (event.queryStringParameters || {}).country;
  if (!country) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Missing country param' }) };
  }

  const KEY  = process.env.AIRTABLE_API_KEY;
  const BASE = process.env.AIRTABLE_BASE_ID;
  const TABLE = 'tblCxRg6DJV9z4nwQ'; // Charity Suggestions

  const formula = encodeURIComponent(
    "AND({Country}='" + country.replace(/'/g, "\\'") + "',{Charity Clicked}!='')"
  );
  const url = `https://api.airtable.com/v0/${BASE}/${TABLE}` +
    `?filterByFormula=${formula}&fields[]=Charity+Clicked&maxRecords=500`;

  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${KEY}` }
    });
    const data = await res.json();

    const tallies = {};
    for (const record of (data.records || [])) {
      const name = record.fields['Charity Clicked'];
      if (name) tallies[name] = (tallies[name] || 0) + 1;
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=60'
      },
      body: JSON.stringify(tallies)
    };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: 'Failed to fetch tallies' }) };
  }
};
