# FastAPI URL Shortener with GitHub Authentication

## 📌 Overview
This project is a **FastAPI-based URL shortener** with **GitHub OAuth authentication**. Users can **log in with GitHub, shorten URLs, and manage their links**. The application is containerized using **Docker** and deployed with **GitHub Actions CI/CD**.

---

## 📂 Directory Structure
```
project/
│── app/
│   │── main.py  # FastAPI Application Entry
│   │── database.py  # Database Connection & Models
│   │── routes.py  # API Endpoints
│   │── auth.py  # GitHub OAuth Authentication
│   │── templates/
│   │   └── index.html  # Web UI
│   └── static/
│       ├── style.css  # UI Styling
│       └── script.js  # Frontend Interactions
│── tests/
│   └── test_main.py  # Unit Tests
│── Dockerfile  # Container Setup
│── docker-compose.yml  # Multi-Container Setup (App + DB)
│── requirements.txt  # Dependencies
│── .github/workflows/ci-cd.yml  # GitHub Actions CI/CD
│── README.md  # Documentation
│── .env  # Environment Variables (GitHub OAuth & DB)
```

---

## 🔧 Setup Instructions

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/your-username/fastapi-url-shortener.git
cd fastapi-url-shortener
```

### 2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Set Up Environment Variables**
Create a `.env` file with your **GitHub OAuth Credentials** and **Database URL**:
```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
DATABASE_URL=postgresql://user:password@localhost/urlshortener
```

### 4️⃣ **Run the Application Locally**
```bash
uvicorn app.main:app --reload
```
Open `http://localhost:8000` in your browser. 🚀

---

## 🚀 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/` | Home Page (Login & Shorten URL UI) |
| **POST** | `/shorten/` | Shorten a URL |
| **GET** | `/{short_url}` | Redirect to Original URL |
| **GET** | `/auth/login` | GitHub OAuth Login |
| **GET** | `/auth/callback` | OAuth Callback |
| **GET** | `/logout` | Logout User |

---

## 🐳 Docker Deployment

### **Build & Run Locally**
```bash
docker-compose up --build
```

### **Push to Docker Hub**
```bash
docker build -t your-dockerhub-username/fastapi-url-shortener .
docker login
docker push your-dockerhub-username/fastapi-url-shortener
```

### **Run Container from Docker Hub**
```bash
docker run -d --name url-shortener -p 8000:8000 your-dockerhub-username/fastapi-url-shortener
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)
This project includes **GitHub Actions** for automatic deployment.

### **.github/workflows/ci-cd.yml**
- **Runs tests using pytest**
- **Builds Docker Image**
- **Pushes to Docker Hub**
- **Deploys to Server**

### **How to Set Up Secrets in GitHub**
1. Go to **GitHub Repository > Settings > Secrets and variables**
2. Add the following secrets:
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_PASSWORD`

---

## 🔑 Authentication & OAuth Flow
1. User clicks **"Login with GitHub"**
2. Redirected to GitHub OAuth login
3. After login, **GitHub sends an access token**
4. User details are **stored in the database**
5. **Session is created**, and user can shorten URLs
6. Logout clears the session

---

## ✅ Running Tests
```bash
pytest tests --disable-warnings --verbose
```

---

## 🚀 Future Enhancements
- ✅ **Store shortened URLs in DB per user**
- ✅ **Custom alias for URLs**
- ✅ **Deploy to AWS/GCP with Kubernetes**

---

### **📌 Authors & Contributors**
- **Your Name** - [GitHub](https://github.com/your-username)

---

Now you're ready to **deploy & test** your FastAPI URL Shortener! 🚀🔥

