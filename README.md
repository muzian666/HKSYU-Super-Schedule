# 超级课程表 — MkDocs 课程评价平台

基于 MkDocs + Material 主题构建的课程评价平台，使用 GitBook 风格的自定义 CSS。适用于任何高校的课程评价信息展示。

## 部署前需要配置的内容

以下文件包含占位信息，部署前请替换为你自己的内容：

| 文件 | 需要修改的内容 |
|------|---------------|
| `mkdocs.yml` | `site_name`、`site_description`、`site_url`、`logo`/`favicon` 路径、`nav` 外部链接 |
| `docs/assets/images/` | 放入你自己的 `logo.png` 和 `favicon.png`（或修改 `mkdocs.yml` 中的文件名） |
| `docs/assets/javascripts/extra.js` | `internalHosts` 数组中添加你的域名 |
| `docs/index.md` | 首页内容、小程序二维码、评价提交链接 |
| `k8s/deployment.yaml` | ICP 备案号（`ICP_NUMBER`）和 `ICP_CHINA_ONLY` |
| `k8s/ingress.yaml` | 域名、TLS secret 名称、资源名称 |
| `k8s/service.yaml` | 服务名称 |
| `docs/` 各院系目录 | 替换为你自己的课程评价数据 |

### ICP 备案号配置

ICP 备案号通过环境变量注入，支持仅对中国大陆 IP 显示：

```yaml
# k8s/deployment.yaml
env:
  - name: ICP_NUMBER
    value: "你的ICP备案号"    # 留空则不显示
  - name: ICP_CHINA_ONLY
    value: "true"             # true = 仅大陆 IP 显示
```

## 供稿方式

### 方式一：问卷提交

在 `docs/index.md` 中放入你自己的评价问卷链接。

### 方式二：GitHub Pull Request

Fork 本仓库，按以下格式创建或编辑课程文件，然后提交 Pull Request。

#### 新增课程

在 `docs/<系别>/` 目录下创建 `<课程编号小写>.md` 文件，内容如下：

```markdown
# COURSE_CODE - English Name

<div class="gb-update-time">最后更新于：YYYY-MM-DD</div>

## 课程基本信息

| 字段 | 内容 |
|------|------|
| 课程编号 | COURSE_CODE |
| 课程名称 | English Name |
| 中文名称 | 中文名称 |
| 所属类型 | 系内选修/系外选修 |
| 任课老师 | 老师姓名 |
| 老师上课使用的语言 | 英语/粤语/普通话 |

## 综合信息

| 评价人数 | 平价评分 | SD (σ) |
|----------|----------|--------|
| 1 | ★★★★★ (5 / 5) | <span class="sd-tip">NaN<span class="sd-tip-content"><strong>公式：</strong> σ = √[ Σ(x<sub>i</sub> − μ)² / N ]<br><strong>说明：</strong>仅 1 条评价，无法计算标准差</span></span> |

## 评价

---

### YYYY-MM-DD

<div class="review-card">
<table class="review-meta-table">
<tr><td class="meta-label">评价人</td><td>你的昵称</td></tr>
<tr><td class="meta-label">成绩</td><td>你获得的成绩</td></tr>
<tr><td class="meta-label">总体评价</td><td>★★★★★ (5 / 5)</td></tr>
</table>
<div class="review-content">

你的评价内容写在这里。

</div>
</div>
```

> **评分说明**：使用 1-5 颗星，对应 `★` 到 `★★★★★`，括号内写 `(N / 5)`。

#### 给已有课程追加评价

打开对应的 `.md` 文件，在 `## 评价` 部分末尾追加新的评价块（从 `---` 开始），同时更新「综合信息」表中的评价人数和平均评分。

完成后还需更新 `docs/<系别>/index.md` 课程列表中的评分（如果评分有变化）。

## 本地部署

### 前置要求

- Python 3.10+
- pip

```bash
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
```

### 方式一：Python 本地运行

```bash
# 构建
mkdocs build

# 本地预览（开发模式，支持热重载）
mkdocs serve -a 127.0.0.1:8000
```

构建产物在 `site/` 目录下，可使用任意 HTTP 服务器托管：

```bash
cd site/ && python3 -m http.server 8080
```

### 方式二：Docker / Podman

```bash
# 构建镜像
docker build -t course-review .

# 运行（不带 ICP 备案号）
docker run -d -p 8080:8080 course-review

# 运行（带 ICP 备案号）
docker run -d -p 8080:8080 \
  -e ICP_NUMBER="京ICP备XXXXXXXX号" \
  -e ICP_CHINA_ONLY=true \
  course-review
```

访问 http://localhost:8080

### 方式三：Kubernetes

```bash
# 构建并推送镜像（替换为你的 registry）
docker build -t your-registry/course-review:latest .
docker push your-registry/course-review:latest

# 部署（请先修改 k8s/ 中的域名和配置）
kubectl apply -f k8s/
```

## 项目结构

```
├── mkdocs.yml                  # MkDocs 主配置
├── Containerfile               # Docker 多阶段构建
├── entrypoint.sh               # 容器启动脚本（envsubst 替换环境变量）
├── nginx.conf                  # Nginx 配置
├── k8s/                        # Kubernetes 部署配置
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── docs/                       # 站点内容（Markdown）
│   ├── index.md                # 首页
│   ├── assets/
│   │   ├── stylesheets/extra.css   # GitBook 风格 CSS
│   │   ├── javascripts/
│   │   │   ├── site-config.js      # 环境变量占位（运行时替换）
│   │   │   └── extra.js            # 外部链接拦截、ICP 备案号、Tooltip
│   │   └── images/
│   ├── soc/                    # 示例：社会系课程
│   └── ...                     # 其他院系
└── overrides/                  # MkDocs 主题覆盖模板
```

## License

MIT License — Copyright (c) 2022-present
