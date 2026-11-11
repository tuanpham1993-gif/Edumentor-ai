/*
 * BẢN DEMO — KHÔNG PHẢI FRONTEND THẬT.
 *
 * Gắn vào các trang *-Live.html của prototype tĩnh để gọi API backend thật
 * (module 01 · Tuấn) khi trình bày. Frontend thật là React trong `frontend/`.
 *
 * Cần chạy:
 *   - Backend:  cd backend; uvicorn app.main:app --reload        (http://localhost:8000)
 *   - Trang UI: cd docs/EduMentor-UI-design/ui-design; python -m http.server 5500
 *               rồi mở http://localhost:5500/html/Main-Live.html
 * Backend cho phép origin localhost:5500 (core/config.py · ALLOWED_ORIGINS).
 */
(function () {
  "use strict";

  var API = "http://localhost:8000/api";
  var TOKEN_KEY = "em-demo-token";

  var LIVE_PAGES = {
    "/login": "Main-Live.html",
    "/register": "Register-Live.html",
    "/me": "Profile-Live.html",
  };

  // ---------- tiện ích ----------
  function $(sel, root) { return (root || document).querySelector(sel); }

  function injectStyle() {
    var css =
      ".live-badge{position:fixed;left:12px;bottom:12px;z-index:9999;padding:6px 10px;border-radius:8px;" +
      "background:#b45309;color:#fff;font:600 12px/1.3 'Be Vietnam Pro',system-ui,sans-serif;box-shadow:0 4px 14px rgba(0,0,0,.35)}" +
      ".live-msg{margin:4px 0 0;padding:10px 12px;border-radius:10px;font-size:14px;line-height:1.45}" +
      ".live-msg.err{background:rgba(220,38,38,.14);border:1px solid rgba(220,38,38,.55);color:#fca5a5}" +
      ".live-msg.ok{background:rgba(22,163,74,.14);border:1px solid rgba(22,163,74,.55);color:#86efac}" +
      ".live-msg ul{margin:4px 0 0 18px;padding:0}" +
      "@keyframes live-shake{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-8px)}40%,80%{transform:translateX(8px)}}" +
      ".live-shake{animation:live-shake .4s}" +
      ".live-note{margin-top:8px;font-size:12px;opacity:.75}";
    var s = document.createElement("style");
    s.textContent = css;
    document.head.appendChild(s);
  }

  function addBadge() {
    var b = document.createElement("div");
    b.className = "live-badge";
    b.textContent = "BẢN DEMO · gọi API thật tại localhost:8000";
    document.body.appendChild(b);
  }

  function showMsg(form, kind, html) {
    var box = $(".live-msg", form);
    if (!box) {
      box = document.createElement("div");
      box.setAttribute("role", kind === "err" ? "alert" : "status");
      var submit = $('button[type="submit"]', form);
      form.insertBefore(box, submit);
    }
    box.className = "live-msg " + kind;
    box.innerHTML = html;
  }

  function escapeHtml(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function shake(el) {
    el.classList.remove("live-shake");
    void el.offsetWidth;
    el.classList.add("live-shake");
  }

  // Đổi phản hồi lỗi của FastAPI thành HTML dễ đọc.
  function errorHtml(status, body) {
    var d = body && body.detail;
    if (Array.isArray(d)) {
      var items = d.map(function (e) {
        var field = (e.loc || []).slice(-1)[0];
        var msg = String(e.msg || "").replace(/^Value error, /, "");
        return "<li>" + escapeHtml(field ? field + ": " + msg : msg) + "</li>";
      });
      return "Lỗi " + status + ": dữ liệu chưa hợp lệ<ul>" + items.join("") + "</ul>";
    }
    return "Lỗi " + status + ": " + escapeHtml(d || "Có lỗi xảy ra.");
  }

  function call(method, path, data, token) {
    var headers = { "Content-Type": "application/json" };
    if (token) headers.Authorization = "Bearer " + token;
    return fetch(API + path, {
      method: method,
      headers: headers,
      body: data ? JSON.stringify(data) : undefined,
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (body) {
        return { status: res.status, ok: res.ok, body: body };
      });
    });
  }

  var NETWORK_ERR =
    "Không kết nối được backend tại <b>localhost:8000</b>. " +
    "Hãy chạy <code>uvicorn app.main:app --reload</code> trong thư mục <code>backend</code>.";

  function setBusy(form, busy) {
    var btn = $('button[type="submit"]', form);
    if (btn) btn.disabled = busy;
  }

  // Bộ prototype dùng route của app thật (/me/edit, /courses...). Trên server tĩnh các
  // đường dẫn đó không tồn tại → ánh xạ sang trang -Live hoặc trang tĩnh tương ứng.
  function wireLinks() {
    fetch("../pages.json")
      .then(function (r) { return r.json(); })
      .catch(function () { return []; })
      .then(function (pages) {
        var map = {};
        (pages || []).forEach(function (p) {
          if (p.route && !map[p.route]) map[p.route] = p.name + ".html";
        });
        Object.keys(LIVE_PAGES).forEach(function (r) { map[r] = LIVE_PAGES[r]; });

        document.addEventListener("click", function (ev) {
          var a = ev.target.closest && ev.target.closest("a[href^='/']");
          if (!a) return;
          var route = a.getAttribute("href");
          ev.preventDefault();
          if (route === "/logout") return logout();
          if (map[route]) window.location.href = map[route];
        });
      });
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_KEY);
    window.location.href = "Main-Live.html?logout=1";
  }

  // ---------- trang Đăng nhập ----------
  function initLogin() {
    var form = $("form");
    var email = $("#email");
    var password = $("#password");
    var params = new URLSearchParams(window.location.search);

    email.value = params.get("email") || "";
    if (params.get("registered")) {
      showMsg(form, "ok", "Đăng ký thành công. Kéo dây đèn rồi đăng nhập bằng tài khoản vừa tạo.");
    } else if (params.get("expired")) {
      showMsg(form, "err", "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    } else if (params.get("logout")) {
      showMsg(form, "ok", "Đã đăng xuất.");
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setBusy(form, true);
      call("POST", "/auth/login", { email: email.value, password: password.value })
        .then(function (r) {
          if (r.ok) {
            sessionStorage.setItem(TOKEN_KEY, r.body.access_token);
            showMsg(form, "ok", "Đăng nhập thành công. Đang mở hồ sơ…");
            setTimeout(function () { window.location.href = "Profile-Live.html"; }, 600);
          } else {
            showMsg(form, "err", errorHtml(r.status, r.body));
            shake(form.closest(".card") || form);
          }
        })
        .catch(function () { showMsg(form, "err", NETWORK_ERR); })
        .finally(function () { setBusy(form, false); });
    });
  }

  // ---------- trang Đăng ký ----------
  function initRegister() {
    var form = $("form");
    $("#reg-email").value = "";

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var data = {
        full_name: $("#full_name").value,
        email: $("#reg-email").value,
        password: $("#reg-password").value,
        confirm_password: $("#reg-confirm").value,
      };
      setBusy(form, true);
      call("POST", "/auth/register", data)
        .then(function (r) {
          if (r.status === 201) {
            showMsg(form, "ok", "Đăng ký thành công cho <b>" + escapeHtml(r.body.email) +
              "</b>. Đang chuyển sang đăng nhập…");
            setTimeout(function () {
              window.location.href = "Main-Live.html?registered=1&email=" + encodeURIComponent(r.body.email);
            }, 1000);
          } else {
            showMsg(form, "err", errorHtml(r.status, r.body));
            shake(form.closest(".card") || form);
          }
        })
        .catch(function () { showMsg(form, "err", NETWORK_ERR); })
        .finally(function () { setBusy(form, false); });
    });
  }

  // ---------- trang Hồ sơ ----------
  function initials(name) {
    var parts = String(name).trim().split(/\s+/);
    var first = parts[0] ? parts[0][0] : "";
    var last = parts.length > 1 ? parts[parts.length - 1][0] : "";
    return (first + last).toUpperCase();
  }

  function formatDate(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return iso;
    var dd = String(d.getDate()).padStart(2, "0");
    var mm = String(d.getMonth() + 1).padStart(2, "0");
    return dd + "/" + mm + "/" + d.getFullYear();
  }

  // Thay dữ liệu mẫu trong trang tĩnh bằng dữ liệu thật (thay theo nội dung chữ).
  function replaceText(pairs) {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var t = node.nodeValue;
      var trimmed = t.trim();
      for (var i = 0; i < pairs.length; i++) {
        var from = pairs[i][0], to = pairs[i][1];
        if (pairs[i][2] === "exact" ? trimmed === from : t.indexOf(from) !== -1) {
          t = pairs[i][2] === "exact" ? t.replace(trimmed, to) : t.split(from).join(to);
        }
      }
      node.nodeValue = t;
    }
  }

  function initProfile() {
    var token = sessionStorage.getItem(TOKEN_KEY);
    if (!token) {
      window.location.replace("Main-Live.html");
      return;
    }

    call("GET", "/me", null, token)
      .then(function (r) {
        if (r.status === 401) {
          sessionStorage.removeItem(TOKEN_KEY);
          window.location.replace("Main-Live.html?expired=1");
          return;
        }
        if (!r.ok) throw new Error("HTTP " + r.status);

        var u = r.body;
        replaceText([
          ["Nguyễn Văn A", u.full_name],
          ["nguyenvana@example.com", u.email],
          ["Tham gia 12/10/2025", "Tham gia " + formatDate(u.created_at)],
          ["NA", initials(u.full_name), "exact"],
          ["Học viên", u.role === "admin" ? "Quản trị viên" : "Học viên", "exact"],
        ]);

        var who = $("._who_7j34e_5");
        if (who) {
          var note = document.createElement("div");
          note.className = "live-note";
          note.textContent =
            "Họ tên, email, vai trò, ngày tham gia lấy từ GET /api/me (dữ liệu thật). " +
            "Thống kê, khóa học, kỹ năng bên dưới là dữ liệu mẫu — API chưa làm.";
          who.appendChild(note);
        }
      })
      .catch(function () {
        alert("Không kết nối được backend tại localhost:8000. Hãy chạy uvicorn trong thư mục backend.");
      });

    // Nút "Đăng xuất" (POST /api/auth/logout chưa có — GĐ6) → chỉ xóa token phía trình duyệt.
    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest && ev.target.closest("button");
      if (btn && btn.textContent.trim() === "Đăng xuất") {
        ev.preventDefault();
        logout();
      }
    });
  }

  // ---------- khởi động ----------
  document.addEventListener("DOMContentLoaded", function () {
    injectStyle();
    addBadge();
    wireLinks();
    var page = document.body.getAttribute("data-live");
    if (page === "login") initLogin();
    if (page === "register") initRegister();
    if (page === "profile") initProfile();
  });
})();
