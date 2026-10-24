create database european_bank_db;
use european_bank_db;

show tables;

DESCRIBE `european bank`;

SELECT *
FROM `european_bank_db`.`european bank`
LIMIT 10;

SELECT COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`;

SELECT COUNT(*) AS churned_customers
FROM `european_bank_db`.`european bank`
WHERE Exited = 1;


SELECT COUNT(*) AS retained_customers
FROM `european_bank_db`.`european bank`
WHERE Exited = 0;

SELECT
    Geography,
    COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`
GROUP BY Geography
ORDER BY total_customers DESC;

SELECT
    ROUND(
        SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    ) AS churn_rate_percentage
FROM `european_bank_db`.`european bank`;

SELECT
    CustomerId,
    Surname,
    Geography,
    Balance
FROM `european_bank_db`.`european bank`
ORDER BY Balance DESC
LIMIT 10;

SELECT
    Gender,
    COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`
GROUP BY Gender;

SELECT
    ROUND(AVG(Balance), 2) AS average_balance,
    MAX(Balance) AS highest_balance,
    MIN(Balance) AS lowest_balance
FROM `european_bank_db`.`european bank`;

SELECT
    CustomerId,
    Surname,
    CreditScore,
    Geography
FROM `european_bank_db`.`european bank`
WHERE CreditScore < 500
ORDER BY CreditScore ASC;

SELECT
    CASE
        WHEN Age < 30 THEN 'Below 30'
        WHEN Age BETWEEN 30 AND 45 THEN '30-45'
        WHEN Age BETWEEN 46 AND 60 THEN '46-60'
        ELSE 'Above 60'
    END AS age_group,
    COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`
GROUP BY age_group
ORDER BY total_customers DESC;

SELECT
    Gender,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_percentage
FROM `european_bank_db`.`european bank`
GROUP BY Gender;

SELECT
    IsActiveMember,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers
FROM `european_bank_db`.`european bank`
GROUP BY IsActiveMember;

SELECT
    NumOfProducts,
    COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`
GROUP BY NumOfProducts
ORDER BY NumOfProducts;

SELECT
    Geography,
    ROUND(AVG(EstimatedSalary), 2) AS average_salary
FROM `european_bank_db`.`european bank`
GROUP BY Geography
ORDER BY average_salary DESC;

SELECT
    COUNT(*) AS zero_balance_customers
FROM `european_bank_db`.`european bank`
WHERE Balance = 0;

SELECT
    NumOfProducts,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_percentage
FROM `european_bank_db`.`european bank`
GROUP BY NumOfProducts
ORDER BY churn_rate_percentage DESC;

SELECT
    Geography,
    COUNT(*) AS total_customers
FROM `european_bank_db`.`european bank`
GROUP BY Geography
HAVING COUNT(*) > 1000
ORDER BY total_customers DESC;

SELECT
    CustomerId,
    Surname,
    Geography,
    EstimatedSalary
FROM `european_bank_db`.`european bank`
WHERE EstimatedSalary > (
    SELECT AVG(EstimatedSalary)
    FROM `european_bank_db`.`european bank`
)
ORDER BY EstimatedSalary DESC
LIMIT 20;

SELECT
    CASE
        WHEN Age < 30 THEN 'Below 30'
        WHEN Age BETWEEN 30 AND 45 THEN '30-45'
        WHEN Age BETWEEN 46 AND 60 THEN '46-60'
        ELSE 'Above 60'
    END AS age_group,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_pct
FROM `european_bank_db`.`european bank`
GROUP BY age_group
ORDER BY churn_rate_pct DESC;

SELECT
    CustomerId,
    Surname,
    Balance,
    DENSE_RANK() OVER (
        ORDER BY Balance DESC
    ) AS balance_rank
FROM `european_bank_db`.`european bank`
LIMIT 10;

SELECT
    Geography,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    SUM(CASE WHEN Exited = 0 THEN 1 ELSE 0 END)
        AS retained_customers
FROM `european_bank_db`.`european bank`
GROUP BY Geography;

SELECT
    CustomerId,
    Surname,
    NumOfProducts,
    Balance,
    Exited
FROM `european_bank_db`.`european bank`
WHERE NumOfProducts = 1
ORDER BY Balance DESC
LIMIT 20;

SELECT
    CustomerId,
    Surname,
    Geography,
    Balance,
    IsActiveMember
FROM `european_bank_db`.`european bank`
WHERE IsActiveMember = 0
  AND Balance > 0
ORDER BY Balance DESC
LIMIT 20;

SELECT
    Geography,
    ROUND(SUM(Balance), 2) AS total_balance,
    ROUND(AVG(Balance), 2) AS average_balance
FROM `european_bank_db`.`european bank`
GROUP BY Geography
ORDER BY total_balance DESC;

SELECT
    Geography,
    Gender,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(AVG(Age), 1) AS average_age,
    ROUND(AVG(Balance), 2) AS average_balance
FROM `european_bank_db`.`european bank`
GROUP BY Geography, Gender
ORDER BY Geography, Gender;

SELECT
    Geography,
    ROUND(SUM(Balance), 2) AS total_balance
FROM `european_bank_db`.`european bank`
GROUP BY Geography
ORDER BY total_balance DESC
LIMIT 5;

SELECT
    Geography,
    ROUND(AVG(CreditScore), 2) AS average_credit_score
FROM `european_bank_db`.`european bank`
GROUP BY Geography
ORDER BY average_credit_score DESC;

SELECT
    CustomerId,
    Surname,
    Geography,
    Balance,
    Exited
FROM `european_bank_db`.`european bank`
WHERE Balance > 100000
  AND Exited = 1
ORDER BY Balance DESC;

SELECT
    IsActiveMember,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_pct
FROM `european_bank_db`.`european bank`
GROUP BY IsActiveMember;

SELECT
    CustomerId,
    Surname,
    NumOfProducts,
    Balance,
    Exited
FROM `european_bank_db`.`european bank`
WHERE NumOfProducts >= 2
ORDER BY NumOfProducts DESC, Balance DESC
LIMIT 20;

SELECT
    Tenure,
    COUNT(*) AS total_customers,
    ROUND(AVG(Balance), 2) AS average_balance
FROM `european_bank_db`.`european bank`
GROUP BY Tenure
ORDER BY Tenure;

SELECT
    CustomerId,
    Surname,
    Geography,
    EstimatedSalary
FROM `european_bank_db`.`european bank`
ORDER BY EstimatedSalary DESC
LIMIT 10;

SELECT
    CASE
        WHEN Exited = 1 THEN 'Churned'
        ELSE 'Retained'
    END AS customer_status,
    COUNT(*) AS total_customers,
    ROUND(AVG(Balance), 2) AS average_balance,
    ROUND(AVG(EstimatedSalary), 2) AS average_salary
FROM `european_bank_db`.`european bank`
GROUP BY Exited;

SELECT
    Geography,
    COUNT(*) AS total_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_pct
FROM `european_bank_db`.`european bank`
GROUP BY Geography
HAVING
    100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
    / COUNT(*) > 20;
    
    SELECT
    COUNT(*) AS total_customers,
    ROUND(AVG(Age), 2) AS average_age,
    ROUND(AVG(CreditScore), 2) AS average_credit_score,
    ROUND(SUM(Balance), 2) AS total_balance,
    ROUND(AVG(Balance), 2) AS average_balance,
    ROUND(AVG(EstimatedSalary), 2) AS average_salary,
    SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Exited = 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS churn_rate_pct
FROM `european_bank_db`.`european bank`;

SELECT * FROM european_bank_db.`european bank`;