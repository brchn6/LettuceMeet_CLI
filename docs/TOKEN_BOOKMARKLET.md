# Token Extraction Bookmarklet

A simple tool to grab your LettuceMeet session token from the browser.

## One-time setup

1. Copy the code below
2. In Chrome, bookmark any page (Ctrl+D / Cmd+D)
3. **Edit the bookmark**: replace the URL with the pasted code
4. Name it something like "LettuceMeet Token"

## The bookmarklet code

```javascript
javascript:(function(){let t=localStorage.getItem('akoko:session_token');if(t){navigator.clipboard.writeText(t).then(()=>{alert('Token copied to clipboard! Paste it to the agent.')}).catch(()=>{let p=prompt('Copy this token:',t);if(p===null)alert('Cancelled.')})}else{alert('No akoko:session_token found in localStorage. Are you on lettucemeet.com?')}})();
```

## How to use

1. Go to [lettucemeet.com](https://lettucemeet.com) (must be logged in)
2. Click the bookmarklet
3. A popup says "Token copied to clipboard!"
4. Paste it to the agent with `login <token>`

## How it works

The bookmarklet runs a tiny JavaScript snippet on the page:

1. Reads `localStorage.getItem('akoko:session_token')`
2. Copies the value to clipboard via `navigator.clipboard.writeText()`
3. Falls back to a prompt dialog if clipboard access fails

No data leaves your browser. No network requests.
