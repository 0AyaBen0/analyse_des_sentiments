// content.js
// Expose a function to extract visible comments and replies (thread-aware)
function extractComments(limit = 200) {
  // select comment text nodes (YouTube uses #content-text)
  const commentEls = Array.from(document.querySelectorAll('#content-text'));
  const comments = [];

  for (let i = 0; i < commentEls.length && comments.length < limit; i++) {
    const el = commentEls[i];
    // get parent comment element to capture context if needed
    const parent = el.closest('ytd-comment-thread-renderer') || el.parentElement;
    const author = parent?.querySelector('#author-text')?.innerText?.trim() || '';
    const text = el.innerText.trim();
    // try to find replies for this comment (if any)
    const replies = Array.from(parent?.querySelectorAll('ytd-comment-replies-renderer #content-text') || [])
      .map(r => r.innerText.trim());
    comments.push({ author, text, replies });
  }
  return comments;
}

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'extract_comments') {
    const data = extractComments(msg.limit || 200);
    sendResponse({ success: true, comments: data });
  }
});

// observe DOM changes and notify popup (optional improvement)
const observer = new MutationObserver((mutations) => {
  // could send message to background/page if needed
});
observer.observe(document.body, { childList: true, subtree: true });
