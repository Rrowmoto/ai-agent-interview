// Vercel Serverless Function - 代理 TokenRhythm API
const https = require('https');

module.exports = async (req, res) => {
  // 设置 CORS 响应头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // 处理 OPTIONS 预检请求
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 只允许 POST 请求
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { messages, model, temperature, max_tokens } = req.body || {};

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'messages is required' });
    }

    const apiData = JSON.stringify({
      model: model || 'deepseek-v4-flash',
      messages: messages,
      temperature: temperature || 0.7,
      max_tokens: max_tokens || 2000,
    });

    const options = {
      hostname: 'tokenrhythm.studio',
      port: 443,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk_tr_l6fAS_vsapXohFQPkmuVR7gZI9D1Vn6PxmkddCNT8Fc',
        'Content-Length': Buffer.byteLength(apiData),
      },
      timeout: 30000,
    };

    const apiReq = https.request(options, (apiRes) => {
      let body = '';
      apiRes.on('data', (chunk) => {
        body += chunk;
      });
      apiRes.on('end', () => {
        try {
          const json = JSON.parse(body);
          return res.status(apiRes.statusCode || 200).json(json);
        } catch (e) {
          return res.status(500).json({ error: 'Invalid response from API', raw: body.substring(0, 200) });
        }
      });
    });

    apiReq.on('error', (err) => {
      return res.status(500).json({ error: err.message });
    });

    apiReq.on('timeout', () => {
      apiReq.destroy();
      return res.status(504).json({ error: 'API request timeout' });
    });

    apiReq.write(apiData);
    apiReq.end();
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};