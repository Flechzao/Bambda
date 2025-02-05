# Bambda++

Bambda++ 是一个用于 Burp Suite 的 Python 插件，旨在通过选择 HTTP 方法、文件后缀、域名和关键字进行过滤，并自动生成相应的代码模板。相较于原生的“Convert to Bambda”功能，Bambda++ 更加贴近日常的安全测试需求。

## 特性

- **选择 HTTP 方法**：可以选择要过滤的 HTTP 方法（如 GET、POST、PUT、DELETE 等）。
- **文件后缀过滤**：支持常见文件后缀的过滤，如 `.js`、`.css`、`.png`、`.jpg`、`.html` 等。
- **域名过滤**：支持排除特定域名的请求。
- **关键字过滤**：支持仅查看和排除特定关键字的请求。
- **代码模板生成**：根据用户选择的过滤条件生成 Java 代码模板，便于后续使用。

## 安装

1. 从 [GitHub](https://github.com/Flechzao/Bambda) 页面下载插件的 JAR 文件。
2. 打开 Burp Suite。
3. 在 "Extender" -> "Extensions" 中点击 "Add" 按钮。
4. 选择 "Python" 作为扩展类型，并选择下载的插件文件。

## 使用说明

1. 在 Burp Suite 中打开 Bambda++ 插件。
2. 根据需要选择过滤条件：
   - 选择 HTTP 方法
   - 选择文件后缀
   - 输入要排除的域名
   - 输入要查看和排除的关键字
3. 点击“生成代码”按钮。
4. 查看生成的代码模板，并根据需要进行调整。

## 界面说明

- **HTTP 方法**: 选择要排除或包含的 HTTP 方法。
- **文件后缀**: 通过复选框选择要过滤的文件后缀，或在输入框中添加自定义后缀。
- **域名过滤**: 输入要排除的域名，多个域名用逗号分隔。
- **关键字过滤**: 输入要查看和排除的关键字，多个关键字用逗号分隔。
- **输出区域**: 生成的代码模板将在此处显示。


## 许可证

该项目遵循 [MIT 许可证](LICENSE)。


## 详细使用教程

可参考 Freebuf文章：https://www.freebuf.com/sectool/418254.html
