# College Predictor

A Flask + PostgreSQL web application that helps students predict eligible colleges based on their entrance exam rank and compare different college branches.

## Features

### College Prediction
- Predict eligible colleges using:
  - Exam
  - Category
  - Quota
  - Rank
- Displays:
  - College Name
  - Branch
  - Closing Rank
  - Average Package
  - Median Package
  - Placement Rate
  - NIRF Ranking
  - Fees
  - Hostel Fees
  - Official Website

### College Comparison
- Compare two college branches side-by-side.
- Compare:
  - Average Package
  - Median Package
  - Placement Rate
  - Fees
  - NIRF Rank

### College Details
- View detailed information about a college and branch.

---

## Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy

### Database
- PostgreSQL

### Frontend
- HTML
- Jinja2 Templates

### Version Control
- Git
- GitHub

---

## Database Design

Main entities:

- College
- Branch
- Exam
- Category
- Quota
- Seat Type
- Counselling Round
- Cutoff

Relationships:

- One College → Many Branches
- One Branch → Many Cutoffs
- One Exam → Many Cutoffs
- One Category → Many Cutoffs
- One Quota → Many Cutoffs
- One Seat Type → Many Cutoffs
- One Counselling Round → Many Cutoffs

---

## Sample Data

Current MVP contains:

- IIT Bombay
- IIT Delhi
- IIT Madras
- IIT Kanpur
- IIT Kharagpur

Branches:

- Computer Science and Engineering
- Electrical Engineering
- Mechanical Engineering

Exam:

- JEE Advanced

Category:

- OPEN

Quota:

- AI (All India)

Year:

- 2025

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Hoofeddam/college-predictor.git
cd college-predictor
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Future Improvements

- AI College Recommendation Chatbot
- More Colleges
- More Exams (JEE Main, COMEDK, KCET, MET)
- Better UI using Bootstrap
- User Accounts
- College Bookmarking
- College Recommendation Engine
- Deployment on Cloud

---

## Author

Reyansh Priyam