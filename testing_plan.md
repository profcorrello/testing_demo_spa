## 🏗️ Project Test Plan: Word-to-HTML Converter

### 1. Test Objectives

The goal is to verify the integrity of the document conversion pipeline across three distinct interfaces: the Command Line (CLI), the Application Programming Interface (API), and the Single Page Application (UI).

### 2. Testing Levels & Scope

| Level | Focus | Tool | Success Criteria |
| --- | --- | --- | --- |
| **Unit Testing** | Conversion Logic | `pytest` | `.docx` structures (bold, lists, headers) map correctly to HTML tags. |
| **Integration Testing** | API Reliability | `httpx` / `Pytest` | Multipart file uploads are accepted; JSON responses are schema-valid. |
| **System/E2E Testing** | User Experience | **Playwright** | The end-user can upload, convert, and view the result without console errors. |

---

### 3. Test Scenarios (The "What to Test")

#### **A. The Logic Layer (CLI)**

* **Happy Path:** Convert a standard 3-page `.docx` with nested lists.
* **Edge Case:** Convert an empty `.docx` file.
* **Error Handling:** Attempt to "convert" a `.pdf` or a corrupted file (should raise a specific `ConversionError`).

#### **B. The Interface Layer (API)**

* **Protocol Check:** Ensure the endpoint only accepts `POST` requests.
* **Payload Limits:** Test the behavior when a file exceeds a size limit (e.g., 10MB).
* **Concurrency:** Ensure the server can handle multiple simultaneous conversion requests.

#### **C. The Presentation Layer (SPA)**

* **Visual Feedback:** Verify a "Loading..." spinner appears during the `POST` request.
* **Mocked Resilience:** Use Playwright to intercept the network and force a `504 Gateway Timeout` to ensure the UI doesn't just "freeze."
* **Cross-Browser:** Run the Playwright suite on **Chromium**, **Firefox**, and **WebKit**.

---

### 4. Traceability Matrix (Simplified)

To show your professor you've thought about "Requirement Traceability":

* **Requirement R1:** Must support Bold/Italic formatting.
* *Verified by:* `test_formatting.py` (Unit).


* **Requirement R2:** Users must be able to use the tool via a browser.
* *Verified by:* `test_spa_upload.py` (Playwright E2E).



---

### 5. Automated Regression Strategy

We will utilize a **CI/CD Pipeline** (e.g., GitHub Actions) where:

1. Unit tests run on every `push`.
2. Integration tests run on `pull_request` to the main branch.
3. Playwright E2E tests run on a staging environment before "deployment."

