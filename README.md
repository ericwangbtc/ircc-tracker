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

每次打开新的终端后，先进入项目目录并激活安装时创建的虚拟环境。

macOS 或 Linux：

```bash
cd ircc-tracker
source .venv/bin/activate
ircc-tracker
```

Windows PowerShell：

```powershell
cd ircc-tracker
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

## 安全说明

- 不支持通过命令行参数传入密码，避免密码进入 shell history。
- 不保存密码或令牌。
- UCI、密码和申请选择均通过交互方式输入。
- HTTPS 证书验证始终保持开启；仅对证书链异常的 IRCC API 使用操作系统证书库、certifi 根证书以及随包内置的中间证书（详见下方“TLS 证书”）。
- 请求超时默认为 30 秒。
- 建议手动、低频查询，不要高频轮询。

## TLS 证书

IRCC 的 API 服务器返回的证书链**不完整**——它缺少签发其叶子证书的中间证书
`Entrust OV TLS Issuing RSA CA 2`。浏览器会通过证书的 AIA 扩展自动补下载这张中间
证书，但 Python 的 TLS 栈不会，因此直连时会报
`unable to get local issuer certificate`（证书验证失败）。

本工具在**不关闭证书验证**的前提下解决此问题：验证时同时信任三处来源——

1. 操作系统证书信任库（兼容公司内部根证书 / 代理）；
2. `certifi` 提供的公共根证书；
3. 随包内置的中间证书 `src/ircc_tracker/certs/ircc_api_intermediates.pem`。

第 3 项保证证书链在任何平台、即使离线也能补齐，无需依赖操作系统联网去补下载。
该额外信任配置仅应用于 IRCC API 域名，不影响 Cognito 或其他 HTTPS 连接。内置证书是公开的 CA 证书，不含任何隐私信息。

如果 IRCC 日后修复了服务器端的证书链配置，此内置证书将变为冗余，可安全移除。

## 测试

测试不会连接 IRCC，也不需要真实账户：

```bash
python -m unittest discover -s tests -v
```

## License

本项目采用 [MIT License](LICENSE)。
