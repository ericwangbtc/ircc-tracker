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

启动后依次输入 UCI、Tracker 密码，并从账户中的申请列表选择要查询的申请：

```bash
ircc-tracker
```

查询结果以 JSON 显示在终端中。输出可能包含姓名、UCI、申请号和移民申请状态等隐私信息，请勿复制到公开位置。

## 安全说明

- 不支持通过命令行参数传入密码，避免密码进入 shell history。
- 不保存密码或令牌。
- UCI、密码和申请选择均通过交互方式输入。
- HTTPS 证书验证始终保持开启，同时信任操作系统证书库、certifi 根证书以及随包内置的中间证书（详见下方“TLS 证书”）。
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
该内置证书是公开的 CA 证书，不含任何隐私信息。

如果 IRCC 日后修复了服务器端的证书链配置，此内置证书将变为冗余，可安全移除。

## 测试

测试不会连接 IRCC，也不需要真实账户：

```bash
python -m unittest discover -s tests -v
```

## License

本项目采用 [MIT License](LICENSE)。
