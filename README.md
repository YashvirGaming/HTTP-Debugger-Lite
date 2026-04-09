<h1 align="center">HTTP Debugger Lite</h1>

<p align="center">
  <b>Advanced HTTP/HTTPS Debugger for Windows</b><br>
  Built with ❤️ by <b>Yashvir Gaming</b>
</p>

<p align="center">
  <a href="https://github.com/YashvirGaming">GitHub</a>
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

<h2>Tech Stack</h2>

<ul>
  <li>Python 3.10+</li>
  <li>PySide6</li>
  <li>Qt WebEngine</li>
  <li>mitmproxy</li>
  <li>PyInstaller</li>
  <li>Inno Setup</li>
</ul>

<hr>

<h2>Screenshots</h2>

<p>
  
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
