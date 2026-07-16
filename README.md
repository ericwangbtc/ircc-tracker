# IRCC Tracker Local

一个只在本机运行的 Python 命令行工具，用于查询你自己的 IRCC Application Status Tracker 数据。

它直接连接：

- IRCC 使用的 AWS Cognito 登录服务；
- IRCC Application Status Tracker API。

密码、ID Token 和 Refresh Token 只存在于当前 Python 进程的内存中，不会写入磁盘。工具不会关闭 TLS 验证，也不会将数据发送到第三方服务器。

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
- HTTPS 证书验证保持开启。
- 请求超时默认为 30 秒。
- 建议手动、低频查询，不要高频轮询。

## 测试

测试不会连接 IRCC，也不需要真实账户：

```bash
python -m unittest discover -s tests -v
```

## License

本项目采用 [MIT License](LICENSE)。
