const https = require('https');

module.exports = async function(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { filePath, content } = req.body;

  try {
    const getRes = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_REPO}/contents/${filePath}`,
      { 
        headers: { 
          Authorization: `Bearer ${process.env.GITHUB_TOKEN}`, 
          'User-Agent': 'madamcutie-admin' 
        } 
      }
    );
    const fileData = await getRes.json();
    
    const updateRes = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_REPO}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
          'Content-Type': 'application/json',
          'User-Agent': 'madamcutie-admin'
        },
        body: JSON.stringify({
          message: 'Admin panel update',
          content: Buffer.from(content).toString('base64'),
          sha: fileData.sha,
        })
      }
    );

    if (updateRes.ok) {
      res.json({ success: true });
    } else {
      const err = await updateRes.json();
      res.status(500).json({ success: false, error: err });
    }
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
}