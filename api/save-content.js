module.exports = async function(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { filePath, content } = req.body;

  try {
    const getRes = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_REPO}/contents/${filePath}?t=${Date.now()}`,
      { 
        cache: 'no-store',
        headers: { 
          Authorization: `Bearer ${process.env.GITHUB_TOKEN}`, 
          'User-Agent': 'madamcutie-admin',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        } 
      }
    );
    
    console.log(`[save-content] GET metadata for ${filePath} status: ${getRes.status}`);
    
    if (!getRes.ok && getRes.status !== 404) {
      const errText = await getRes.text();
      console.error(`[save-content] GET metadata failed:`, errText);
      return res.status(getRes.status).json({ success: false, error: `Failed to fetch file metadata: ${errText}` });
    }
    
    const fileData = getRes.ok ? await getRes.json() : {};
    console.log(`[save-content] File SHA: ${fileData.sha}`);

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

    const updateBody = await updateRes.json();
    console.log(`[save-content] PUT update status: ${updateRes.status}`, JSON.stringify(updateBody));

    if (updateRes.status === 200 || updateRes.status === 201) {
      res.json({ success: true });
    } else {
      res.status(updateRes.status || 500).json({ success: false, error: updateBody });
    }
  } catch (e) {
    console.error(`[save-content] Error handling save:`, e);
    res.status(500).json({ success: false, error: e.message });
  }
}