
## Prequisites:

### **Create Virtual Environment**

```sh
python3 -m venv .venv
```

### **Activate Virtual Environment**

```sh
source .venv/bin/activate
```

### **Install Requirements**

```sh
pip install -r requirements.txt
```

--- 

## **🚀 Set Up Google Cloud for Google Forms API Authentication (Python)**
This guide walks you through configuring **Google Cloud** for using **Google Forms API** with a **Python script**.

---

### **✅ Step 1: Create a Google Cloud Project**
1. **Go to Google Cloud Console** → [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. **Give it a name** (e.g., `GoogleFormsBot`) and click **Create**.

---

### **✅ Step 2: Enable APIs**
1. **Open Google Cloud API Library** → [API Library](https://console.cloud.google.com/apis/library)
2. **Search for and enable these APIs:**
   - **Google Forms API** → [Enable Here](https://console.cloud.google.com/apis/library/forms.googleapis.com)
   - **Google Drive API** → [Enable Here](https://console.cloud.google.com/apis/library/drive.googleapis.com)

---

### **✅ Step 3: Configure OAuth Consent Screen**
1. **Go to** [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **"External"** (if using a personal Google account).
3. Click **Create**.
4. Fill out:
   - **App Name** (e.g., `Google Forms Auto-Filler`).
   - **User Support Email** (your Google email).
   - **Developer Email** (your email again).
5. Click **Save and Continue**.
6. **Scopes** → Click **"Add or Remove Scopes"** and add:
   ```
   https://www.googleapis.com/auth/forms
   https://www.googleapis.com/auth/drive
   ```
7. Click **Save and Continue** until finished.

---

### **✅ Step 4: Configure Test Users**

1. **On the "Test Users" page**, click **"Add Users"**.
2. **Enter your Google email** (or any other emails allowed to access the API).
3. Click **Save and Continue**.
4. Click **Back to Dashboard**.

🔹 **Why Add Test Users?**
   - Google restricts **unverified apps** to **test users only**.
   - Without adding users, you’ll get **Error 403: access_denied**.

---

### **✅ Step 5: Create OAuth Credentials**
1. **Go to** [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** → **OAuth Client ID**.
3. Select **Application Type: "Desktop App"**.
4. Click **Create**.
5. Click **Download JSON** → Save as `credentials.json`.

---

## **🚀  Run the Python Script**

1. **Ensure your virtual environment is activated**.
2. **Run the script:**
   ```sh
   python src/app.py
   ```
3. **Authorize the App in the Browser**:
   - A browser window will open.
   - Log in with your Google Account.
   - Click **"Allow"** to grant access.
   - After authorization, the script will generate `token.json` for future use.

---

