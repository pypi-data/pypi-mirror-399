import json
import httpx
import sys
import time
from typing import AsyncGenerator, Dict, Any
from ..core import logger

def stream_generator_parser(base_url, payload, headers, timeout):
    tool_calls_buffer = {}
    final_tool_calls = None
    received_ids = {}
    tool_name_sent = set()
    reasoning_buffer = ""
    usage = None  # 新增：缓存 usage

    with httpx.stream("POST", f"{base_url}", json=payload, headers=headers, timeout=timeout) as response:

        if response.status_code != 200:
            logger.error(f"BaseAPI - 在发送请求时收到错误状态码：{response.status_code}，错误信息：{response.read()}，请求信息：{payload}")
            raise Exception(f"请求失败了，状态码：{response.status_code}, 错误信息：{response.read()}")

        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    # 新增：如果这条 data 包含 usage，就缓存
                    if "usage" in data:
                        usage = data["usage"]

                    for choice in data.get("choices", []):
                        delta = choice.get("delta", {})

                        if "content" in delta:
                            content = delta.get("content", "")
                            if content:
                                yield {"role": "assistant", "content": content}

                        if "reasoning_content" in delta:
                            reasoning_content = delta.get("reasoning_content", "")
                            if reasoning_content:
                                reasoning_buffer += reasoning_content
                                yield {
                                    "role": "assistant",
                                    "reasoning_content": reasoning_content,
                                    "content": ""
                                }

                        if "tool_calls" in delta:
                            for tool_call in delta["tool_calls"]:
                                index = tool_call["index"]

                                if index not in tool_calls_buffer:
                                    tool_calls_buffer[index] = {
                                        "index": index,
                                        "function": {"arguments": ""},
                                        "type": "",
                                        "id": ""
                                    }

                                if tool_call.get("id") and index not in received_ids:
                                    received_ids[index] = tool_call["id"]

                                current = tool_calls_buffer[index]
                                current["id"] = received_ids.get(index, "")
                                current["type"] = tool_call.get("type") or current["type"]

                                if tool_call.get("function"):
                                    func = tool_call["function"]
                                    current["function"]["name"] = (
                                        func.get("name") or current["function"].get("name", "")
                                    )

                                    if current["function"].get("name") and index not in tool_name_sent:
                                        tool_name_sent.add(index)
                                        yield {
                                            "role": "assistant",
                                            "content": "",
                                            "tool_name": current["function"]["name"]
                                        }

                                    if func.get("arguments") is not None:
                                        new_args = func.get("arguments", "")
                                        if new_args:
                                            current["function"]["arguments"] += new_args
                                            yield {
                                                "role": "assistant",
                                                "content": "",
                                                "tool_arguments": new_args,
                                                "tool_index": index
                                            }
                                    else:
                                        current["function"]["arguments"] += (
                                            func.get("arguments", "") if func.get("arguments") else ""
                                        )

                            final_tool_calls = [v for k, v in sorted(tool_calls_buffer.items())]

                except json.JSONDecodeError:
                    continue

        # 最后一次统一发出 tool_calls 和 usage
        if final_tool_calls or usage is not None:
            last = {
                "role": "assistant",
                "content": ""
            }
            if final_tool_calls:
                last["tool_calls"] = final_tool_calls
                last["id"] = final_tool_calls[0]["id"]
                logger.info(f"BaseAPI - 返回的最终工具调用信息：{final_tool_calls}")
            if usage is not None:
                logger.info(f"BaseAPI - 返回的usage信息：{usage}")
                last["usage"] = usage
            yield last


async def astream_generator_parser(
    base_url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    timeout: int
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    异步流式解析器，用于处理异步API调用返回的流式数据
    """
    tool_calls_buffer = {}
    final_tool_calls = None
    received_ids = {}
    tool_name_sent = set()
    reasoning_buffer = ""
    usage = None  # 新增：缓存 usage

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", f"{base_url}", json=payload, headers=headers, timeout=timeout) as response:
            if response.status_code != 200:
                logger.error(f"BaseAPI - 在发送请求时收到错误状态码：{response.status_code}，错误信息：{await response.aread()}，请求信息：{payload}")
                raise Exception(f"请求失败了，状态码：{response.status_code}")

            async for line in response.aiter_lines():
                line = line.strip()
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        # 新增：如果这条 data 包含 usage，就缓存
                        if "usage" in data:
                            usage = data["usage"]

                        for choice in data.get("choices", []):
                            delta = choice.get("delta", {})

                            if "content" in delta:
                                content = delta.get("content", "")
                                if content:
                                    yield {"role": "assistant", "content": content}

                            if "reasoning_content" in delta:
                                reasoning_content = delta.get("reasoning_content", "")
                                if reasoning_content:
                                    reasoning_buffer += reasoning_content
                                    yield {
                                        "role": "assistant",
                                        "reasoning_content": reasoning_content,
                                        "content": ""
                                    }

                            if "tool_calls" in delta:
                                for tool_call in delta["tool_calls"]:
                                    index = tool_call["index"]

                                    if index not in tool_calls_buffer:
                                        tool_calls_buffer[index] = {
                                            "index": index,
                                            "function": {"arguments": ""},
                                            "type": "",
                                            "id": ""
                                        }

                                    if tool_call.get("id") and index not in received_ids:
                                        received_ids[index] = tool_call["id"]

                                    current = tool_calls_buffer[index]
                                    current["id"] = received_ids.get(index, "")
                                    current["type"] = tool_call.get("type") or current["type"]

                                    if tool_call.get("function"):
                                        func = tool_call["function"]
                                        current["function"]["name"] = (
                                            func.get("name") or current["function"].get("name", "")
                                        )

                                        if current["function"].get("name") and index not in tool_name_sent:
                                            tool_name_sent.add(index)
                                            yield {
                                                "role": "assistant",
                                                "content": "",
                                                "tool_name": current["function"]["name"]
                                            }

                                        if func.get("arguments") is not None:
                                            new_args = func.get("arguments", "")
                                            if new_args:
                                                current["function"]["arguments"] += new_args
                                                yield {
                                                    "role": "assistant",
                                                    "content": "",
                                                    "tool_arguments": new_args,
                                                    "tool_index": index
                                                }
                                        else:
                                            current["function"]["arguments"] += (
                                                func.get("arguments", "") if func.get("arguments") else ""
                                            )

                                final_tool_calls = [v for k, v in sorted(tool_calls_buffer.items())]
                                
                    except json.JSONDecodeError:
                        continue

            # 最后一次统一发出 tool_calls 和 usage
            if final_tool_calls or usage is not None:
                last = {
                    "role": "assistant",
                    "content": ""
                }
                if final_tool_calls:
                    last["tool_calls"] = final_tool_calls
                    last["id"] = final_tool_calls[0]["id"]
                    logger.info(f"BaseAPI - 返回的最终工具调用信息：{final_tool_calls}")
                if usage is not None:
                    logger.info(f"BaseAPI - 返回的usage信息：{usage}")
                    last["usage"] = usage
                yield last



def process_result(result, max_tool_output_length=200):
    in_reasoning = False  # 是否处于推理中
    last_tool_name = ""   # 上一个工具名称
    tool_args_buffer = {} # 工具参数缓冲区

    for r in result:
        # -------- 推理内容 --------
        if "reasoning_content" in r:
            if not in_reasoning:
                print("\n🤔 ──── 开始推理 ────")
                in_reasoning = True
            print(r["reasoning_content"], end="", flush=True)
            continue

        # 结束推理状态
        if in_reasoning:
            print("\n😣 ──── 推理结束 ────\n")
            in_reasoning = False

        # -------- 工具启动 --------
        if "tool_name" in r:
            tool_name = r["tool_name"]
            last_tool_name = tool_name
            tool_args_buffer = {}  # 重置参数缓冲区

            if tool_name == "remember":
                print("\n📝 记忆已更新！")
                continue

            # 显示工具加载动画
            sys.stdout.write(f"\n🛠 正在执行工具：{tool_name}")
            sys.stdout.flush()
            for dot in [".", "..", "..."]:
                sys.stdout.write(f"\r🛠 正在执行工具：{tool_name}{dot}")
                sys.stdout.flush()
                time.sleep(0.3)
            print()

        # -------- 工具参数流式更新 --------
        elif "tool_arguments" in r:
            tool_index = r.get("tool_index", 0)
            if tool_index not in tool_args_buffer:
                tool_args_buffer[tool_index] = ""
            tool_args_buffer[tool_index] += r["tool_arguments"]
            
            if last_tool_name != "remember":
                # 实时显示工具参数构建过程
                args_so_far = tool_args_buffer[tool_index]
                sys.stdout.write(f"\r🔧 参数构建中：{args_so_far}")
                sys.stdout.flush()

        # -------- 工具参数 -------- (保持原有逻辑以兼容性)
        elif "tool_arguments" in r and "tool_index" not in r:
            if last_tool_name != "remember":
                print(f"🔧 参数：{r['tool_arguments']}")

        # -------- 工具结果 --------
        elif r.get("role") == "tool":
            if last_tool_name == "remember":
                continue
            content = r["content"]
            if len(content) > max_tool_output_length:
                preview = content[:max_tool_output_length].rstrip()
                print(f"✅ 工具结果（部分）：\n{preview}...\n🔽 内容过长（共 {len(content)} 字符）")
            else:
                print(f"✅ 工具结果：{content}")

        # -------- 普通内容 --------
        elif "content" in r and r["content"]:
            print(r["content"], end="")