# NERNA (NER Notebook Annotation)

Follow the official repository: [NER-Notebook-Annotation - GitHub](https://github.com/danttis/NER-Notebook-Annotation/) 	


**NERNA** is a lightweight package designed for **Named Entity Recognition (NER) annotation** directly within Python notebooks.

Originally intended as a Streamlit-based interface, it has been reworked to run natively inside notebook environments (such as Jupyter, Google Colab, Databricks, etc.). This makes it easier to use without requiring deployment of web applications or cloud server contracts.

## Key Features

* ✅ Lightweight, interactive JavaScript interface embedded in notebooks
* ✅ Compatible with local notebooks and cloud platforms (e.g., Colab, Databricks)
* ✅ No need for external servers or deployments
* ⚠️ Annotations are made using **JavaScript**, so **they cannot be accessed directly as Python variables**. However, the input to the tool must be a **Python list of strings**.

---

## Usage Example

```python
from nerna import NERAnnotator

# List of texts to annotate
texts = [
    'Brazil won the 2002 World Cup.',
    'The planet’s drinking water is running out.'
]

# Initialize annotation
annotator = NERAnnotator(texts)

# Render the interactive annotation interface
annotator.render()
```
![NERNA Screenshot](https://raw.githubusercontent.com/danttis/NER-Notebook-Annotation/refs/heads/main/docs/img/image.png)

---

## Notes

4. **Retrieve annotations:**

   There are two ways to retrieve the annotated data back into Python:

   **Option A: Export to Python Variable (Recommended for Colab/Jupyter)**
   
   Pass the name of your variable to the `render` method:
   ```python
   # 1. Initialize
   annotator = NERAnnotator(texts)
   
   # 2. Render with variable name
   annotator.render(variable_name="annotator")
   ```
   *   In the UI, click the **"🐍 Export to Python"** button.
   *   Access the data in Python:
   ```python
   # After clicking the button:
   print(annotator.annotations)
   ```

   **Option B: Load from JSON (Fallback)**
   
   *   Click **"📥 Download All"** in the UI to save a `.json` file.
   *   Load it in Python:
   ```python
   from nerna import load_annotations_from_json
   
   data = load_annotations_from_json("path/to/all_annotations_....json")
   print(data)
   ```

* Annotated results are not automatically returned to Python unless you use the "Export to Python" button.
* Ideal for manual review, small-scale labeling tasks, or quick experimentation in NLP workflows.

