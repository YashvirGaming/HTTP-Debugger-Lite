<h1 align="center">HTTP Debugger Lite</h1>

<p align="center">
  <b>Advanced HTTP/HTTPS Debugger for Windows</b><br>
  Built with ❤️ by <b>Yashvir Gaming</b>
</p>

<p align="center">
  <a href="https://github.com/YashvirGaming">
    <img src="https://img.shields.io/badge/GitHub-YashvirGaming-0a0a0a?style=for-the-badge&logo=github">
  </a>
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Built%20With-Python-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/License-Free-green?style=for-the-badge">
</p>

<hr>

<h2>Overview</h2>
<p>
  HTTP Debugger Lite is a Windows desktop application built in Python with PySide6 that captures,
  inspects, and displays live HTTP and HTTPS traffic in a clean modern interface.
</p>

<p>
  It provides a lightweight debugging experience inspired by premium HTTP debugging tools, with
  support for request and response inspection, JSON formatting, HTML preview, filtering, and
  installer packaging.
</p>

<hr>

<h2>Features</h2>

<ul>
  <li>Live HTTP and HTTPS traffic capture</li>
  <li>Automatic proxy enable / disable inside the app</li>
  <li>MITM-based HTTPS inspection</li>
  <li>Request list with:
    <ul>
      <li>ID</li>
      <li>Method</li>
      <li>Status code</li>
      <li>URL</li>
      <li>Content type</li>
      <li>Size</li>
      <li>Duration</li>
    </ul>
  </li>
  <li>Request Details tabs:
    <ul>
      <li>Header</li>
      <li>Content</li>
      <li>Raw</li>
    </ul>
  </li>
  <li>Response Details tabs:
    <ul>
      <li>Header</li>
      <li>Content</li>
      <li>Raw</li>
      <li>HTML Preview</li>
    </ul>
  </li>
  <li>Pretty-printed JSON responses with syntax highlighting</li>
  <li>Embedded HTML render preview using Qt WebEngine</li>
  <li>Search and filter support</li>
  <li>Right-click copy actions</li>
  <li>Dark neon / cyber-inspired UI</li>
  <li>Packaged EXE build</li>
  <li>Custom Windows installer with branding</li>
</ul>

<hr>

## ⚠️ IMPORTANT (READ BEFORE USING)

> **⚠️ THIS APPLICATION MUST BE RUN AS ADMINISTRATOR ⚠️**

- Required for HTTPS interception  
- Required for certificate installation  
- Required for system proxy control  

👉 Without admin rights:
- HTTPS traffic ❌ will NOT work  
- Certificate installation ❌ will fail  
- Debugger will be limited  

<hr>

<h2>Screenshots</h2>

<p>
  <img width="1024" height="1536" alt="main-ui" src="https://github.com/user-attachments/assets/1c5a6149-d217-4d71-a042-db884ffced83" />
  
  <img width="1588" height="1127" alt="request-response" src="https://github.com/user-attachments/assets/6cbea48d-5bf6-4a2c-a0bb-2af24152ae5c" />
  
  <img width="588" height="462" alt="installer" src="https://github.com/user-attachments/assets/317fe2e6-4eb4-4614-954f-ffe3373c64c2" />
</p>

<pre>
/assets/screenshots/main-ui.png
/assets/screenshots/request-response.png
/assets/screenshots/installer.png
</pre>

<hr>

<h2>How It Works</h2>

<ol>
  <li>The app starts a local proxy backend.</li>
  <li>Windows proxy is automatically enabled when capture starts.</li>
  <li>HTTPS traffic is inspected through the MITM backend.</li>
  <li>Captured sessions are displayed live in the GUI.</li>
  <li>When paused or closed, proxy settings are restored automatically.</li>
</ol>

<hr>

<h2>Project Highlights</h2>

<ul>
  <li>Clean desktop UI built with PySide6</li>
  <li>Real-time request/response monitoring</li>
  <li>Modern installer with custom branding</li>
  <li>Designed as a lightweight alternative to premium debugging tools</li>
</ul>

<hr>

---

<h2>Author</h2>

<p>
  <b>Yashvir Gaming</b><br>
  GitHub: <a href="https://github.com/YashvirGaming">https://github.com/YashvirGaming</a>
</p>

<hr>

<h2>Disclaimer</h2>

<p>
  This project is intended for debugging, development, educational use, and authorized traffic
  inspection within environments you control or are permitted to test.
</p>
