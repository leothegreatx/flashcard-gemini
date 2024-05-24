**Gemini Flashcard**

Gemini Flashcard is a full-stack project built using React.js and FastAPI. The project is designed to take a video link, transcribe the video, 
and store the transcription in a document. The document is then split into smaller chunks and used to generate flashcards using Vertex AI to capture and define concepts. 
React.js is used to access these features and provide a simple, user-friendly UI where users can generate and delete flashcards.

**Getting Started**

To get started with the Gemini Flashcard project, follow these steps:

**1. Clone the repository:**

```python
git clone <repository_url>
```
**2. navigate to the repository directory in your terminal. Then, execute the following command to swiftly install the required libraries and dependencies:**

```python
pip3 install -r requirements.txt
```
**3. Set up Vertex AI for your project:**
3.1. Log into the Google Cloud Console.

3.2. Create a new project.

3.3. Enable the Vertex AI API.

3.4. Create a service account.

3.5. Generate and download the key file for the service account.

3.6. Assign the necessary permissions to the service account, such as Owner, Service Account Token Creator, and Vertex AI Administrator.

**4. Authenticate the Google Cloud SDK with your Google account:**
```python
gcloud auth login
```
**4. Set the GOOGLE_APPLICATION_CREDENTIALS environment variable:**
```python
export GOOGLE_APPLICATION_CREDENTIALS="/Path/To/KeyFile.json"
```
**5. Start the FastAPI server:**
```python
uvicorn main:app --reload
```
**6. Start the React app:**
```python
npm run dev
```
With these steps, you should have the Gemini Flashcard project up and running. You can now use the UI to generate and manage your flashcards.
