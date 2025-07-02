# CHECK
Comprehensive Handwritten Exam Checking Kit with TrOCR and FAST
Backend repo for the C.H.E.C.K system without the TrOCR and FAST model.

Warning: This repository does not contain any of the stated moodel as they are downloaded seperately.

How to run: (when the model is already downloaded)
1.  **Activate Virtual Environment:**
    ```
    .localenv\Scripts\activate
    ```
3.  **Enable Execution Policy (if needed):** If the terminal does not activate the virtual environment, you may need to set the execution policy (for PowerShell):
    ```
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
4.  **Start the Application:** To run the backend server (with auto-reload for development):
    ```
    uvicorn app:app --reload
    ```
