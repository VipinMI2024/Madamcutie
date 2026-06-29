module.exports = async function(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { filePath, content } = req.body;
  const MAX_RETRIES = 3;

  async function fetchLatestSHA() {
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
    if (!getRes.ok && getRes.status !== 404) {
      const errText = await getRes.text();
      throw new Error(`Failed to fetch file metadata: ${errText}`);
    }
    const fileData = getRes.ok ? await getRes.json() : {};
    return fileData.sha || null;
  }

  async function attemptUpdate(sha) {
    const body = {
      message: `Admin panel update - ${new Date().toISOString()}`,
      content: Buffer.from(content).toString('base64'),
    };
    if (sha) body.sha = sha;

    const updateRes = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_REPO}/contents/${filePath}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
          'Content-Type': 'application/json',
          'User-Agent': 'madamcutie-admin'
        },
        body: JSON.stringify(body)
      }
    );
    return updateRes;
  }

  try {
    let lastError = null;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      console.log(`[save-content] Attempt ${attempt} for ${filePath}`);

      // Always fetch fresh SHA before each attempt
      let sha = null;
      try {
        sha = await fetchLatestSHA();
        console.log(`[save-content] Fresh SHA: ${sha}`);
      } catch (shaErr) {
        return res.status(500).json({ success: false, error: shaErr.message });
      }

      const updateRes = await attemptUpdate(sha);
      const updateBody = await updateRes.json();
      console.log(`[save-content] PUT status: ${updateRes.status}`);

      if (updateRes.status === 200 || updateRes.status === 201) {
        return res.json({ success: true });
      }

      if (updateRes.status === 409) {
        console.warn(`[save-content] 409 conflict on attempt ${attempt}, retrying...`);
        lastError = updateBody;
        // Small delay before retry
        await new Promise(r => setTimeout(r, 300 * attempt));
        continue;
      }

      // Other errors - don't retry
      return res.status(updateRes.status || 500).json({ success: false, error: updateBody });
    }

    // All retries exhausted
    return res.status(409).json({ 
      success: false, 
      error: 'Conflict could not be resolved after multiple retries. Please try again.',
      details: lastError
    });

  } catch (e) {
    console.error(`[save-content] Error:`, e);
    res.status(500).json({ success: false, error: e.message });
  }
}