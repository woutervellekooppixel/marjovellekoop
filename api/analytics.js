// Bezoekcijfers uit Google Analytics 4 voor /analytics.
// De sleutel van het service account staat in de Vercel-omgevingsvariabele GA_SERVICE_ACCOUNT
// (de volledige JSON). Dat account heeft alleen leesrechten op deze ene property.
const { createSign } = require('node:crypto');

const PROPERTY = '557946356';
const RANGES = [7, 28, 90];

let cachedToken = null;

const b64 = x => Buffer.from(typeof x === 'string' ? x : JSON.stringify(x)).toString('base64url');

async function token() {
  if (cachedToken && cachedToken.exp > Date.now() + 60_000) return cachedToken.value;
  const key = JSON.parse(process.env.GA_SERVICE_ACCOUNT);
  const now = Math.floor(Date.now() / 1000);
  const unsigned = `${b64({ alg: 'RS256', typ: 'JWT' })}.${b64({
    iss: key.client_email, scope: 'https://www.googleapis.com/auth/analytics.readonly',
    aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600,
  })}`;
  const sig = createSign('RSA-SHA256').update(unsigned).sign(key.private_key, 'base64url');
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion: `${unsigned}.${sig}` }),
  });
  const d = await r.json();
  if (!d.access_token) throw new Error('Inloggen bij Google Analytics mislukt');
  cachedToken = { value: d.access_token, exp: Date.now() + d.expires_in * 1000 };
  return cachedToken.value;
}

async function ga(tok, method, body) {
  const r = await fetch(`https://analyticsdata.googleapis.com/v1beta/properties/${PROPERTY}:${method}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${tok}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(d.error?.message || `Google Analytics gaf ${r.status}`);
  return d.rows || [];
}

const val = (row, i = 0) => Number(row.metricValues[i].value || 0);
const dim = (row, i = 0) => row.dimensionValues[i].value;
const list = (rows, n = 1) => rows.map(r => ({ name: dim(r), value: val(r), ...(n > 1 ? { users: val(r, 1) } : {}) }));

const TOTALS = ['activeUsers', 'newUsers', 'sessions', 'screenPageViews', 'averageSessionDuration', 'engagementRate'];

async function report(days) {
  const tok = await token();
  const cur = { startDate: `${days - 1}daysAgo`, endDate: 'today' };
  const prev = { startDate: `${2 * days - 1}daysAgo`, endDate: `${days}daysAgo` };
  const top = (dimension, metric, limit) => ga(tok, 'runReport', {
    dateRanges: [cur], dimensions: [{ name: dimension }], metrics: [{ name: metric }],
    orderBys: [{ metric: { metricName: metric }, desc: true }], limit,
  });
  const [totals, daily, pages, channels, sources, devices, cities, live] = await Promise.all([
    ga(tok, 'runReport', { dateRanges: [cur, prev], metrics: TOTALS.map(name => ({ name })) }),
    ga(tok, 'runReport', {
      dateRanges: [{ startDate: `${2 * days - 1}daysAgo`, endDate: 'today' }],
      dimensions: [{ name: 'date' }], metrics: [{ name: 'activeUsers' }, { name: 'screenPageViews' }],
      orderBys: [{ dimension: { dimensionName: 'date' } }], keepEmptyRows: true,
    }),
    ga(tok, 'runReport', {
      dateRanges: [cur], dimensions: [{ name: 'pagePath' }], metrics: [{ name: 'screenPageViews' }, { name: 'activeUsers' }],
      orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }], limit: 10,
    }),
    top('sessionDefaultChannelGroup', 'sessions', 8),
    top('sessionSource', 'sessions', 8),
    top('deviceCategory', 'activeUsers', 5),
    top('city', 'activeUsers', 8),
    ga(tok, 'runRealtimeReport', { metrics: [{ name: 'activeUsers' }] }),
  ]);

  // Met twee datumbereiken zet GA de naam van het bereik als dimensie in elke rij
  const byRange = {};
  for (const r of totals) byRange[dim(r)] = Object.fromEntries(TOTALS.map((m, i) => [m, val(r, i)]));
  const empty = Object.fromEntries(TOTALS.map(m => [m, 0]));

  // Dagreeks: vul ontbrekende dagen aan met 0 en splits in deze en de vorige periode
  const counts = Object.fromEntries(daily.map(r => [dim(r), { users: val(r, 0), views: val(r, 1) }]));
  const series = [];
  for (let i = 2 * days - 1; i >= 0; i--) {
    const d = new Date(Date.now() - i * 864e5).toLocaleDateString('sv-SE', { timeZone: 'Europe/Amsterdam' });
    series.push({ date: d, ...(counts[d.replaceAll('-', '')] || { users: 0, views: 0 }) });
  }

  return {
    days,
    updated: new Date().toISOString(),
    now: live[0] ? val(live[0]) : 0,
    current: byRange.date_range_0 || empty,
    previous: byRange.date_range_1 || empty,
    daily: series.slice(days),
    dailyPrevious: series.slice(0, days),
    pages: list(pages, 2),
    channels: list(channels),
    sources: list(sources),
    devices: list(devices),
    cities: list(cities).filter(c => c.name !== '(not set)'),
  };
}

module.exports = async (req, res) => {
  const days = Number(new URL(req.url, 'http://x').searchParams.get('dagen')) || 28;
  if (!RANGES.includes(days)) return res.status(400).json({ error: 'Kies 7, 28 of 90 dagen' });
  if (!process.env.GA_SERVICE_ACCOUNT) return res.status(503).json({ error: 'De koppeling met Google Analytics is nog niet ingesteld' });
  try {
    const data = await report(days);
    res.setHeader('Cache-Control', 'public, s-maxage=600, stale-while-revalidate=3600');
    res.status(200).json(data);
  } catch (e) {
    res.status(502).json({ error: e.message });
  }
};
