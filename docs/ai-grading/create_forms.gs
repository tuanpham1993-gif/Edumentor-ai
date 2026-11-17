/**
 * EduMentor AI — tạo 2 Google Form thu bài cho bộ bài chuẩn (B4 · Tuấn · 14/11/2026).
 * Sinh tự động từ backend/data/ai-grading/split.json + course_312_en.json — KHÔNG sửa tiêu đề câu:
 * lệnh `gold_sheets collect` nhận câu qua mã [XX-TL-NN] ở đầu tiêu đề và câu đồng ý qua chữ "Consent".
 *
 * Cách dùng: script.google.com → New project → dán toàn bộ file này → chọn hàm createGoldForms → Run
 * → cho phép quyền (tạo Form trong Drive của bạn) → xem link ở View → Logs (Execution log).
 */

const FORMS = {
  "A": [
    {
      "title": "[PY-TL-03] Explain what the print() and input() functions do in Python.",
      "help": ""
    },
    {
      "title": "[CS-TL-03] How is a syntax error different from a logic error? Give an example of each.",
      "help": ""
    },
    {
      "title": "[ITER-TL-01] Explain the difference between the break statement and the continue statement in a loop.",
      "help": ""
    },
    {
      "title": "[VAR-TL-05] What is None in Python? How is it different from a variable that has never been assigned a value?",
      "help": ""
    },
    {
      "title": "[COND-TL-03] Explain the meaning of the three logical operators and, or, not.",
      "help": ""
    }
  ],
  "B": [
    {
      "title": "[PY-TL-02] Compare lists and tuples in Python, and give an example of when you should use a tuple.",
      "help": ""
    },
    {
      "title": "[CS-TL-05] This program should compute the average of two numbers, but it prints a wrong result:",
      "help": "a = 4\nb = 6\navg = a + b / 2\nprint(avg)\nWhat type of error is this, why is it wrong, how do you fix it, and name one way to debug it."
    },
    {
      "title": "[ITER-TL-05] Write (or describe) a program that asks the user to enter a password until they enter 'abc123', and then prints 'Login successful'. Explain why you use while instead of for.",
      "help": ""
    },
    {
      "title": "[VAR-TL-02] State the rules for naming variables in Python, give one valid name and one invalid name, and explain what \"dynamic typing\" means.",
      "help": ""
    },
    {
      "title": "[COND-TL-06] A person gets a ticket discount if they are under 12 or aged 60 or over. Write the matching if condition, explain why you use or and not and, and say what happens when age = 30.",
      "help": ""
    }
  ]
};

const INTRO =
  "This short quiz helps us test an automatic grader for the EduMentor AI student project. Answer in your own words, " +
  "in English, as you would in a real test — short answers are fine, and wrong answers are useful too. Please do not " +
  "look things up or use AI tools. We do not collect your name or email. Your answers are used only to measure the " +
  "grader's accuracy in our course project and are not published.";

const CONSENT_TITLE =
  "Consent: I agree that my anonymous answers may be used to evaluate the grader in this course project.";

function createGoldForms() {
  for (const [name, items] of Object.entries(FORMS)) {
    const level = name === "A" ? "easy" : "advanced";
    const form = FormApp.create(`EduMentor AI - Python short answers (Form ${name}, ${level})`); // gạch ngang thường: dấu "—" làm hỏng tên file .zip tải về trên Windows
    form.setDescription(INTRO);
    form.setCollectEmail(false);
    form.setAllowResponseEdits(false);
    form.setLimitOneResponsePerUser(false); // true sẽ bắt đăng nhập Google → mất ẩn danh
    form.setShowLinkToRespondAgain(false);
    form.setProgressBar(true);

    // Trang 1: đồng ý. Chọn "No" → nộp luôn, không thấy câu hỏi.
    const consent = form.addMultipleChoiceItem().setTitle(CONSENT_TITLE).setRequired(true);
    const questions = form.addPageBreakItem().setTitle("Questions (about 15–20 minutes)")
      .setHelpText("Answer each question in a few sentences. You may skip a question you cannot answer.");
    consent.setChoices([
      consent.createChoice("Yes, I agree", questions),
      consent.createChoice("No", FormApp.PageNavigationType.SUBMIT),
    ]);

    // Trang 2: 5 câu tự luận (Paragraph, không bắt buộc).
    for (const it of items) {
      const q = form.addParagraphTextItem().setTitle(it.title).setRequired(false);
      if (it.help) q.setHelpText(it.help);
    }
    form.setConfirmationMessage("Thank you! Your answers help us measure the grader's accuracy.");

    Logger.log(`Form ${name} — gửi link này: ${form.getPublishedUrl()}`);
    Logger.log(`Form ${name} — link chỉnh sửa (giữ riêng): ${form.getEditUrl()}`);
  }
}
