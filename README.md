# 🎤 Voice Agent Studio

**Generate AI-powered radio host voice lines using ElevenLabs + ChatGPT.**  
Create host personalities, add topic prompts, and generate audio with optional music intros.

---

## 🚀 Features

- 🎙️ Add and manage custom radio hosts
- 🧠 Generate personality-driven lines using ChatGPT
- 🔊 Voice-over lines with ElevenLabs TTS
- 🎵 Add intro music from Supabase
- 📥 Download or delete generated voice lines

---

## 🛠 Tech Stack

**Frontend:**  
HTML + Vanilla JS + CSS (no frameworks)

**Backend:**  
Flask + Python

**Storage:**  
Supabase (audio uploads) https://supabase.com/dashboard/project/epcfwbrehvlsyprxzcrn/storage/buckets/audio

**Voice:**  
[ElevenLabs API](https://www.elevenlabs.io/)

**AI:**  
[OpenAI ChatGPT](https://platform.openai.com/)

---

## 🧪 Optional Tools

- 🪪 **Favicon**  
  Place your favicon at: `static/img/favicon.png`
- 🎵 **Music Intros**  
  Upload `.mp3` files manually to Supabase:
  https://supabase.com/dashboard/project/epcfwbrehvlsyprxzcrn/storage/buckets/audio
  ```text
  Bucket: audio
  Path: audio/soundbite/
