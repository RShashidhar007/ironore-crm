# Speech Recognition Troubleshooting Guide

## Issue: Speech Input Not Being Captured

If you're speaking but the text is not appearing, follow these debugging steps:

### Step 1: Check Browser Console
1. Open your browser's Developer Tools (Press F12)
2. Go to the **Console** tab
3. Look for messages starting with `[Speech Recognition]`

#### Expected Console Output When Using Mic:
```
[Speech Recognition] Started listening...
[Speech Recognition] onresult fired, event: ...
[Speech Recognition] Results length: 1
[Speech Recognition] Results: ...
[Speech Recognition] Transcript: "your spoken text" Is Final: true Target field: null
[Speech Recognition] Updating input field (chat) to: your spoken text
[Speech Recognition] Stopped listening
```

### Step 2: Check for Errors
Look for any error messages in the console like:
- `[Speech Recognition] Error event:` - Indicates what went wrong
- `[Speech Recognition] No results captured` - Microphone heard nothing
- `[Speech Recognition] Last result is empty` - Result data was malformed

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `no-speech` | No sound captured | Speak louder, closer to microphone |
| `audio-capture` | No microphone detected | Check microphone is connected and enabled |
| `permission-denied` | Microphone access blocked | Allow microphone access in browser settings |
| `network` | Network issue | Check internet connection |
| `not-allowed` | Browser doesn't allow access | Use Chrome, Edge, or Safari; update browser |

### Step 3: Verify Microphone Works
1. Test your microphone in another app (Discord, Teams, etc.)
2. Ensure microphone is not muted
3. Check Windows Sound Settings → Recording Devices

### Step 4: Test in Different Context

#### Testing in Chat (No Form)
1. Click the 🎙️ mic button
2. You should see: `[toggleListening] No form active, defaulting to chat input`
3. Speak text like "Hello"
4. Text should appear in the chat input field at the bottom

#### Testing in Quotation Form
1. Click "Ask for a Quotation"
2. Select a product
3. Click the 🎙️ mic button
4. You should see: `[toggleListening] Setting quotationQuantity field`
5. Speak a number like "100"
6. Number should appear in the Quantity field

#### Testing in Order Form
1. Click "Place an Order"
2. Select a product
3. Click the 🎙️ mic button
4. You should see: `[toggleListening] Setting orderQuantity field`
5. Speak a number
6. Number should appear in the Quantity field

### Step 5: Browser Compatibility
Speech Recognition works in:
- ✅ Chrome/Chromium (best support)
- ✅ Edge
- ✅ Safari (macOS/iOS)
- ❌ Firefox (not supported)

If you're using Firefox, switch to Chrome or Edge.

### Step 6: Check Mic Button Visual Feedback
- **🎙️ Outline** = Not listening
- **🎤 Filled** = Currently listening (should change while you speak)

### Step 7: Enable Detailed Logging
The code now includes comprehensive logging. Check for these patterns in console:

```javascript
[Speech Recognition] Started listening...           // Mic activated
[Speech Recognition] Results length: 1              // Got results
[Speech Recognition] Transcript: "text"             // What was heard
[Speech Recognition] Is Final: true                 // Final result (not interim)
```

If you see `Is Final: false`, the system is still waiting for you to finish speaking. Wait 2-3 seconds after speaking.

### Step 8: Test Microphone Permission
If you see `permission-denied` error:

**Chrome/Edge:**
1. Click the lock icon in address bar
2. Find "Microphone" setting
3. Change to "Allow"
4. Refresh page
5. Try again

**Safari:**
1. System Preferences → Security & Privacy → Microphone
2. Find and allow your browser
3. Refresh page

### Step 9: Network Requirements
- Must have active internet connection
- Web Speech API may use cloud services for processing (on some browsers)
- Firewall/VPN shouldn't block microphone access

### Step 10: Verify Form State
Open browser console and type:
```javascript
// Check if form is active when mic button clicked
console.log('quotationDetails:', quotationDetails)
console.log('orderDetails:', orderDetails)
```

If `selectedProduct` is null, the form isn't properly selected yet.

## Quick Checklist

- [ ] Using Chrome, Edge, or Safari browser
- [ ] Microphone is connected and not muted
- [ ] Browser has microphone permission granted
- [ ] Internet connection is active
- [ ] Speaker volume is reasonable
- [ ] Console shows `[Speech Recognition] Started listening...`
- [ ] Console shows `[Speech Recognition] Transcript:` with your text
- [ ] Form is properly selected before clicking mic

## Still Not Working?

If after all steps it still doesn't work, check the browser console for the exact error. Take a screenshot of the error and share it along with:
1. Browser name and version
2. Operating system
3. Whether microphone works in other apps
4. Exact error message from console

## Technical Details

### Speech Recognition Handler Flow:
```
User clicks mic button
    ↓
toggleListening() called
    ↓
Check which form is active
    ↓
Set selectedFieldRef.current (null for chat, field name for forms)
    ↓
recognitionRef.current.start()
    ↓
Browser prompts for microphone permission (first time)
    ↓
onstart event fires → "Started listening..."
    ↓
User speaks
    ↓
onresult event fires with transcript
    ↓
Route to correct field or input
    ↓
onend event fires → "Stopped listening"
```

### Result Object Structure:
```javascript
event.results = [
  [
    {
      transcript: "hello world",
      confidence: 0.95,
      ...
    }
  ]
]

// Last result: event.results[event.results.length - 1]
// Is final: event.results[lastIndex].isFinal
```
