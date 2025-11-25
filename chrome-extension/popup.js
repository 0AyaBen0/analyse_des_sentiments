// popup.js
const apiInput = document.getElementById('apiUrl');
const refreshBtn = document.getElementById('refreshBtn');
const status = document.getElementById('status');
const statsDiv = document.getElementById('stats');
const commentsList = document.getElementById('commentsList');
const darkToggle = document.getElementById('darkToggle');
const copyBtn = document.getElementById('copyBtn');
const exportBtn = document.getElementById('exportBtn');

let currentData = []; // {author,text,replies, sentiment, confidence}
let chart = null;

// load saved apiUrl
chrome.storage.local.get(['apiUrl','theme'], (res) => {
  if(res.apiUrl) apiInput.value = res.apiUrl;
  if(res.theme === 'dark') document.body.classList.add('dark');
});

darkToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  const theme = document.body.classList.contains('dark') ? 'dark' : 'light';
  chrome.storage.local.set({ theme });
});

// utility to call content script
function extractCommentsFromTab(callback) {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if(!tabs[0]) { callback({success:false, error:'no active tab'}); return; }
    chrome.tabs.sendMessage(tabs[0].id, { action: 'extract_comments', limit: 200 }, (res) => {
      callback(res);
    });
  });
}

// call API
async function callApi(apiUrl, comments) {
  const payload = { comments: comments.map(c => c.text) };
  const resp = await fetch(apiUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  if(!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

function renderStats(stats, total) {
  statsDiv.innerHTML = `
    <p>Total comments: ${total}</p>
    <p>Positif: ${stats["1"] || 0} — Neutre: ${stats["0"] || 0} — Négatif: ${stats["-1"] || 0}</p>
  `;
}

function renderComments(list) {
  commentsList.innerHTML = '';
  list.forEach((c, idx) => {
    const div = document.createElement('div');
    div.className = 'comment';
    div.innerHTML = `<strong>${c.author || 'User'}</strong>
                     <p>${escapeHtml(c.text)}</p>
                     <small>Sentiment: ${c.sentiment} — conf: ${c.confidence ?? 'N/A'}</small>`;
    commentsList.appendChild(div);
  });
}

function escapeHtml(s){ return (s||'').replaceAll('<','&lt;').replaceAll('>','&gt;'); }

// create/update chart
function drawChart(counts){
  const ctx = document.getElementById('pieChart').getContext('2d');
  const data = [counts["1"]||0, counts["0"]||0, counts["-1"]||0];
  const labels = ['Positif','Neutre','Négatif'];
  if(chart) { chart.data.datasets[0].data = data; chart.update(); return; }
  chart = new Chart(ctx, {
    type: 'pie',
    data: { labels, datasets: [{ data }] },
    options: { responsive: true }
  });
}

// copy and export helpers
function buildCSV(data){
  const header = ['author','text','sentiment','confidence'];
  const rows = data.map(d => [d.author, `"${d.text.replace(/"/g,'""')}"`, d.sentiment, d.confidence ?? '']);
  return [header.join(','), ...rows.map(r=>r.join(','))].join('\n');
}

copyBtn.addEventListener('click', async () => {
  const csv = buildCSV(currentData);
  await navigator.clipboard.writeText(csv);
  status.innerText = 'CSV copied to clipboard ✅';
});

exportBtn.addEventListener('click', () => {
  const csv = buildCSV(currentData);
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'comments_sentiment.csv';
  a.click();
  URL.revokeObjectURL(url);
});

// main flow
refreshBtn.addEventListener('click', () => {
  const apiUrl = apiInput.value.trim();
  if(!apiUrl) { status.innerText='Set API URL first'; return; }
  chrome.storage.local.set({ apiUrl });
  status.innerText = 'Extracting comments...';
  extractCommentsFromTab(async (res) => {
    if(!res || !res.success) { status.innerText = 'Could not extract comments'; return; }
    const raw = res.comments;
    status.innerText = `Sending ${raw.length} comments to API...`;
    try {
      const apiResp = await callApi(apiUrl, raw);
      // apiResp expected: { sentiments: [...], stats: {...}, total: n, confidences?: [...] }
      const preds = apiResp.sentiments || [];
      const confidences = apiResp.confidences || [];
      currentData = raw.map((r,i) => ({
        author: r.author,
        text: r.text,
        replies: r.replies,
        sentiment: preds[i],
        confidence: confidences[i] ?? null
      }));
      renderStats(apiResp.stats || {}, apiResp.total || preds.length);
      drawChart(apiResp.stats || {});
      renderComments(currentData);
      status.innerText = 'Done ✅';
    } catch (err) {
      status.innerText = 'API error: ' + err.message;
    }
  });
});
