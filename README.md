# HKSYU 超级课程表

> 香港树仁大学课程评价平台 — 由树仁学生共建

## 项目背景

本项目是香港树仁大学（HKSYU）的非官方课程评价平台，旨在帮助同学们在选课时有可参考的真实评价。所有评价均来自真实的学生经历，涵盖课程难度、给分情况、老师风格等维度。

由于缺少持续的评价供稿，原网站已暂停运营。现在将项目开源，希望树仁的同学们能够通过 GitHub Pull Request 的方式继续贡献评价，让这个平台持续为后来者提供参考。

## 快速运行

### 方式一：Python 本地运行

```bash
# 安装依赖
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin

# 本地预览（支持热重载）
mkdocs serve -a 127.0.0.1:8000

# 生产构建
mkdocs build
```

构建产物在 `site/` 目录下，可使用任意 HTTP 服务器托管：

```bash
cd site/ && python3 -m http.server 8080
```

### 方式二：Docker / Podman

```bash
# 构建镜像
docker build -t hksyu-super-schedule .

# 运行
docker run -d -p 8080:8080 hksyu-super-schedule

# 带 ICP 备案号运行（仅大陆 IP 可见）
docker run -d -p 8080:8080 \
  -e ICP_NUMBER="你的ICP备案号" \
  -e ICP_CHINA_ONLY=true \
  hksyu-super-schedule
```

### 方式三：Kubernetes

```bash
kubectl apply -f k8s/
```

> **注意**：部署前需修改 `k8s/ingress.yaml` 中的域名和 TLS 配置。ICP 备案号在 `k8s/deployment.yaml` 的 `env` 中配置。

## 供稿方式

### 方式一：问卷提交

填写 [评价问卷](https://wj.qq.com/s2/8669157/afbb/) 即可提交课程评价。

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
│   ├── bus/                    # 商学系
│   ├── chi/                    # 中文系
│   ├── comp/                   # 计算机系
│   ├── econ/                   # 经济系
│   ├── eng/                    # 英文系
│   ├── fin/                    # 金融系
│   ├── fren/                   # 法语系
│   ├── ge/                     # 通识课（GEA/GEB/GEC/GED）
│   ├── hist/                   # 历史系
│   ├── jour/                   # 新传系
│   ├── law/                    # 法律系
│   ├── mdit/                   # 媒体设计与虚拟现实科技
│   ├── pe/                     # 体育
│   ├── phil/                   # 哲学系
│   ├── pra/                    # 公共关系与广告
│   └── soc/                    # 社会系
└── overrides/                  # MkDocs 主题覆盖模板
```

## License

MIT License — Copyright (c) 2022-present HKSYU Students
