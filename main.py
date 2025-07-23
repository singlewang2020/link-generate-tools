import os
import threading
import time
import urllib.parse
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>支付宝跳转链接生成器</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    input[type=text] { width: 300px; padding: 8px; font-size: 16px; }
    button { padding: 8px 16px; font-size: 16px; margin-right: 10px; }
    .result { margin-top: 20px; word-break: break-all; }
  </style>
</head>
<body>
  <h1>支付宝跳转链接生成器</h1>
  <form method="post" id="form">
    <label for="exp_locker_no">请输入 exp_locker_no：</label><br>
    <input type="text" id="exp_locker_no" name="exp_locker_no" required
           value="{{ exp_locker_no or '' }}"><br><br>
    <button type="submit">生成链接</button>
  </form>

  {% if link %}
    <div class="result">
      <strong>生成的支付宝跳转链接：</strong><br>
      <a href="{{ link }}" target="_blank" id="generatedLink">{{ link }}</a>
      <button type="button" id="copyBtn">复制链接</button>
    </div>
  {% endif %}

  <button type="button" id="shutdownBtn" style="margin-top:30px; background-color: red; color: white;">
    关闭服务
  </button>

  <script>
    document.getElementById('copyBtn')?.addEventListener('click', function() {
      const link = document.getElementById('generatedLink').textContent;
      navigator.clipboard.writeText(link).then(() => {
        alert('链接已复制到剪贴板！');
      }).catch(() => {
        alert('复制失败，请手动复制。');
      });
    });

    document.getElementById('shutdownBtn').addEventListener('click', function() {
      if (confirm("确定要关闭服务吗？")) {
        fetch('/shutdown', { method: 'POST' })
          .then(response => response.json())
          .then(data => {
            alert(data.message);
            setTimeout(() => {
              window.close(); // 关闭浏览器标签页（仅部分浏览器支持）
            }, 1000);
          });
      }
    });
  </script>
</body>
</html>
'''

def generate_alipay_link(exp_locker_no: str) -> str:
    base_url = "alipays://platformapi/startapp"
    app_id = "2021004124613039"
    page = "pages/pickup/pickupList"
    now_time = int(time.time())
    param_value = f"expLockerNo={exp_locker_no}&nowTime={now_time}"
    encoded_param_value = urllib.parse.quote(param_value, safe='')
    query = f"param%3D{encoded_param_value}"
    full_url = f"{base_url}?appId={app_id}&page={page}&query={query}"
    return full_url

@app.route('/', methods=['GET', 'POST'])
def index():
    link = None
    exp_locker_no = None
    if request.method == 'POST':
        exp_locker_no = request.form.get('exp_locker_no', '').strip()
        if exp_locker_no:
            link = generate_alipay_link(exp_locker_no)
    return render_template_string(HTML_TEMPLATE, link=link, exp_locker_no=exp_locker_no)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    def shutdown_server():
        time.sleep(1)  # 给响应时间先返回给浏览器
        os._exit(0)    # 直接退出进程

    threading.Thread(target=shutdown_server).start()
    return jsonify({"message": "服务正在关闭..."})

if __name__ == '__main__':
    app.run()
