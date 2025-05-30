 Warehouse Management 

This module implements a lightweight, custom warehouse and inventory tracking system for Frappe ERP, designed to manage stock movements, maintain accurate inventory valuation, and provide essential reporting.
Features
1. Custom Stock Entry

Handles three types of stock transactions:

    Receipt: Adds incoming stock to the target warehouse.

    Consume: Removes stock from the source warehouse.

    Transfer: Moves stock from one warehouse to another, updating both.

   
   ![image](https://github.com/user-attachments/assets/8274f6da-a7bb-4dfe-aaec-e6cc9f7ebfce)


   ![image](https://github.com/user-attachments/assets/da237360-b677-4535-9fd1-020c2e9175d4)
   ![image](https://github.com/user-attachments/assets/bec8023c-9811-4506-a453-063286e6085d)



Each transaction generates a corresponding Custom Stock Ledger Entry to maintain quantity and valuation history.
2. Stock Valuation


    Updates valuation dynamically on each incoming or outgoing transaction.
    
   ![image](https://github.com/user-attachments/assets/572f1161-ca37-4992-a48b-070cea573449)

3. Reporting
 Stock Balance Report

    Shows latest stock quantity, rate, and value per item and warehouse.


 
![image](https://github.com/user-attachments/assets/efc50516-d8a0-4b03-8b59-2c22d25c19c7)


 Stock Ledger Report

    Detailed transaction history per item and warehouse.

    
   ![image](https://github.com/user-attachments/assets/2fffaf5f-1b15-406e-ba20-48c3329f85f2)


Testing

Automated tests are provided using Frappe's built-in FrappeTestCase framework. The tests ensure:

    Each transaction type (Receipt, Consume, Transfer) completes successfully.

    Correct behavior of ledger entry generation.
   ![image](https://github.com/user-attachments/assets/7b6e3a7b-0499-4cdb-b9ad-1525d128bbc2)


Tests Include:

    Setup of random test items and warehouses

    Execution and submission of each type of stock entry

    Clean-up after each test to maintain database integrity

