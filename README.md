Conduit RealWorld Automation Framework 🚀
This repository features a robust, scalable automation framework for the Conduit (RealWorld) application. Built with a focus on modern software testing patterns and AI-augmented development (Vibe Coding), this project demonstrates how to achieve high test coverage and reliability with efficiency.

🛠 Tech Stack
Language: Python 3.x

Framework: Pytest

Tool: Selenium WebDriver

Pattern: Page Object Model (POM)

Principles: DRY (Don't Repeat Yourself), Clean Code, Type Hinting

✨ Key Features
Hybrid Testing Strategy: Leveraging API calls for fast setup (Arrange) and Selenium for end-to-end user flow validation (Act/Assert).

Vibe Coding Workflow: Developed using advanced AI-driven methodologies to accelerate framework scaffolding and focus on complex logic and edge cases.

Security Conscious: Includes test scenarios for basic vulnerability checks like XSS and SQL Injection.

Robust Synchronization: Custom wait strategies to handle dynamic elements and asynchronous XHR requests.

Scalable POM: Decoupled page logic from test scripts for easy maintenance and readability.

📁 Project Structure
Plaintext
├── pages/              # Page Object classes (UI elements & actions)
├── tests/              # Test suites (UI and API integration)
├── utils/              # Helper functions and configurations
├── conftest.py         # Pytest fixtures and global setup
└── requirements.txt    # Project dependencies
🚀 Getting Started
Clone the repo: git clone https://github.com/StasLisson/Conduit_Automation.git

Install dependencies: pip install -r requirements.txt

Run tests: pytest tests/
