# Claude 测试文档

此文档用于测试 Claude Code 的脚本执行功能。

## 基础命令测试

```bash {"id": "echo-test", "title": "Echo 测试"}
echo "Hello Claude!"
echo "当前时间: $(date)"
echo "工作目录: $(pwd)"
```

## 系统信息

```bash {"id": "system-info", "title": "系统信息"}
echo "操作系统: $(uname -s)"
echo "主机名: $(hostname)"
echo "用户: $(whoami)"
```

## 文件操作

```bash {"id": "file-ops", "title": "文件操作"}
# 创建测试文件
echo "测试内容" > /tmp/claude-test.txt
cat /tmp/claude-test.txt
ls -la /tmp/claude-test.txt
rm /tmp/claude-test.txt
echo "文件操作完成"
```

## 环境变量

```bash {"id": "env-test", "title": "环境变量"}
echo "PATH 前5个路径:"
echo $PATH | tr ':' '\n' | head -5
echo ""
echo "SHELL: $SHELL"
echo "HOME: $HOME"
```

## 计算测试

```bash {"id": "calc-test", "title": "简单计算"}
echo "2 + 3 = $((2+3))"
echo "10 * 5 = $((10*5))"
echo "100 / 4 = $((100/4))"
```

## 网络测试

```bash {"id": "network-test", "title": "网络测试"}
echo "尝试连接 Google DNS..."
timeout 2 curl -s -o /dev/null -w "%{http_code}" https://8.8.8.8 || echo "网络不可用或超时"
```

## 进度演示

```bash {"id": "progress-demo", "title": "进度演示"}
for i in 1 2 3 4 5; do
    echo "进度: $i/5 - $(date +%H:%M:%S)"
    sleep 0.5
done
echo "完成!"
```

---

> **提示**: 点击右侧的 "▶" 按钮执行脚本，点击 "⏹" 停止执行。
