# Token Bookmarklet

One-click token extraction for LettuceMeet.

## Setup

Create a bookmark with this URL:

```
javascript:(function(){let t=localStorage.getItem('akoko:session_token');if(t){navigator.clipboard.writeText(t).then(()=>{alert('Token copied!')}).catch(()=>{prompt('Copy:',t)})}else{alert('Not found')}})();
```

## Use

1. Go to lettucemeet.com (logged in)
2. Click the bookmarklet
3. Token is on your clipboard
