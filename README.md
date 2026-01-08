<div align="center"> 

## UK Road Traffic Congestin predictor

It is a secure end-to-end traffic congestion system system which has been built using streamlit, PostgreSQL, and machine learning model. The application supports real-time traffic forecasting, trained model upload, user authnetication, and CSV batch predictions

**Features ▪︎ System architecture ▪︎ Database Requirments ▪︎ Model Requirments ▪︎ Database Specifications ▪︎ Deployment ▪︎ Local Deployment instructions**  

</div> 

## Features

- 🔐 User Authentication: Login & Registration

- 📦 Upload trained Machine Learning models (.pkl)

- 📊 Upload and validate CSV traffic datasets

- 🚦 Junction-level traffic congestion prediction

- 📈 Batch prediction for entire datasets

- 🗄️ PostgreSQL database hosted on Neon

- ☁️ Deployed on Streamlit Cloud

## System architecture

| Component  | Technology        |
| ---------- | ----------------- |
| Frontend   | Streamlit         |
| Backend    | Python            |
| ML         | scikit-learn      |
| Database   | PostgreSQL (Neon) |
| Auth       | bcrypt            |
| Deployment | Streamlit Cloud   |

## Database Requirments

| Column Name  | Description        |
| ---------- | ----------------- |
| Junction   | Road Junction Identifier         |
| Vehicles    | Number of Vehicles            |
| Date and Time         | Timestamp (YYYY-MM-DD HH:MM:SS)      |

## Model Requirements  
- Must be a trained scikit-learn model

- Saved using joblib.dump()

- Must support .predict()

- Expected input features:

      Vehicles

      Hour

      DayOfWeek

      Month

      Weekend

      RushHour
## Files Structure

(To Be Added)

## Database Specifications

The designed system leverages serveless PostGreSQL database hosted on Neon

## Deployment

- Frontend: Streamlit Cloud

- Database: Neon PostgreSQL

- CI/CD: GitHub → Streamlit Cloud

## Local deployment instructions

(To Be added)

## System Security

- Passwords hashed with bcrypt

- Database access secured via SSL

- Secrets managed using Streamlit Secrets

## System Front-end
**Login Page**
<img width="1825" height="956" alt="image" src="https://github.com/user-attachments/assets/06c3277f-9146-4c38-9024-6ce2b70abe31" />

**Register Page**
<img width="1761" height="1001" alt="image" src="https://github.com/user-attachments/assets/e23e39be-908f-40f6-b8d6-10d94a704286" />

**Dashboard page**
<img width="1817" height="965" alt="image" src="https://github.com/user-attachments/assets/3fd70457-a8e3-40f2-b093-894cc52716f0" />

**Prediction Done**
<img width="1640" height="972" alt="image" src="https://github.com/user-attachments/assets/5af43272-2d4e-44a7-befe-7d365eb76c51" />

## Author

OMAR KHALIFA

## Project Link

https://uktrafficpredictor-ufl4vvlq9cro2jhzgmy8fo.streamlit.app

## License 

The project is for education purposes only 






