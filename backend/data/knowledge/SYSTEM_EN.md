# EDUMENTOR AI - SYSTEM OPERATING MANUAL & RAG KNOWLEDGE BASE
*(Static Operating System Manual & Learner Guide for EduMentor AI)*

---

## 1. SYSTEM OVERVIEW & ENVIRONMENT CONVENTIONS

### 1.1. Platform Introduction
EduMentor AI is an intelligent online learning ecosystem and AI-powered tutor designed for learners in computer science, software engineering, and data science. The platform seamlessly bridges high-quality Massive Open Online Courses (MOOCs) from leading global institutions (Coursera, edX, etc.) with an internal knowledge graph comprising **5,893 skills**, **213 skill relationships (prerequisites, extensions, related)**, and **4,509 curated courses**.

### 1.2. RAG Boundaries & Scope of Service
- **No Video Hosting:** EduMentor AI functions as an intelligent orientation guide and academic companion. It does not directly host or stream third-party course lecture videos. When a learner clicks "Join Course" ("Tham gia học ↗"), the system redirects them directly to the provider's official course page.
- **No Direct Payments or Automated Enrollments:** Course enrollment fees, financial aid, certificate issuances, and grading on external MOOC platforms are independently managed by the respective third-party providers.
- **Internal Course Tracking Lifecycle:** The platform tracks progress internally across 4 states: `Bookmarked (Đã lưu)` $\rightarrow$ `Ongoing (Đang học)` $\rightarrow$ `Completed (Hoàn thành)` (recognized upon passing the comprehensive quiz $\ge 60\%$) $\rightarrow$ `Abandoned (Đã bỏ)`.

### 1.3. Environment Conventions & Global Navigation
- **Frontend Local URL:** `http://localhost:5173`
- **Backend API Docs (FastAPI Swagger UI):** `http://localhost:8000/docs`
- **Global Header Navigation:**
  - **Courses (`/courses`):** Search, browse, and filter the catalog of 4,509 courses.
  - **Learning Path (`/ai-learning-path`):** Access personal learning path Roadmaps on interactive canvas graphs.
  - **My Courses (`/my-courses`):** Manage ongoing, bookmarked, completed, and abandoned courses.
  - **Quiz Practice (`/ai-quiz-practice`):** 20-question skill-based standardized review quizzes.
  - **AI Tutor (`/ai-tutor`):** Multi-turn conversational mentor for code debugging, conceptual explanation, and interactive inline drills.
  - **Contact (`/contact`):** System feedback and technical support.
  - **Profile / Avatar Menu (`/profile`):** Personal dashboard, learning statistics, theme toggle (Dark/Light), and password management.

---

## 2. USER ACCOUNT & PROFILE MANAGEMENT SUBSYSTEM

### 2.1. Registration Process (`/register`)
- **Direct Static URL:** `http://localhost:5173/register`
- **Required Form Fields:**
  1. *Full Name:* User's display name (e.g., Nguyen Van A).
  2. *Email Address:* Unique account identifier, used for notifications, authentication, and password recovery.
  3. *Password:* Must satisfy all 5 security criteria:
     - Minimum 8 characters in length.
     - At least 1 uppercase letter (`A-Z`).
     - At least 1 lowercase letter (`a-z`).
     - At least 1 numerical digit (`0-9`).
     - At least 1 special character (`!@#$%^&*()_+...`).
  4. *Confirm Password:* Must match the password exactly.
- **Action:** Click **"Register →" ("Đăng ký →")**. The account is created with the default role of **Student (Học viên)**.

### 2.2. Login Process (`/login`)
- **Direct Static URL:** `http://localhost:5173/login`
- **Steps:**
  1. Enter registered email address.
  2. Enter password.
  3. Click **"Login →" ("Đăng nhập →")**.
  4. The backend issues two secure tokens: **Access Token** (JWT, valid for 30 minutes) and **Refresh Token** (supports automated Refresh Token Rotation to sustain the session).

### 2.3. Password Recovery Process (`/forgot-password`)
- **Direct Static URL:** `http://localhost:5173/forgot-password`
- **Steps:**
  1. Click the **"Forgot password?" ("Quên mật khẩu?")** link on the login screen.
  2. Enter the registered email address.
  3. Click **"Send Request →" ("Gửi yêu cầu →")**.
  4. The UI transitions to the **"Check Your Email" ("Kiểm tra email của bạn")** screen (`/check-email-confirmation`):
     - Check inbox and spam folders.
     - *Security notice:* The reset link is **single-use** and has a short expiration window of **15 to 30 minutes**.
     - If the email is not received, learners can click **"Resend request" ("Gửi lại yêu cầu")** or return via **"← Back to login" ("← Quay lại đăng nhập")**.

### 2.4. Password Reset Process (`/reset-password`)
- **Direct Static URL:** `http://localhost:5173/reset-password` (accessed with a verification token from the email link)
- **Steps:**
  1. Open the reset link received in the email.
  2. Enter the new password satisfying the 5 security standards.
  3. Re-enter the new password in the confirmation box and click **"Reset Password →" ("Đặt lại mật khẩu →")**.

### 2.5. Personal Profile Management (`/profile`)
- **Direct Static URL:** `http://localhost:5173/profile`
- **Core Features & Layout:**
  1. **Theme Switcher:** Allows learners to toggle seamlessly between **Dark Theme** and **Light Theme** via the header switch.
  2. **Learning Overview Widgets:**
     - *Courses in Progress:* Number of currently active courses.
     - *Completed Courses:* Total courses passed through review quizzes.
     - *Known Skills:* Number of skills mastered and recorded in the profile.
     - *Active Learning Paths:* Number of active roadmap trees currently followed.
  3. **Identity & Profile Info:**
     - *Avatar:* Upload image directly (JPG/PNG format, maximum file size 2 MB; returns HTTP 413 if oversized or 415 if invalid format) or provide an image URL.
     - *Full Name:* Editable user display name.
     - *Email, Role (Student), and Join Date:* Read-only security fields.
  4. **Quick Access Sections:** Displays quick lists of ongoing courses, current known/learning skills, and recent quiz history.

### 2.6. Password Change in Settings
- **Access Route:** Navigate to Profile (`/profile`) $\rightarrow$ Click **"Change Password" ("Đổi mật khẩu")**.
- **Steps:**
  1. Enter current password (if incorrect, system returns error `400: Current password is incorrect`).
  2. Enter new password meeting all complexity standards and **must be different from the current password**.
  3. Re-enter new password and click **"Save Changes →" ("Lưu thay đổi →")**.

### 2.7. "My Skills" Management Subsystem (`/profile` $\rightarrow$ "My Skills" Tab)
- **Direct Access Route:** Navigate to `← Profile` $\rightarrow$ Settings sidebar menu $\rightarrow$ Select **"My Skills" ("Kỹ năng của tôi")** tab (or click "Manage" on the Skills widget on the Profile Dashboard).
- **Core Synchronization Rule:**
  > *"Mark skills you already know or are currently learning. When passing a course review quiz, skills covered in that course automatically transition to Known."*
- **Detailed Functional Components:**
  1. **Add New Skill (Input & Quick Action):**
     - *Skill Search Field:* Search and select skills from the system's standardized catalog of 5,893 skills (`🔍 Search in skill catalog`).
     - *Initial Status:* Dropdown to designate initial state (**"Known" / "Đã biết"** or **"Learning" / "Đang học"**).
     - *Action Button:* Click **"+ Add" ("+ Thêm")** to append the skill to the pending staging list.
  2. **Pill Filter Tabs:**
     - **All (N):** Shows all tracked personal skills.
     - **Known (N):** Filters skills mastered by the learner.
     - **Learning (N):** Filters skills currently being studied.
  3. **Interactive Skills Table:**
     - *Skill Name:* Name of the skill. Newly added uncommitted items display a small yellow tag **"Newly added" ("Mới thêm")** with an active row highlight.
     - *Status (Inline Status Dropdown):* Learners can click directly on the status badge to switch between **"Known ▾" ("Đã biết ▾")** and **"Learning ▾" ("Đang học ▾")**. If marked for deletion, the status turns into a red warning tag **"Will delete" ("Sẽ xóa")** with the skill text strikethrough/dimmed.
     - *Last Updated:* Shows the last modified timestamp (e.g., `20/10/2025`). Unsaved items display **"Unsaved" ("Chưa lưu")**.
     - *Row Actions:*
       - Trash Icon (🗑️): Marks the skill for deletion.
       - Undo Icon (↶): Reverses the deletion for rows currently marked as "Will delete".
  4. **Batch Save & Pending Changes Bar:**
     - To optimize performance and avoid excessive network requests (`PATCH /api/me/skills`), all modifications (Additions, Status changes, Deletions) enter a **Pending State**.
     - A floating notification bar pinned at the bottom displays: **`X unsaved changes · save once for all` ("X thay đổi chưa lưu · lưu một lần cho tất cả")**.
     - **"Undo" ("Hoàn tác") Button:** Discards all pending modifications and resets the table to its previous server state.
     - Orange **"Save Changes" ("Lưu thay đổi") Button:** Executes an atomic batch transaction updating all modifications in a single operation.

---

## 3. MOOC COURSE CATALOG SUBSYSTEM (`/courses` & `/courses/{id}`)

### 3.1. Course Catalog Browse Page (`/courses`)
- **Direct Static URL:** `http://localhost:5173/courses`
- **Data Repository:** Manages 4,509 online courses mapped from globally renowned academic and industry partners.
- **Smart Filter Controls:**
  - *Keyword Search (`search`):* Fast full-text lookup by course title or syllabus description.
  - *Skill Filter (`skill`):* Filters courses teaching specific technical skills.
  - *Level Filter (`level`):*
    - **Beginner (Cơ bản):** 2,747 foundational courses requiring no prior programming knowledge.
    - **Intermediate (Trung cấp):** 1,562 courses for intermediate practitioners.
    - **Advanced (Nâng cao):** 200 courses covering specialized algorithms, system architecture, and optimization.
  - *Sort Options (`sort_by`):* Sort by Highest Rating (★) or Number of Reviews/Enrolled Students.
- **Course Card Layout:**
  - Authenticated MOOC platform badge.
  - Course title and provider (e.g., Stanford University, Google, IBM, UC Davis).
  - Star rating average (★ 1.0 – 5.0) and review counts.
  - Core skill tags.
  - Bookmark toggle icon and **"View Details" ("Xem chi tiết")** button.

### 3.2. Course Details Page (`/courses/{id}`)
- **Direct Static URL:** `http://localhost:5173/courses/{id}`
- **Page Sections:**
  1. *Course Overview:* Title, institution, instructors, level, schedule, and comprehensive syllabus.
  2. *Skill Accrual Matrix:* Visually distinguishes skills taught in the course:
     - Green badge labeled **"You already know" ("Bạn đã biết")**: Skills previously mastered by the learner.
     - Badge labeled **"Not yet acquired" ("Chưa có")**: New skills the learner will gain upon course completion.
  3. *3-Stage Course Journey Tracker:*
     - **Stage 1 — Saved (Đã lưu):** Marked for future review.
     - **Stage 2 — Ongoing (Đang học):** Active study session opened via external MOOC link.
     - **Stage 3 — Completed (Hoàn thành):** Verified after scoring $\ge 60\%$ on the course review quiz.
  4. *Right Action Control Panel:*
     - **"Join Course ↗" ("Tham gia học ↗") Button:** Opens the original course link on the external platform in a new browser tab and automatically transitions status to `ongoing`.
     - **"Bookmarked / Remove Bookmark" ("Đã lưu · Bỏ lưu") Toggle:** Adds or removes the course from the user's bookmarks.
     - **"Take Review Quiz" ("Làm bài ôn tập") Button:** Jumps directly to the course's 20-question review exam.
     - **"Stop Tracking" ("Ngừng theo dõi") Button:** Sets course status to `abandoned`.

---

## 4. MY COURSES MANAGEMENT SUBSYSTEM (`/my-courses`)

- **Direct Static URL:** `http://localhost:5173/my-courses`
- **Purpose:** Centralized personal learning workspace categorized into 4 tabs:
  1. **"Ongoing" ("Đang học") Tab:**
     - Displays all active courses the user has joined.
     - Quick actions: **"Open Course ↗" ("Mở khóa học ↗")**, **"Take Review Quiz" ("Làm bài ôn tập")**, and **"Stop Tracking" ("Ngừng theo dõi")**.
  2. **"Bookmarked" ("Đã lưu") Tab:**
     - Stores courses saved for later.
     - Actions: **"Join Course ↗" ("Tham gia học ↗")** or **"Remove Bookmark" ("Bỏ lưu")**.
  3. **"Completed" ("Hoàn thành") Tab:**
     - Lists all courses where the learner achieved $\ge 60\%$ on the review quiz.
     - Corresponding skills are officially accredited and synchronized into the user's profile as "Known".
  4. **"Abandoned" ("Đã bỏ") Tab:**
     - Contains dropped courses. Learners can resume learning at any time without losing historical quiz records.

---

## 5. AI LEARNING PATH ADVISOR & ROADMAP CANVAS SUBSYSTEM

### 5.1. Personal Learning Paths Directory (`/ai-learning-path`)
- **Direct Static URL:** `http://localhost:5173/ai-learning-path`
- **Features:**
  - Manages roadmaps across 3 status tabs: **"Following" ("Đang theo")**, **"Completed" ("Hoàn thành")**, **"Abandoned" ("Đã từ bỏ")**.
  - Path Summary Card: Roadmap title, career goal, percentage progress bar based on acquired skills (e.g., `2/7 skills`), last updated timestamp, and **"View Roadmap" ("Xem lộ trình")** button.
  - Action Button: **"+ Create New Path with AI" ("+ Tạo lộ trình mới với AI")**.

### 5.2. AI Consultant — Conversational Path Generation
- **Workflow:**
  1. Learner enters career/technical aspirations in natural language (e.g., *"I want to become a Data Analyst. I know Excel but have no programming background."*).
  2. AI parses the objective, extracting and mapping keywords against the 5,893 standardized skills.
  3. System evaluates Skill Graph relations (prerequisites, extensions) and calculates cosine similarity against historical learning trajectories:
     $$\text{sim}_i = \text{cosine\_similarity}(q, p_i)$$
  4. Renders an interactive Draft Roadmap Canvas alongside the conversation.
  5. The learner can request live conversational adjustments (e.g., *"Can you add basic Machine Learning as well?"*).
  6. Learner clicks **"Save This Path →" ("Lưu lộ trình này →")** to commit to the database or **"Discard" ("Bỏ đề xuất")**.

### 5.3. Roadmap Canvas Detail & Editor (`/ai-learning-path/{id}`)
- **Direct Static URL:** `http://localhost:5173/ai-learning-path/{id}`
- **Two-Column Interactive Workspace:**
  - **Left Column — Visual Roadmap Graph:**
    - Interactive directed graph connecting skill nodes via prerequisite arrows (`from_skill` $\rightarrow$ `to_skill`).
    - Standard Node Color Legend:
      - **Known (Đã biết):** Verified through quiz completions or profile manual confirmations.
      - **Learning (Đang học):** Belonging to an active ongoing course.
      - **Unlearned (Chưa học):** Upcoming required milestones.
      - **Target (Mục tiêu):** Core objective skill nodes.
      - **Extension (Mở rộng):** Advanced elective recommendations.
    - *Flexibility Principle:* The roadmap is an orientation guide. Learners are never forced into a rigid linear sequence and may explore any node at will.
  - **Right Column — Skill Details & Course Recommendations:**
    - Clicking any node (e.g., Pandas) inspects its prerequisites, extensions, and curated course recommendations.
    - Courses are ranked dynamically using semantic and level-fit matching:
      $$\text{Score}(u, s, c) = 0.7 \times \text{skill\_match}(s, c) + 0.3 \times \text{level\_fit}(u, s, c)$$
    - Includes quick buttons: **"Join Course ↗"** and **"Bookmark"**.
  - **Roadmap Management Toolbar:**
    - **"+ Add Skill / Connection" ("+ Thêm kỹ năng / kết nối")**: Modal popup to search system skills, assign role (`Prerequisite`, `Extension`), set display order, and define directed edges.
    - **"Rename" ("Đổi tên")**: Update path title.
    - **"Abandon Path" ("Từ bỏ lộ trình")**: Marks path as `abandoned` while preserving history.

---

## 6. AI QUIZ PRACTICE & ASSESSMENT SUBSYSTEM (`/ai-quiz-practice`)

The quiz practice subsystem provides an objective, standardized evaluation of knowledge gained from each course, serving as the required milestone to officially complete courses and record skills.

> [!IMPORTANT]
> **Core Nature of AI Quiz Practice (Fundamental Distinction from AI Tutor):**
> AI Quiz Practice **generates questions strictly based on the Skills** mapped to the course. All multiple-choice questions, tests, and explanations in this subsystem are **purely theoretical and academic in nature, with no situational case studies or practical project contexts**. Its sole purpose is to verify standardized theoretical recall and conceptual understanding to certify course completion.

### 6.1. Quiz Intro & Setup (`/ai-quiz-practice/intro` or `/courses/{id}/review`)
- **Standardized Exam Configuration:**
  - **Question Count:** Exactly 20 multiple-choice questions evenly distributed across the course's mapped skills (pure theory).
  - **Passing Threshold:** $\ge 60\%$ (at least 12/20 correct answers).
  - **Attempts Allowed:** Unlimited ($\infty$), allowing repeated revision without penalty.
- **System Rules:**
  - Scoring $\ge 60\%$ transitions the course to **"Completed" ("Hoàn thành")** and registers all mapped skills as **"Known" ("Đã biết")** in the user's profile.
  - Unanswered questions are scored as incorrect.
  - Scores and explanations are archived in history and automatically dispatched to the learner's registered email.
- **Resume In-Progress Exam:** If a prior attempt is unfinished, a banner alerts: *"You have an unfinished attempt · answered X/20 questions"* with a **"Continue in-progress attempt" ("Tiếp tục bài đang làm")** button.
- **Availability Requirement:** Learners must join the course first (`ongoing`), and the course's question bank must contain at least 20 active questions.

### 6.2. Active Quiz Session Interface (`/ai-quiz-practice/session`)
- **Exam Testing Screen:**
  - Header displays current skill category (e.g., *Skill: Pandas*), question index (*Question 8 / 20*), and a progress bar.
  - Question stem and 4 choices (A, B, C, D).
  - Navigation: **"← Previous Question"** and **"Next Question →"**.
  - **"Pause, continue later" ("Tạm rời, làm tiếp sau") Button:** Saves all answered choices to the server so the session can be resumed anytime.
- **Question Navigator Sidebar:**
  - 20-number grid with status color indicators:
    - *Dark Orange:* Answered.
    - *White with Gray Border:* Unanswered.
    - *Orange Highlight Border:* Currently active on screen.
  - Progress tracker: *Answered 9/20* with warning: *"11 unanswered questions remaining. Blank answers will be scored as incorrect."*
  - **"Submit Exam" ("Nộp bài") Button:** Prompts confirmation before grading.

### 6.3. Quiz Result Summary (`/ai-quiz-practice/result`)
- **Summary Metrics Display:**
  - Circular percentage score gauge (e.g., 85%).
  - Accuracy ratio: (e.g., `17/20 correct`).
  - Outcome badge: **"✓ Passed (Passing score $\ge 60\%$)"** or **"Failed"**.
  - Submission timestamp.
- **Automated State Updates:**
  - Course status automatically updated to **Completed**.
  - Associated skills recorded as **Known** in profile.
  - Detailed score report dispatched to user email.
- **Action Buttons:**
  - **"View Detailed Answers →" ("Xem chi tiết đáp án →")**.
  - **"Retake Quiz" ("Làm lại")**.
  - **"Back to My Courses" ("Về khóa học của tôi")**.

### 6.4. Answer Review & Explanation (`/ai-quiz-practice/result/detail`)
- **Review Filters:** Toggle between **"All (20)"** or **"Incorrect / Blank (X)"** to isolate knowledge gaps.
- **Question Breakdown:**
  - Associated skill badge.
  - Question stem and all 4 options.
  - Clear visual indicators:
    - User's selection labeled **"Your choice" ("Bạn chọn")**.
    - System correct answer highlighted in color and labeled **"Correct answer" ("Đáp án đúng")**.
    - Status badge: **Correct**, **Incorrect**, or **Blank (counted as incorrect)**.
  - **"Explanation" ("Giải thích") Box:** Provides theoretical definitions and academic reasoning retrieved from the question bank.

### 6.5. Quiz History (`/ai-quiz-practice` or `/me/review-history`)
- **Direct Static URL:** `http://localhost:5173/ai-quiz-practice`
- **History Filters:** Filter by specific Course or by Result (*All*, *Passed*, *Failed*).
- **Summary Table:** Paginated table listing Submission Time, Course Name, Score (%), Correct/Total ratio, Result (Passed/Failed), and Actions (**"View Details"** or **"Retake"**).

---

## 7. AI TUTOR SUBSYSTEM (PRACTICAL CODE MENTOR)

### 7.1. Scope & Conversational Capabilities (`/ai-tutor`)
- **Direct Static URL:** `http://localhost:5173/ai-tutor`
- **Role:** 24/7 technical mentor specializing in applied software engineering and real-world problem-solving.
- **Core Competencies:**
  1. *Applied Theory & Practical Case Studies:* Explains abstract programming concepts through production case studies and real project architecture rather than dry academic definitions.
  2. *Code Analysis & Debugging:* Learners paste buggy snippets or terminal traces. AI Tutor diagnoses root causes, points out problematic lines, and provides clean refactored solutions with rationale.
  3. *Multi-turn Contextual Memory:* Maintains isolated session memory across exchanges, enabling deep, continuous technical inquiry.

### 7.2. Interactive Chat Features
1. **Suggested Prompts (`suggested_prompts`):**
   - Clickable suggestion pills displayed above the input field based on the active topic.
   - Promotes horizontal skill expansion (e.g., *"Compare Pandas DataFrame vs. SQL Table in production environments"*, *"Best practices for optimizing queries on large datasets"*).
2. **Interactive In-Chat Quizzes (`INLINE_QUIZ`):**
   - AI Tutor automatically triggers the **INLINE_QUIZ** feature to generate **practical scenario-based + theoretical questions** directly inside the chat stream for the learner to answer.
   - AI Tutor checks and evaluates the accuracy of the learner's written response and delivers **in-depth reinforcement feedback based on their specific answer and logic**. In contrast to AI Quiz Practice, these questions and explanations emphasize applied problem-solving and engineering trade-offs.

---

## 8. SECURITY PRINCIPLES & GOVERNANCE RULES FOR LEARNERS

1. **User Data Isolation:**
   - Learners only have access to view, update, and manage their own profiles, learning paths, enrolled courses, and assessment records. Cross-tenant or unauthorized record access is strictly forbidden.
2. **Global Knowledge Graph Immutability:**
   - The master catalog of 5,893 skills, 213 relationships, and course listings is maintained by System Administrators. Customizing personal paths never mutates the underlying global graph.
3. **Independent Course Completion Policy:**
   - Opening an external MOOC link only records the course as "Ongoing".
   - A course is only recognized as "Completed" and skills recorded as "Known" once the learner achieves $\ge 60\%$ on the standardized 20-question review quiz.
4. **AI Service Fault Tolerance:**
   - AI response latency typically spans 2 to 15 seconds. If the AI service experiences temporary downtime or timeouts, user-friendly alerts are returned while all previously saved database records remain intact.

---

## 9. ERROR CODE REFERENCE & TROUBLESHOOTING GUIDE

| Error Code / Scenario | Root Cause | Learner Resolution |
|---|---|---|
| **Error 400 (Bad Request)** on password change | Current password does not match database record, or new password is identical to old password. | Verify CapsLock; enter the exact current password; ensure new password differs from current. |
| **Error 401 (Unauthorized)** | Expired session (Access Token expired past 30 mins with invalid Refresh Token) or unauthenticated request. | Navigate to Login page (`http://localhost:5173/login`) to re-authenticate session. |
| **Error 403 (Forbidden)** | Learner attempting to access admin endpoints (`/admin/*`) or modify another user's paths/quizzes. | Permission restricted to students. Return to personal dashboard. |
| **Error 404 (Not Found)** on path/quiz attempt | The path ID (`path_id`) or attempt ID (`attempt_id`) does not exist or does not belong to the current account. | Check personal lists at `/ai-learning-path` or `/ai-quiz-practice` to select valid records. |
| **Error 413 (Payload Too Large)** on avatar upload | Uploaded image file exceeds maximum size threshold (max 2 MB). | Compress or resize image below 2 MB before uploading. |
| **Error 415 (Unsupported Media Type)** on avatar upload | Uploaded file is not in an acceptable image format. | Upload only `.jpg` or `.png` files. Formats like `.gif`, `.bmp`, or docs are rejected. |
| **Error 503 (Service Unavailable)** on AI features | AI inference service (Qwen3 / LLM gateway) is initializing or experiencing high load. | Wait 10–15 seconds and click "Retry". Previously saved data is never lost. |
| **Quiz button disabled / cannot start** | Learner has not clicked "Join Course" yet, or course question bank has under 20 questions. | Click **"Join Course ↗"** to set status to "Ongoing". If still disabled, questions are being added. |
| **Password reset email not received** | Email filtered into Spam/Junk folder or entered email does not match any registered account. | Check Spam/Promotions folder; re-verify email spelling and submit request again. |

---

## 10. FREQUENTLY ASKED QUESTIONS (LEARNER FAQ)

### 10.1. Account & Authentication
- **Q1: Can I change my registered email address?**
  - *Answer:* No. The email address serves as the unique account identifier within EduMentor AI and cannot be modified after registration. You can update your display Full Name and Avatar via Profile settings.
- **Q2: How long is the password reset link valid?**
  - *Answer:* The link is single-use and expires automatically after 15 to 30 minutes for security purposes.

### 10.2. Courses & Learning Paths
- **Q3: Does clicking "Join Course" charge me money?**
  - *Answer:* No. Clicking "Join Course ↗" simply opens the course page on the external MOOC platform (e.g., Coursera) in a new tab and updates your internal status to "Ongoing". Decisions to audit for free or purchase verified certificates occur on the external provider's platform.
- **Q4: Must I follow the exact order of arrows on the roadmap graph?**
  - *Answer:* Not at all. The Roadmap Canvas illustrates prerequisite logic and recommended progressions. Learners have complete autonomy to learn any skill node in whatever order suits their personal goals.
- **Q5: Can I add custom skills to an AI-generated learning path?**
  - *Answer:* Yes. On the Roadmap detail canvas (`/ai-learning-path/{id}`), click **"+ Add Skill / Connection"** to search the system's 5,893 skills and connect edges into your personal tree.

### 10.3. Assessment & Review Quizzes
- **Q6: What score is required to pass a review quiz and complete a course?**
  - *Answer:* You must score **60% or higher** (answering at least 12 out of 20 multiple-choice questions correctly).
- **Q7: What happens if I fail a quiz attempt? Are there retake limits?**
  - *Answer:* There are no penalties and you have **unlimited retakes ($\infty$)**.
- **Q8: What if I am interrupted while taking a quiz?**
  - *Answer:* Click **"Pause, continue later" ("Tạm rời, làm tiếp sau")**. The system saves all selected answers. When returning to the quiz intro page, click **"Continue in-progress attempt"**.

### 10.4. AI Tutor & Interactive Drills
- **Q9: Can AI Tutor analyze and debug my code?**
  - *Answer:* Yes. Paste your source code and error messages directly into `/ai-tutor`. AI Tutor identifies the root cause and provides clean, commented solutions with architectural explanations.
- **Q10: How do I practice topics discussed with AI Tutor? How does it differ from AI Quiz Practice?**
  - *Answer:* AI Tutor automatically activates the **INLINE_QUIZ** feature to generate practical scenario-based + theoretical questions right inside the chat for you to answer, providing personalized feedback based on your specific logic. Conversely, AI Quiz Practice tests are strictly theoretical multiple-choice evaluations based on skill definitions without applied project scenarios.

---

## 11. VECTOR DATABASE METADATA CHUNKING GUIDE (FOR RAG)

When ingesting this document into a Vector Database, partition by level-2 headings (`##`) and attach the following metadata tags for optimal semantic routing:

- **Chunk Section 1:** `category: "overview", tags: ["introduction", "rag_boundaries", "navigation", "localhost:5173"]`
- **Chunk Section 2:** `category: "auth", tags: ["registration", "login", "forgot_password", "reset_password", "profile", "dark_mode", "my_skills"]`
- **Chunk Section 3:** `category: "courses", tags: ["course_catalog", "course_detail", "mooc", "levels", "known_skills"]`
- **Chunk Section 4:** `category: "my_courses", tags: ["my_courses", "ongoing", "bookmarked", "completed", "abandoned"]`
- **Chunk Section 5:** `category: "learning_path", tags: ["ai_learning_path", "roadmap_canvas", "skill_nodes", "prerequisites", "extensions"]`
- **Chunk Section 6:** `category: "quiz", tags: ["review_quiz", "20_questions", "passing_score_60", "pause_and_resume", "answer_review", "theory_only"]`
- **Chunk Section 7:** `category: "ai_tutor", tags: ["ai_tutor", "code_mentor", "debugging", "suggested_prompts", "inline_quiz", "practical_questions"]`
- **Chunk Section 8 & 9:** `category: "troubleshooting", tags: ["error_codes", "error_400", "error_413", "error_415", "error_503", "faq"]`
- **Chunk Section 10:** `category: "faq", tags: ["learner_faq", "frequently_asked_questions", "quick_answers"]`

