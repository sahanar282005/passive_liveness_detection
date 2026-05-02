# Passive Liveness Detection System

## 📌 Overview

The **Passive Liveness Detection System** is an AI-powered web application designed to detect whether a submitted face image is from a **live human** or a **spoof attempt** (such as a photo, screen replay, or printed image).

Unlike active systems (blink, head movement, etc.), this system performs **passive liveness detection**, meaning:

* No user interaction required
* Works with a single image input
* Fast and seamless experience

---

## 🚀 Features

### 🧠 AI-Based Liveness Detection

* Uses a deep learning model (**ResNet18**) for classification
* Detects real vs fake faces from a single image
* Designed for security-sensitive applications

### 📤 Image Upload Interface

* Clean frontend UI for uploading images
* Displays logs like:

  * Image uploaded
  * Processing started
  * Result returned

### ⚡ Real-Time Processing

* Image sent to backend API
* Backend processes and returns result instantly

### 🌐 Full Stack Deployment

* Frontend deployed on **Vercel**
* Backend deployed on **Render**
* Fully cloud-hosted architecture

---

## 🏗️ System Architecture

```
User (Browser)
     ↓
Frontend (Vite + React on Vercel)
     ↓ API Call
Backend (FastAPI on Render)
     ↓
AI Model (ResNet18)
     ↓
Prediction Response (Live / Spoof)
```

---

## 🧰 Tech Stack

### 🔹 Frontend

* React (with Hooks)
* Vite (build tool)
* JavaScript (JSX)
* Fetch API (for backend communication)
* CSS for styling

### 🔹 Backend

* FastAPI (Python)
* Uvicorn (ASGI server)
* REST API architecture

### 🔹 Machine Learning

* PyTorch
* ResNet18 architecture
* Image preprocessing using:

  * OpenCV / PIL
  * NumPy

### 🔹 Deployment

* Vercel → Frontend hosting
* Render → Backend hosting
* GitHub → Version control

---

## ⚙️ Functional Workflow

### 1. Image Upload

* User selects an image from device
* Image is converted into `FormData`

### 2. API Request

* Frontend sends POST request:

```
POST /analyze
```

* Payload: Image file

### 3. Backend Processing

* Image received by FastAPI
* Preprocessed:

  * Resized
  * Normalized
* Passed into ResNet18 model

### 4. Model Prediction

* Model outputs classification:

  * `Live`
  * `Spoof`

### 5. Response

* Backend sends JSON response:

```json
{
  "result": "Live",
  "confidence": 0.94
}
```

### 6. UI Update

* Frontend displays result
* Logs updated dynamically

---

## 📁 Project Structure

```
passive-liveness-system/
│
├── backend/
│   ├── main.py              # FastAPI server
│   ├── model/               # Trained model files
│   └── utils/               # Preprocessing logic
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main UI logic
│   │   ├── components/      # UI components
│   │   └── assets/
│   ├── index.html
│   └── package.json
│
├── vercel.json              # Deployment config
└── README.md
```

---

## 🔗 API Endpoint

### POST `/analyze`

**Request:**

* Content-Type: `multipart/form-data`
* Body: image file

**Response:**

```json
{
  "result": "Live",
  "confidence": 0.92
}
```

---

## 🌍 Deployment Details

### Frontend (Vercel)

* Hosted using Vite build
* Automatically deploys on Git push

### Backend (Render)

* FastAPI app exposed as REST API
* Public URL used in frontend:

```
https://passive-liveness-detection.onrender.com
```

---

## 🔐 Environment Configuration

Originally used:

```
VITE_API_URL
```

Now simplified:

* API URL is directly defined in frontend code
* Avoids deployment issues with missing environment variables

---

## 🧪 How to Run Locally

### 1. Clone Repository

```bash
git clone https://github.com/your-username/passive-liveness-system.git
cd passive-liveness-system
```

### 2. Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Use Cases

* Face authentication systems
* Banking / KYC verification
* Attendance systems
* Fraud prevention
* Secure login systems

---

## ⚠️ Limitations

* Accuracy depends on training data
* May struggle with:

  * Low lighting
  * Blurry images
  * Extreme angles

---

## 🔮 Future Improvements

* Add video-based liveness detection
* Improve model accuracy with larger datasets
* Add face landmark detection
* Integrate with authentication systems
* Mobile support

---

## 👩‍💻 Author

Developed by **Sahana**

---

## ⭐ Final Note

This project demonstrates:

* Full-stack development
* AI model integration
* Real-world deployment
* Debugging & production readiness

---
