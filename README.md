# NEXORA

NEXORA is an AI-powered E-Commerce and Enterprise Management Platform built with Django, featuring intelligent dynamic pricing, AI product description generation, customer review sentiment classification, and real-time dashboard analytics.

---

## 🚀 Key Features

- **AI Machine Learning Engine (`ml_engine`)**:
  - **Dynamic Pricing Optimizer**: Random Forest Regressor for market-responsive price recommendation.
  - **Smart Product Description Generator**: Generates optimized product titles and descriptions using generative AI (Gemini, xAI, Groq).
  - **Review Classification**: Sentiment analysis and dataset classifier.
- **E-Commerce Suite**:
  - **Product Management**: Full cataloging with categories, stock tracking, and variant handling.
  - **Order & Cart Workflow**: Real-time cart calculations, checkout flow, and shipping integration.
  - **Customer & Bakery/Vendor Portals**: User profiles, custom quote requests, and order histories.
- **Analytics & Dashboard**:
  - Interactive merchant dashboard visualizing sales, revenue, active products, and customer feedback.

---

## 🛠️ Technology Stack

- **Backend Framework**: Django 6.0 (Python 3.13)
- **Machine Learning / AI**: Scikit-Learn, Pandas, NumPy, Google Generative AI (Gemini), Groq API, xAI API
- **Database**: SQLite3 (Development)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS / Custom Templates

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.10+
- `pip` package manager

### 2. Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ansontk8/Nexora.git
   cd Nexora
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

5. **Database Migration**:
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the web app at `http://127.0.0.1:8000/`.

---

## 🧠 ML Engine Tools

To train the dynamic pricing optimizer model:
```bash
python ml_engine/train_pricing_optimizer.py
```

To run ML feature diagnostics & tests:
```bash
python ml_engine/test_ml_features.py
```

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
