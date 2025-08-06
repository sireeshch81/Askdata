# Product Recommendation Service - MongoDB Integration

🎯 **Successfully processes 1,900+ members with dual-format output!**

This service generates product recommendations for members and saves them in dual formats:
- **JSON files** (original format) for backward compatibility
- **MongoDB** (team's API format) for frontend consumption

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- ~~Docker and Docker Compose~~
- MongoDB, OLTP DB, and DW DB running

### 1. Environment Setup
```bash
First, starting in the recommendation service directory, create a virtual environment and install the dependencies:
* python -m venv rec-env
* . rec-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start databases (from project root, should already be running, but if not)
* docker-compose up -d mongodb oltp-db dw-db

# Generate recommendations for specific member
python src/main.py --member-id 1

# Generate recommendations for ALL active members (~1,900 members)
python src/main.py --source oltp --batch-size 100
