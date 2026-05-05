#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 守护进程 - 持久的 RAG 查询服务
===================================
保持模型在内存中，通过 stdin/stdout 协议通信。
每个查询通过一行 JSON 请求触发，避免重复加载模型。

用法:
  python3 scripts/rag_daemon.py              # 启动服务
  echo '{"q":"HBM 项目"}' | python3 scripts/rag_daemon.py --oneshot  # 单次查询

集成到 OpenClaw:
  echo '{"q":"你的问题"}' | nc -U /tmp/rag_daemon.sock
  或通过 exec 调用: echo '{"q":"..."}' | python3 scripts/rag_daemon.py --oneshot
"""

import sys
import json
import os
import signal
import socket
import time
from pathlib import Path

# 将 RAG 包加入路径
RAG_DIR = Path(__file__).parent.parent / "memory/RAG"
sys.path.insert(0, str(RAG_DIR))

from retriever import HBMRetriever
from context_assembler import assemble_context, format_for_bootstrap
from processor import process_results
from cache import get_cache

SOCKET_PATH = "/tmp/rag_daemon.sock"


class RAGDaemon:
    """RAG 查询守护进程"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.retriever = None
        self.cache = get_cache()
    
    def _ensure_model(self):
        """确保模型已加载（只加载一次）"""
        if self.retriever is None:
            if self.debug:
                print("[RAG] 首次加载模型...", file=sys.stderr)
            self.retriever = HBMRetriever()
            if self.debug:
                print("[RAG] 模型加载完成", file=sys.stderr)
    
    def query(self, text: str, limit: int = 5, fmt: str = "context") -> str:
        """执行查询，返回字符串结果"""
        self._ensure_model()
        
        # 检查缓存
        cached = self.cache.get(text, limit)
        if cached:
            results = cached
        else:
            results = self.retriever.retrieve(text, limit)
            self.cache.set(text, limit, results)
        
        if not results:
            return json.dumps({"found": False, "results": []})
        
        if fmt == "json":
            output = []
            for r in results:
                output.append({
                    "source": r.get("source"),
                    "score": round(r.get("score", 0), 3),
                    "method": " / ".join(r.get("methods", [r.get("method", "unknown")])),
                    "content": r.get("content", "")[:300],
                    "metadata": r.get("metadata", {})
                })
            return json.dumps({"found": True, "results": output}, ensure_ascii=False)
        
        elif fmt == "bootstrap":
            return format_for_bootstrap(results, text)
        
        else:  # context
            return assemble_context(results, text)
    
    def handle_request(self, request: dict) -> str:
        """处理单次请求"""
        action = request.get("action", "query")
        
        if action == "query":
            text = request.get("q", "")
            limit = request.get("limit", 5)
            fmt = request.get("fmt", "context")
            return self.query(text, limit, fmt)
        
        elif action == "cache_stats":
            return json.dumps(self.cache.stats())
        
        elif action == "cache_clear":
            self.cache.clear()
            return json.dumps({"status": "ok"})
        
        elif action == "ping":
            return json.dumps({"status": "ok"})
        
        else:
            return json.dumps({"error": f"unknown action: {action}"})
    
    def run_socket(self):
        """通过 Unix socket 提供服务"""
        self._ensure_model()
        
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(5)
        os.chmod(SOCKET_PATH, 0o666)
        
        print(f"[RAG 守护进程] 启动 - socket: {SOCKET_PATH}", file=sys.stderr)
        print(f"[RAG 守护进程] 模型已加载，等待查询...", file=sys.stderr)
        
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(65536)
                if not data:
                    conn.close()
                    continue
                
                try:
                    request = json.loads(data.decode("utf-8"))
                    response = self.handle_request(request)
                    conn.sendall(response.encode("utf-8"))
                except json.JSONDecodeError:
                    conn.sendall(json.dumps({"error": "invalid JSON"}).encode("utf-8"))
                except Exception as e:
                    conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
                
                conn.close()
            
            except KeyboardInterrupt:
                print("\n[RAG 守护进程] 关闭", file=sys.stderr)
                break
        
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
    
    def run_oneshot(self):
        """单次查询模式（通过 stdin）"""
        data = sys.stdin.read()
        if not data:
            print(json.dumps({"error": "no input"}))
            return
        
        try:
            request = json.loads(data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "invalid JSON"}))
            return
        
        result = self.handle_request(request)
        print(result)


def main():
    daemon = RAGDaemon(debug=True)
    
    if "--oneshot" in sys.argv:
        daemon.run_oneshot()
    else:
        daemon.run_socket()


if __name__ == "__main__":
    main()
