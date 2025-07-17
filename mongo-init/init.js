db = db.getSiblingDB('askdata_db');
db.questions.insertMany([
  { question: "What is customer churn rate?", created_at: new Date() },
  { question: "Show top 5 performing branches", created_at: new Date() }
]);

