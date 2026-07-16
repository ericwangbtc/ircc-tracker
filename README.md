# IRCC Tracker Local

一个只在本机运行的 Python 命令行工具，用于查询你自己的 IRCC Application Status Tracker 数据。

它直接连接：

- IRCC 使用的 AWS Cognito 登录服务；
- IRCC Application Status Tracker API。

密码、ID Token 和 Refresh Token 只存在于当前 Python 进程的内存中，不会写入磁盘。工具始终开启 TLS 证书验证，不会关闭证书验证，也不会将数据发送到第三方服务器。

> 这是非官方工具。IRCC 的内部 API 没有公开文档，可能随时变化。请仅用于查询自己的账户；遇到 403、WAF 或限流时不要尝试绕过。

## 安装

需要 Python 3.11 或更新版本。请先通过操作系统、Python 官方安装包或你常用的包管理器安装合适的 Python 版本。

克隆并进入项目目录：

```bash
git clone https://github.com/ericwangbtc/ircc-tracker.git
cd ircc-tracker
```

在 macOS 或 Linux 上安装：

```bash
python3 --version
python3 -m venv .venv

source .venv/bin/activate
python -m pip install --upgrade pip setuptools
python -m pip install .
```

在 Windows PowerShell 上安装：

```powershell
py -3.11 --version
py -3.11 -m venv .venv

.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools
python -m pip install .
```

如果 `python3` 指向低于 3.11 的版本，请使用系统中对应 Python 3.11 或更新版本的命令替代它。

## 使用

每次打开新的终端后，记得激活安装时创建的虚拟环境。

macOS 或 Linux：

```bash
source .venv/bin/activate
ircc-tracker
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
ircc-tracker
```

如果终端提示 `command not found: ircc-tracker`，通常是因为虚拟环境尚未激活，或者安装步骤尚未完成。

程序会依次完成以下步骤：

1. 在 `UCI:` 后输入自己的 UCI。可以输入纯数字，也可以保留连字符，例如 `12-3456-7890`；程序发送请求前会自动移除连字符。
2. 在 `Tracker password:` 后输入 IRCC Application Status Tracker 的密码。输入密码时终端不会显示字符或星号，这是正常的安全行为；输入完成后按 Enter。
3. 程序显示 `Connecting to IRCC…`，完成登录后列出当前账户下的申请。
4. 在 `Select application number:` 后输入申请左侧的**列表序号**，例如输入 `1`，而不是输入 `E123456789` 形式的申请号。
5. 程序获取所选申请的详情，并以格式化 JSON 输出到终端。

交互示例中的 UCI、申请号和日期均为虚构数据：

```bash
ircc-tracker
UCI: 12-3456-7890
Tracker password:
Connecting to IRCC…

Applications:
  1. E123456789  PR  inProgress  2026-01-15T12:00:00.000Z
Select application number: 1
{
  "applicationNumber": "E123456789",
  "details": {
    "...": "IRCC 返回的申请详情"
  }
}
```

可以按 Ctrl+C 取消查询。程序退出后，密码和登录令牌会随进程结束而消失。

JSON 输出是 IRCC 后台返回的原始申请数据，字段可能随 IRCC 调整而变化。输出可能包含姓名、出生日期、住址、电话、电子邮箱、UCI、申请号和申请状态等敏感信息。分享终端截图、错误报告或日志前，请先完整遮盖这些内容，不要将原始输出发布到 GitHub Issue 或其他公开位置。

### 登录错误

程序会显示 Cognito 返回的安全错误类型，并给出对应操作建议，例如登录风控、尝试次数超限、必须重置密码或账户尚未确认。错误信息不会包含输入的密码或登录令牌。遇到安全阻止或次数限制时，请停止重复尝试，并改用官方 Tracker 验证账户状态。

## 安全说明

- 不支持通过命令行参数传入密码，避免密码进入 shell history。
- 不保存密码或令牌。
- UCI、密码和申请选择均通过交互方式输入。
- 请求超时默认为 30 秒。
- 建议手动、低频查询，不要高频轮询。

## License

本项目采用 [MIT License](LICENSE)。

---

# IRCC Tracker Local — English

A Python command-line tool that runs entirely on your computer and lets you query your own IRCC Application Status Tracker data.

It connects directly to:

- the AWS Cognito authentication service used by IRCC;
- the IRCC Application Status Tracker API.

Your password, ID Token, and Refresh Token remain in the current Python process and are never written to disk. TLS certificate verification is always enabled, and the tool does not send your data to any third-party server.

> This is an unofficial tool. IRCC's internal API is undocumented and may change at any time. Use it only to query your own account. Do not attempt to bypass HTTP 403 responses, WAF restrictions, or rate limits.

## Installation

Python 3.11 or later is required. Install a suitable Python version through your operating system, the official Python installer, or your preferred package manager.

Clone the repository and enter the project directory:

```bash
git clone https://github.com/ericwangbtc/ircc-tracker.git
cd ircc-tracker
```

Install on macOS or Linux:

```bash
python3 --version
python3 -m venv .venv

source .venv/bin/activate
python -m pip install --upgrade pip setuptools
python -m pip install .
```

Install in Windows PowerShell:

```powershell
py -3.11 --version
py -3.11 -m venv .venv

.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools
python -m pip install .
```

If `python3` points to a version older than Python 3.11, replace it with the command for an installed Python 3.11 or later version.

## Usage

Remember to activate the virtual environment whenever you open a new terminal.

macOS or Linux:

```bash
source .venv/bin/activate
ircc-tracker
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
ircc-tracker
```

If the terminal reports `command not found: ircc-tracker`, the virtual environment is probably not active or the installation has not been completed.

The program will guide you through the following steps:

1. Enter your UCI after `UCI:`. You may enter digits only or retain the hyphens, for example `12-3456-7890`; the program removes hyphens before sending the request.
2. Enter your IRCC Application Status Tracker password after `Tracker password:`. The terminal will not display characters or asterisks while you type. This is expected security behavior. Press Enter when finished.
3. The program displays `Connecting to IRCC…` and lists the applications associated with your account after authentication succeeds.
4. After `Select application number:`, enter the **list number** shown to the left of the application, such as `1`. Do not enter an application number such as `E123456789`.
5. The program retrieves the selected application's details and prints formatted JSON in the terminal.

All UCI numbers, application numbers, and dates in this example are fictional:

```bash
ircc-tracker
UCI: 12-3456-7890
Tracker password:
Connecting to IRCC…

Applications:
  1. E123456789  PR  inProgress  2026-01-15T12:00:00.000Z
Select application number: 1
{
  "applicationNumber": "E123456789",
  "details": {
    "...": "Application details returned by IRCC"
  }
}
```

Press Ctrl+C to cancel a query. Your password and authentication tokens disappear with the process after the program exits.

The JSON output contains raw application data returned by the IRCC backend, and its fields may change when IRCC updates the service. It may contain sensitive information such as your name, date of birth, address, phone number, email address, UCI, application number, and application status. Fully redact this information before sharing terminal screenshots, bug reports, or logs. Never post the raw output in a GitHub Issue or anywhere else public.

### Login errors

The program displays the safe Cognito error type with guidance for security blocks, excessive attempts, required password resets, and unconfirmed accounts. Error messages never include the password or authentication tokens. If a login is blocked for security reasons or excessive attempts, stop retrying and verify the account through the official Tracker.

## Security

- Passwords cannot be supplied through command-line arguments, preventing them from being stored in shell history.
- Passwords and tokens are not saved.
- The UCI, password, and application selection are entered interactively.
- The default request timeout is 30 seconds.
- Query manually and infrequently. Do not poll the service at a high rate.

## License

This project is licensed under the [MIT License](LICENSE).
