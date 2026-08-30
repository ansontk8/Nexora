NEXORA

NEXORA is an AI-powered hybrid e-commerce marketplace developed using Django that supports both **digital and physical products** on a unified platform.
The system provides separate workflows for digital downloads and physical product delivery, with dedicated features for customers, vendors, and administrators. It also integrates AI and Machine Learning features for product recommendations, description generation, review analysis, fraud detection, and sales prediction.

## Features

Customer
- Registration and login
- Product browsing and search
- AI-powered recommendations
- Digital and physical product purchases
- Secure digital downloads
- Physical order tracking
- Reviews and ratings
- AI chatbot support

Vendor
- Vendor registration and verification
- Product management
- Digital file uploads
- Stock management
- Low-stock alerts
- AI product description generation
- Sales and revenue dashboard
- Seller performance score
- Trust badges

 Admin
- Vendor management and approval
- Product moderation
- Category management
- Order and transaction monitoring
- Review and fraud monitoring
- Vendor performance management
- Platform analytics

AI & ML Features

- **AI Product Description Generator** – Generates product titles, descriptions, highlights, and usage suggestions.
- **Smart Recommendations** – Provides personalized product suggestions based on user interactions.
- **AI Chatbot** – Provides order, download, refund, and platform assistance.
- **Sentiment Analysis** – Analyzes customer reviews and identifies sentiment.
- **Fake Review Detection** – Classifies reviews as genuine, suspicious, or fake.
- **Sales Prediction** – Predicts future sales using historical sales and product trends.

Stock Management

- Stock quantity tracking
- Low-stock alerts
- Stock history
- Automatic out-of-stock handling

Technologies Used

**Frontend**
- HTML5
- CSS3
- JavaScript
- Django Templates

**Backend**
- Python
- Django

**Database**
- SQLite3

Project Structure
NEXORA/
│
├── accounts/
├── ai_engine/
├── core/
├── dashboard/
├── ml_engine/
├── nexora/
├── orders/
├── products/
├── reviews/
├── static/
├── templates/
├── media/
│
├── db.sqlite3
├── manage.py
└── .env

How to Run
Prerequisites
•	Python 3.x 
•	Django 
•	Git 

Installation

git clone <repository-url>
cd nexora
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Open:
http://127.0.0.1:8000/

Project Objective

The objective of NEXORA is to create a secure, intelligent, and scalable hybrid e-commerce marketplace that combines digital and physical product commerce with AI-powered automation, personalization, analytics, and trust mechanisms.

Future Enhancements
•	Online payment integration 
•	Mobile application 
•	Advanced AI recommendations 
•	Improved sales forecasting 
•	Multilingual support 
•	Cloud deployment 
•	Enhanced fraud detection 

License
This project was developed for educational and academic purposes.

Developer
Anson T Kuruvilla 
