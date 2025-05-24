# Marine-Debris-Data-Collection-Web-App

- Built a **Flask web application** to log marine debris observations
- User input:
  - Image upload
  - Description
  - GPS coordinates (latitude, longitude)
- The app:
  - Uses Google Gemini API to classify debris
  - Uses Nominatim API to convert GPS → country name

### LLM Prompting Strategy

- Prompt 1 asks Gemini:
  > Is this marine debris? If not, return Not debris  
- If it is marine debris:
  - Classify into one of the following categories:  
    Plastic, Metal, Glass, Rubber, Processed Wood, Fabric, Other
  - If it doesn't fit any, LLM returns Other
- Strict response formatting is enforced so only one keyword (category) is returned

### Valid Submissions
- Stored in local folder: `static/uploads/`
- Logged into SQLite database: `debris.db`
- Shown in an HTML table on the homepage

### Invalid Submissions
- Rejected if:
  - Not an image (`.jpg`, `.png`, etc.)
  - Not marine debris (e.g., a ship, fish, or person)
  - LLM returns an unrecognized category

---

## How to Run the App Locally

bash
conda activate info8000sp25
cd part2
python app.py

## Notes:
- The application has two routes:
1. /submit: handles POST requests to validate and log debris entries
2. / (root): serves the submission form and displays all logged debris

