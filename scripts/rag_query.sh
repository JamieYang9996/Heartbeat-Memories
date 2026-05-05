#!/usr/bin/env bash
# RAG 查询助手 - 在 OpenClaw 对话中调用
# 用法: ./scripts/rag_query.sh <查询词>
# 示例: ./scripts/rag_query.sh HBM 项目 目标

SOCKET="/tmp/rag_daemon.sock"

if [ ! -S "$SOCKET" ]; then
    echo "⚠️ RAG 守护进程未运行，正在启动..."
    cd /home/admin/.openclaw/workspace
    nohup python3 scripts/rag_daemon.py > /tmp/rag_daemon.log 2>&1 &
    sleep 10
    if [ ! -S "$SOCKET" ]; then
        echo "❌ 启动失败，请检查日志: /tmp/rag_daemon.log"
        exit 1
    fi
    echo "✅ RAG 守护进程已启动"
fi

QUERY="$*"
if [ -z "$QUERY" ]; then
    echo "❌ 请提供查询词"
    echo "用法: ./scripts/rag_query.sh <查询词>"
    exit 1
fi

# 构建 JSON 请求，使用 bootstrap 格式（精简）
echo "{\"q\":\"$QUERY\",\"limit\":3,\"fmt\":\"bootstrap\"}" | nc -U "$SOCKET" 2>/dev/null

# 如果 socket 通信失败，回退到 oneshot 模式
if [ $? -ne 0 ]; then
    echo "⚠️ Socket 通信失败，使用单次查询模式..."
    echo "{\"q\":\"$QUERY\",\"limit\":3,\"fmt\":\"bootstrap\"}" | python3 /home/admin/.openclaw/workspace/scripts/rag_daemon.py --oneshot 2>/dev/null
fi
