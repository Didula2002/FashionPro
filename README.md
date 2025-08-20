# 🧥 FashionPro

FashionPro is an **AI and AR-based fashion web application** that allows users to get outfit recommendations through a smart chatbot, try on fashion accessories like glasses and hats using **2D and 3D virtual try-on** features, and purchase products through a complete **e-commerce system**.

---

## ✨ Key Features

- 🤖 AI-powered chatbot for personalized outfit suggestions  
- 🖼️ Image-based outfit recommendation using ResNet50 and KNN  
- 📷 2D webcam-based virtual try-on system  
- 🕶️ 3D AR try-on using Snapchat Lens Studio  
- 🛒 Full-stack e-commerce platform with cart, checkout, product listings, and admin dashboard  

---

## ⚙️ Installation Guide

1. Create a `.env` file in the `FashionPro Ecommerce/server` folder using this content:

```env
MONGODB_URI=" "
RESEND_API=" "
FRONTEND_URL="http://localhost:5173"
SECRET_KEY_ACCESS_TOKEN=" "
SECRET_KEY_REFRESH_TOKEN=" "
CLODINARY_CLOUD_NAME=" "
CLODINARY_API_KEY=" "
CLODINARY_API_SECRET_KEY=" "
VITE_API_URL=http://localhost:8080
```

---

## 🚀 Run Instructions

Please follow this exact order to run the project correctly:

### Step 1: Start Chatbot Frontend (`frontend` folder)

```bash
cd frontend
npm install
npx vite
```

### Step 2: Start Image-Based Recommendation Backend (`backend` folder)

```bash
cd backend
pip install -r requirements.txt
flask run
```

### Step 3: Start Chatbot Backend (`chatbot` folder)

```bash
cd chatbot
python -m venv venv
venv\Scripts\activate   # For Windows
source venv/bin/activate   # For macOS/Linux
pip install -r requirements.txt
python app.py
```

### Step 4: Start E-commerce Frontend (`FashionPro Ecommerce/client`)

```bash
cd FashionPro Ecommerce/client
npm install
npx vite
```

### Step 5: Start E-commerce Backend (`FashionPro Ecommerce/server`)

```bash
cd FashionPro Ecommerce/server
npm install
npm start
```

---

## 🌐 Access URLs

- Chatbot Frontend: http://localhost:5173  
- E-commerce Frontend: http://localhost:5174 (if configured separately)  
- Chatbot APIs:  
  - Image-based: http://localhost:5000  
  - Text-based: http://localhost:5001  

---

## ✅ Technologies Used

- 💻 Frontend: React.js, Tailwind CSS  
- 🧠 Backend: Node.js, Express, Flask  
- 🧬 AI: PyTorch, TensorFlow, ResNet50, KNN  
- 💾 Database: MongoDB  
- 🎯 AR: Snapchat Lens Studio (3D try-on)  
- ☁️ Hosting & APIs: Cloudinary, Resend API