# HAL 官网

作者：Condy

HAL 相机的独立官网仓库。公开页面由 GitHub Pages 从 `master` 分支的 `/docs` 发布，无需安装依赖或配置后台。

## 公开页面

| 页面 | 简体中文 | English |
| --- | --- | --- |
| 技术支持 | [支持](https://yangkj.github.io/halcam/zh/support.html) | [Support](https://yangkj.github.io/halcam/en/support.html) |
| 隐私政策 | [隐私政策](https://yangkj.github.io/halcam/zh/privacy-policy.html) | [Privacy Policy](https://yangkj.github.io/halcam/en/privacy-policy.html) |
| 用户协议 | [用户协议](https://yangkj.github.io/halcam/zh/terms-of-service.html) | [Terms of Use](https://yangkj.github.io/halcam/en/terms-of-service.html) |

首页设计仍需最终审核，本次不发布根目录首页。请直接使用以上页面链接。

## 内容维护

- 隐私政策及用户协议的唯一正文源位于 HAL App 的 `Hal/Resources/Legal/`，网站导出相同正文；不要分别维护两套事实。
- 支持正文位于 `content/support.zh-Hans.md`、`content/support.en.md`。
- `docs/assets/pages.css` 是三个辅助页面的共用样式。
- 页面不使用第三方字体、分析或广告脚本。

在官网仓库目录更新并核对导出页面：

```sh
python3 tools/sync_pages.py ../Hal/Resources/Legal
python3 tools/sync_pages.py ../Hal/Resources/Legal --check
python3 tools/check_pages.py
```

检查静态页面后，将对应网页和样式一起提交。发布后分别核对中文、英文链接及正文。

## 本地审核

`preview/` 存放未批准的首页方向稿，已忽略，不属于本次公开页面。可直接在浏览器打开其中的 `index.html`，不依赖服务器。首页获批后再将确认的文件放入 `docs/`，连同引用资源单独提交；不要把整个预览目录强制加入当前提交。

如需通过本机服务器预览辅助页面：

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

然后打开 `http://127.0.0.1:4173/zh/support.html`，结束后按 `Ctrl+C` 停止。

## 发布设置

GitHub 仓库 **Settings → Pages** 使用 **Deploy from a branch**，分支选择 `master`，目录选择 `/docs`。源码推送后由 GitHub Pages 构建。当前不配置自定义域名。

发布只允许包含已授权的技术支持、隐私政策、用户协议及必要样式与维护工具。首页布局、交互和展示素材需用户最终审核，不能随本次发布进入远端。
