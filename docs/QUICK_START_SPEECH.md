# Quick Start: Speech Recognition

## 🚀 Quick Test (30 Seconds)

1. **Open App**
2. **Open Console**: Press `F12` 
3. **Click 🎙️ Button**: Bottom of chat
4. **Speak**: Say "hello"
5. **Check**: Look for `[Speech Recognition] Transcript: "hello"` in console

✅ If you see it → Speech is working!  
❌ If not → Open `SPEECH_RECOGNITION_TROUBLESHOOTING.md`

---

## 📍 Where to Find Mic Button

```
┌─────────────────────────────────────┐
│     CRM Assistant Chat              │
├─────────────────────────────────────┤
│ Bot: How can I help you?            │
└─────────────────────────────────────┘
 🎙️  ┌──────────────────────┐  Send
    │ Type or speak...      │
    └──────────────────────┘
    ↑
  Mic Button (Click to speak)
```

---

## 🎤 How to Use Speech

### In Chat
1. Click 🎙️ button
2. Speak any message
3. Text appears in input field

### In Quotation Form
1. Click "Ask for a Quotation"
2. Select a product
3. Click 🎙️ button (in form context)
4. Speak a number (e.g., "one hundred")
5. Number appears in Quantity field

### In Order Form
1. Click "Place an Order"
2. Select a product
3. Click 🎙️ button (in form context)
4. Speak a number
5. Number appears in Quantity field

---

## 🔴 Visual Indicators

| Button | Meaning |
|--------|---------|
| 🎙️ | Ready to listen |
| 🎤 | Currently listening |

---

## ⚠️ If Not Working

### Step 1: Check Microphone
- [ ] Microphone is plugged in
- [ ] Microphone is not muted
- [ ] Test in another app (Discord, Teams)

### Step 2: Check Browser
- [ ] Using Chrome, Edge, or Safari
- [ ] NOT using Firefox
- [ ] Updated to latest version

### Step 3: Check Permission
- [ ] Browser asked for microphone permission
- [ ] You clicked "Allow"
- [ ] Try refreshing page if you see no prompt

### Step 4: Check Console
1. Press F12
2. Look for red error messages
3. Search for `[Speech Recognition]`
4. Note the exact error

### Step 5: Get Help
Share this from console:
- Exact error message
- Browser name + version
- Operating system

---

## 📱 Supported Browsers

| Browser | Status |
|---------|--------|
| Chrome | ✅ Works great |
| Edge | ✅ Works great |
| Safari | ✅ Works |
| Firefox | ❌ Not supported |

---

## 💬 What You Can Say

### Numbers (Quantities)
- "one", "two", "ten", "twenty", "fifty", "hundred", "thousand"
- Numbers will be converted to digits (e.g., "one hundred" → "100")

### Text (Chat)
- Anything you want to type in chat
- Speak naturally and clearly

### Dates (Complaint form)
- Speak the date naturally
- System will format it properly

---

## 🔧 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| "No microphone found" | Check microphone is connected |
| "Permission denied" | Allow microphone in browser settings |
| "I didn't hear anything" | Speak louder, closer to mic |
| "Not supported" | Use Chrome, Edge, or Safari |
| Text not appearing | Check console for errors (F12) |

---

## 📚 Full Documentation

For detailed troubleshooting:
→ See `SPEECH_RECOGNITION_TROUBLESHOOTING.md`

For technical details:
→ See `SPEECH_RECOGNITION_FIX.md`

---

## ✨ Tips for Best Results

1. **Speak Clearly** - Enunciate each word
2. **Pause Before Speaking** - Wait 1 second after clicking mic
3. **Speak at Normal Volume** - Don't shout or whisper
4. **Be Close to Mic** - 6-12 inches away
5. **Quiet Environment** - Minimize background noise
6. **Wait for Response** - Don't immediately check; give it 2-3 seconds

---

## 🎯 Common Phrases

### Quotation
"Ask for a Quotation" → Select Product → 🎙️ → "one hundred"

### Order
"Place an Order" → Select Product → 🎙️ → "fifty"

### Complaint
"Raise a Complaint" → Select Category → 🎙️ → Speak description

---

## 📞 Still Need Help?

1. Open Console (F12)
2. Click mic button
3. Speak
4. Take screenshot of console
5. Note any [Speech Recognition] error messages
6. Share with support team

---

**Last Updated**: August 26, 2026  
**Version**: 2.0 (Fixed & Enhanced)  
**Status**: Production Ready ✅
