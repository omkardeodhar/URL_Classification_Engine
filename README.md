# URL Classification and Enforcement Framework

## Overview

This project is a Python-based URL classification and traffic enforcement system built for real-time HTTP request interception and control. It leverages **mitmproxy** for HTTP-level traffic interception and a **Random Forest** machine learning model for categorizing and enforcing allow/block decisions on intercepted web traffic.

The framework is designed for high-performance inspection and control of HTTP traffic streams, combining machine learning with manual policy management for flexible security enforcement.

## Features

- **HTTP-Level Interception:** Captures and analyzes HTTP requests in real time using mitmproxy.
- **URL Classification Engine:** Utilizes a Pandas preprocessing pipeline with TF-IDF vectorization feeding a Random Forest model trained on tens of thousands of domains.
- **Real-Time Decision Enforcement:** Predicts request categories and allow/block decisions on the fly.
- **Manual Policy Control:** Supports both automatic ML-based decisions and manual request blocking through policy configuration.
- **Detailed Logging:** Logs URL metadata, model predictions, and action decisions for auditing and analysis.
- **Flask Admin Panel:** Provides a live dashboard for traffic inspection, manual overrides, and dynamic rule updates.

## Technical Stack

- **Python 3**
- **mitmproxy** for HTTP interception
- **Scikit-learn** (Random Forest Classifier)
- **Pandas** and **TF-IDF Vectorization** for data preprocessing
- **Flask** for the administrative interface

## License

> **License Notice:**  
> This project is licensed under a proprietary "All Rights Reserved" license.  
> Unauthorized use, copying, modification, or distribution of any part of this project is strictly prohibited.

---

