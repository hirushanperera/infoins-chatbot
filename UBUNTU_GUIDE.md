# 🚀 UBUNTU SETUP GUIDE - Infoins V4 Chatbot

## Complete Step-by-Step Guide for Ubuntu Users

---

## 📋 STEP 1: Get Your Google AI API Key

### 1.1 Open Your Web Browser
- Open Firefox or Chrome

### 1.2 Go to Google AI Studio
- Visit: **https://aistudio.google.com/**
- Sign in with your Google account

### 1.3 Create API Key
1. Look for **"Get API key"** button (usually on the left sidebar)
2. Click **"Create API key"**
3. Choose **"Create API key in new project"**
4. **COPY** the key that appears (it starts with `AIzaSy...`)
5. **SAVE IT** somewhere safe - you'll need it in a minute!

---

## 📦 STEP 2: Install Python and Required Tools

### 2.1 Open Terminal
- Press `Ctrl + Alt + T` to open Terminal

### 2.2 Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### 2.3 Install Python and pip
```bash
sudo apt install python3 python3-pip -y
```

### 2.4 Verify Installation
```bash
python3 --version
pip3 --version
```

You should see version numbers (like Python 3.10.x)

---

## 📁 STEP 3: Download and Extract Your Chatbot Files

### 3.1 Create a Folder for Your Chatbot
```bash
cd ~
mkdir infoins-chatbot
cd infoins-chatbot
```

### 3.2 Download the Files
- You should have downloaded all the chatbot files
- Move them to the `infoins-chatbot` folder:
  ```bash
  # If files are in Downloads folder:
  cp ~/Downloads/*.py ~/infoins-chatbot/
  cp ~/Downloads/*.html ~/infoins-chatbot/
  cp ~/Downloads/*.txt ~/infoins-chatbot/
  cp ~/Downloads/*.sh ~/infoins-chatbot/
  cp ~/Downloads/.env.example ~/infoins-chatbot/
  ```

### 3.3 OR: If You Have a ZIP File
```bash
cd ~/Downloads
unzip infoins-chatbot.zip
mv infoins-chatbot ~/
cd ~/infoins-chatbot
```

---

## 🔧 STEP 4: Install Python Packages

### 4.1 Install Required Packages
```bash
cd ~/infoins-chatbot
pip3 install -r requirements.txt
```

Wait for it to finish installing...

---

## 🔑 STEP 5: Set Up Your API Key

### 5.1 Create Environment File
```bash
cp .env.example .env
nano .env
```

### 5.2 Add Your API Key
1. You'll see a text editor open
2. Replace `your_api_key_here` with your actual API key from Step 1
3. It should look like this:
   ```
   GEMINI_API_KEY=AIzaSyDEFGH1234567890abcdefghijklmno
   ```
4. Press `Ctrl + X` to exit
5. Press `Y` to save
6. Press `Enter` to confirm

---

## ▶️ STEP 6: Run Your Chatbot!

### 6.1 Make the Start Script Executable
```bash
chmod +x start.sh
```

### 6.2 Run the Chatbot
```bash
./start.sh
```

### 6.3 What You'll See
You should see something like:
```
✅ API key found!
📦 Checking Python packages...
✅ Packages installed!

🌐 Starting server...
📱 Access URLs:
   Local:   http://localhost:5000
   Network: http://192.168.1.100:5000

Press Ctrl+C to stop the server
```

---

## 🌐 STEP 7: Open the Chatbot in Your Browser

### 7.1 On Your Ubuntu Computer
- Open Firefox or Chrome
- Go to: **http://localhost:5000**
- You should see the chatbot interface! 🎉

### 7.2 On Your Phone (Same WiFi Network)
1. Look at the **Network** URL from Step 6.3 (e.g., `http://192.168.1.100:5000`)
2. On your phone's browser, type that exact URL
3. Make sure your phone is on the same WiFi network!

---

## 🛑 STEP 8: Stop the Chatbot

### To Stop the Server:
- In the terminal where it's running, press: `Ctrl + C`

### To Start Again Later:
```bash
cd ~/infoins-chatbot
./start.sh
```

---

## 🔥 ALTERNATIVE METHOD: Manual Run (Without Script)

If the start.sh script doesn't work, you can run it manually:

### Step 1: Set Environment Variable
```bash
cd ~/infoins-chatbot
export GEMINI_API_KEY="AIzaSy_YOUR_ACTUAL_KEY_HERE"
```

### Step 2: Run the Server
```bash
python3 chatbot_server.py
```

### Step 3: Open Browser
- Go to http://localhost:5000

---

## 📱 ACCESSING FROM YOUR PHONE - DETAILED GUIDE

### Find Your Ubuntu Computer's IP Address:
```bash
hostname -I | awk '{print $1}'
```

This will show something like: `192.168.1.100`

### On Your Phone:
1. Connect to the SAME WiFi network as your computer
2. Open browser (Chrome, Firefox, Safari)
3. Type in the address bar: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`
4. Press Go!

### If It Doesn't Work:
#### Check Firewall:
```bash
# Allow port 5000 through firewall
sudo ufw allow 5000
```

---

## 🌍 DEPLOY ONLINE (Optional - Access from Anywhere!)

### Why Deploy Online?
- Access from anywhere, not just your WiFi
- Share with others
- No need to keep your computer running

### Best Free Options for Ubuntu Users:

### Option 1: Render.com (Recommended)

1. **Sign Up**
   - Go to https://render.com
   - Sign up for free account

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub account (or upload files)

3. **Configure**
   - Name: infoins-chatbot
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn chatbot_server:app`

4. **Add Environment Variable**
   - Key: `GEMINI_API_KEY`
   - Value: Your actual API key

5. **Deploy!**
   - Render will give you a URL like: `https://your-chatbot.onrender.com`

### Option 2: Railway.app

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Add environment variable: `GEMINI_API_KEY`
5. Railway auto-deploys!

### Option 3: PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Sign up for free account
3. Upload your files
4. Set up a Flask web app
5. Add API key in settings

---

## 🐛 TROUBLESHOOTING

### Problem: "pip3: command not found"
**Solution:**
```bash
sudo apt install python3-pip -y
```

### Problem: "Permission denied" when running start.sh
**Solution:**
```bash
chmod +x start.sh
```

### Problem: "Module not found" errors
**Solution:**
```bash
pip3 install --user google-genai flask flask-cors
```

### Problem: "Port 5000 already in use"
**Solution:**
```bash
# Find what's using port 5000
sudo lsof -i :5000
# Kill it (replace PID with actual number)
sudo kill -9 PID

# OR use a different port - edit chatbot_server.py
# Change: app.run(host='0.0.0.0', port=5000)
# To:     app.run(host='0.0.0.0', port=8080)
```

### Problem: Can't access from phone
**Solution:**
```bash
# 1. Check firewall
sudo ufw allow 5000

# 2. Check your IP
hostname -I

# 3. Make sure phone is on same WiFi
# 4. Try: http://YOUR_IP:5000 (not https)
```

### Problem: API Key not working
**Solution:**
- Make sure you copied the entire key (starts with AIzaSy)
- Check if there are extra spaces
- Go back to https://aistudio.google.com/ and create a new key
- Make sure billing is enabled if required

---

## 📝 QUICK REFERENCE COMMANDS

### Start Chatbot:
```bash
cd ~/infoins-chatbot
./start.sh
```

### Stop Chatbot:
```
Press Ctrl + C in the terminal
```

### Check if Server is Running:
```bash
curl http://localhost:5000
```

### Find Your IP Address:
```bash
hostname -I
```

### Edit API Key:
```bash
nano ~/infoins-chatbot/.env
```

### Update Packages:
```bash
cd ~/infoins-chatbot
pip3 install -r requirements.txt --upgrade
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Installed Python and pip
- [ ] Got Google AI API key
- [ ] Created infoins-chatbot folder
- [ ] Downloaded all files
- [ ] Installed requirements.txt
- [ ] Created .env file with API key
- [ ] Run start.sh successfully
- [ ] Opened http://localhost:5000 in browser
- [ ] Tested chatbot with a question
- [ ] (Optional) Accessed from phone
- [ ] (Optional) Deployed online

---

## 🎉 YOU'RE DONE!

Your chatbot should now be working! If you have any issues, check the Troubleshooting section above.

### Need Help?
- Double-check each step
- Make sure API key is correct
- Ensure all files are in the right folder
- Check terminal for error messages

---

**Made with ❤️ for Ubuntu Users**
