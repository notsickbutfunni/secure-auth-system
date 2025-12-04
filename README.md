# secure-auth-system


### How to run

1. Create virtual environment

    ```
    python -m venv venv
    ```

2. Activate

    Windows:

    ```
    .venv\Scripts\activate
    ```


    Mac/Linux:
    ```
    source venv/bin/activate
    ```

3. Install dependencies
    ```
    pip install -r requirements.txt 
    ```

4. Run FastAPI server
    ```
    uvicorn main:app --reload
    ```