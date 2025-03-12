
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
## SKIP Google Cloud config if you already have a credentials.json file in your project!

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

## **🚀  How to use **



0. **Ensure your virtual environment is activated**.


1. **Get you form id from url**:
 https://docs.google.com/forms/d/HERE_IS_FORM_ID/edit 

2. **Get a pre-filled link for your form**: 

(https://spreadsheet.dev/submit-responses-to-google-form-apps-script)

The steps to get the pe-filled link are:
- Select the "three dots" ( ⠇) menu on the form that you see on the right hand side of the Send button.
- Select the Get pre-filled link menu item. This will open the form in a new tab (or a new browser window).
- Enter a sample response to each question on the form.
- Click the Get link button at the bottom of the form.
- A toast notification will appear on the screen that will allow you to copy the link to pre-fill the form with the responses you entered previously. Click the COPY LINK button on that notification to copy the link to your clipboard.
Example: https://storage.googleapis.com/spreadsheetdev-content/videos/get-google-form-pre-filled-link-0.mp4?preload=metadata

Once you complete the steps to get the pre-filled link, you should have it saved in your clipboard. Paste the link somewhere where you can retrieve it later. We will be using this link in step 3 of this tutorial.
The link should look like this:

```
https://docs.google.com/forms/d/e/<FORM_ID>/viewform?usp=pp_url&entry.240448027=Name&entry.692437909=name@example.com&entry.211305940=Hiking&entry.1158868403=Museum+visit&entry.1576266760=No+meat+or+poultry&entry.1576266760=No+eggs&entry.1576266760=__other_option__&entry.1576266760.other_option_response=No+nuts+please
```

https://storage.googleapis.com/ssdefault/images/1Q9qWa00QVYb549-moqh3VvnZol9C6SaBqNiuIqxH82w/7884f3296b510fad9ecf62f4e7d1763e.png

Example:
```
https://docs.google.com/forms/d/e/1FAIpQLScq30KM2lk0YDAkA-iwx4L7sBZdWldduEVsF7pF1coMW2Kr1Q/viewform?usp=pp_url&entry.343824263=blabla@gmail.com&entry.1744160725=test&entry.448924330=3D+Printers&entry.448924330=IOT&entry.448924330=E-Commerce&entry.560853869=2&entry.973603086=Slightly&entry.2145368981=Quite+a+bit&entry.1896969503=Moderately&entry.38137748=dfff&entry.1488704822=Rom&entry.1604402633=dd
```

```
TEXT: entry.343824263=blabla@gmail.com
CHECKBOX (multiple answers): entry.448924330=3D+Printers&entry.448924330=IOT&entry.448924330=E-Commerce  
RADIO (1 answer): entry.560853869=2
MATRIX (1 answer per each question): entry.973603086=Slightly&entry.2145368981=Quite+a+bit&entry.1896969503=Moderately
```


3. **Run the script:**
   ```sh
   python src/read_form.py --form-id xxxxxxxxx
   ```

4. **Authorize the App in the Browser**:
   - A browser window will open.
   - Log in with your Google Account.
   - Click **"Allow"** to grant access.
   - After authorization, the script will generate `token.json` for future use.

5. **The read_form script will create two files under 'data' directory**:

    1. form_data_<FORM_ID>.json (needed for visualising the form for debug purposes)
    2. entry_data_<FORM_ID>.json

    IMPORTANT!
    You need to identify and fill accordingly the `entry.XXXX` for each title. Use the pre-fill url generated at step 2 for identification. 

    If the form will be updated, I will advise you to delete the `entry_data_<FORM_ID>.json` so you can have generate a fresh one.

6. **Run the script:**
   ```sh
   python src/submit_form.py --form-id xxxxxxxxx
   ```

This will automatically fill the forms based on entry_data_<FORM_ID>.json with random responses.

---
