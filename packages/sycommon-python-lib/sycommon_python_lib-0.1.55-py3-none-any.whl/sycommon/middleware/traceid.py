import json
import re
from typing import Dict, Any
from fastapi import Request, Response
from sycommon.logging.kafka_log import SYLogger
from sycommon.tools.merge_headers import merge_headers
from sycommon.tools.snowflake import Snowflake


def setup_trace_id_handler(app):
    @app.middleware("http")
    async def trace_id_and_log_middleware(request: Request, call_next):
        # ========== 1. 请求阶段：确保获取/生成 x-traceId-header ==========
        # 优先从请求头读取（兼容任意大小写）
        trace_id = request.headers.get(
            "x-traceId-header") or request.headers.get("x-traceid-header")
        # 无则生成雪花ID
        if not trace_id:
            trace_id = Snowflake.id

        # 设置 trace_id 到日志上下文
        token = SYLogger.set_trace_id(trace_id)
        header_token = SYLogger.set_headers(request.headers.raw)

        # 获取请求参数
        query_params = dict(request.query_params)
        request_body: Dict[str, Any] = {}
        files_info: Dict[str, str] = {}

        json_content_types = [
            "application/json",
            "text/plain;charset=utf-8",
            "text/plain"
        ]
        content_type = request.headers.get("content-type", "").lower()
        is_json_content = any(ct in content_type for ct in json_content_types)

        if is_json_content and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 兼容纯文本格式的 JSON（先读文本再解析）
                if "text/plain" in content_type:
                    raw_text = await request.text(encoding="utf-8")
                    request_body = json.loads(raw_text)
                else:
                    # application/json 直接解析
                    request_body = await request.json()
            except Exception as e:
                try:
                    request_body = await request.json()
                except Exception as e:
                    # 精准捕获 JSON 解析错误（而非泛 Exception）
                    request_body = {"error": f"JSON parse failed: {str(e)}"}

        elif "multipart/form-data" in content_type and request.method in ["POST", "PUT"]:
            try:
                # 从请求头中提取boundary
                boundary = None
                if "boundary=" in content_type:
                    boundary = content_type.split("boundary=")[1].strip()
                    boundary = boundary.encode('ascii')

                if boundary:
                    # 读取原始请求体
                    body = await request.body()

                    # 尝试从原始请求体中提取文件名
                    parts = body.split(boundary)
                    for part in parts:
                        part_str = part.decode('utf-8', errors='ignore')

                        # 使用正则表达式查找文件名
                        filename_match = re.search(
                            r'filename="([^"]+)"', part_str)
                        if filename_match:
                            field_name_match = re.search(
                                r'name="([^"]+)"', part_str)
                            field_name = field_name_match.group(
                                1) if field_name_match else "unknown"
                            filename = filename_match.group(1)
                            files_info[field_name] = filename
            except Exception as e:
                request_body = {
                    "error": f"Failed to process form data: {str(e)}"}

        # 构建请求日志（包含 traceId）
        request_message = {
            "traceId": trace_id,  # 请求日志中加入 traceId
            "method": request.method,
            "url": str(request.url),
            "query_params": query_params,
            "request_body": request_body,
            "uploaded_files": files_info if files_info else None
        }
        request_message_str = json.dumps(request_message, ensure_ascii=False)
        SYLogger.info(request_message_str)

        try:
            # 处理请求
            response = await call_next(request)

            # 获取响应Content-Type（统一小写）
            content_type = response.headers.get("content-type", "").lower()

            # ========== 2. SSE 响应：仅设置 x-traceId-header，不修改其他头 ==========
            if "text/event-stream" in content_type:
                try:
                    # 强制写入 x-traceId-header 到响应头
                    response.headers["x-traceId-header"] = trace_id
                    # 确保前端能读取（仅补充暴露头，不覆盖原有值）
                    expose_headers = response.headers.get(
                        "access-control-expose-headers", "")
                    if expose_headers:
                        if "x-traceId-header" not in expose_headers.lower():
                            response.headers[
                                "access-control-expose-headers"] = f"{expose_headers}, x-traceId-header"
                    else:
                        response.headers["access-control-expose-headers"] = "x-traceId-header"
                    # SSE 必须移除 Content-Length（仅这一个额外操作）
                    headers_lower = {
                        k.lower(): k for k in response.headers.keys()}
                    if "content-length" in headers_lower:
                        del response.headers[headers_lower["content-length"]]
                except AttributeError:
                    # 流式响应头只读：初始化时仅加入 traceId 和必要暴露头
                    new_headers = dict(response.headers) if hasattr(
                        response.headers, 'items') else {}
                    new_headers["x-traceId-header"] = trace_id  # 强制加入
                    # 保留原有暴露头，补充 traceId
                    if "access-control-expose-headers" in new_headers:
                        if "x-traceId-header" not in new_headers["access-control-expose-headers"].lower():
                            new_headers["access-control-expose-headers"] += ", x-traceId-header"
                    else:
                        new_headers["access-control-expose-headers"] = "x-traceId-header"
                    # 移除 Content-Length
                    new_headers.pop("content-length", None)
                    response.init_headers(new_headers)
                return response

            # ========== 3. 非 SSE 响应：强制写入 x-traceId-header，保留 CORS ==========
            # 备份 CORS 头（防止丢失）
            cors_headers = {}
            cors_header_keys = [
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers",
                "access-control-expose-headers",
                "access-control-allow-credentials",
                "access-control-max-age"
            ]
            for key in cors_header_keys:
                for k in response.headers.keys():
                    if k.lower() == key:
                        cors_headers[key] = response.headers[k]
                        break

            # 合并 headers（非 SSE 场景）
            merged_headers = merge_headers(
                source_headers=request.headers,
                target_headers=response.headers,
                keep_keys=None,
                delete_keys={'content-length', 'accept', 'content-type'}
            )

            # 强制加入 x-traceId-header（优先级最高）
            merged_headers["x-traceId-header"] = trace_id
            # 恢复 CORS 头 + 补充 traceId 到暴露头
            merged_headers.update(cors_headers)
            expose_headers = merged_headers.get(
                "access-control-expose-headers", "")
            if expose_headers:
                if "x-traceId-header" not in expose_headers.lower():
                    merged_headers["access-control-expose-headers"] = f"{expose_headers}, x-traceId-header"
            else:
                merged_headers["access-control-expose-headers"] = "x-traceId-header"

            # 更新响应头
            if hasattr(response.headers, 'clear'):
                response.headers.clear()
                for k, v in merged_headers.items():
                    response.headers[k] = v
            elif hasattr(response, "init_headers"):
                response.init_headers(merged_headers)
            else:
                for k, v in merged_headers.items():
                    try:
                        response.headers[k] = v
                    except (AttributeError, KeyError):
                        pass

            # 处理普通响应体（JSON 加入 traceId）
            response_body = b""
            try:
                async for chunk in response.body_iterator:
                    response_body += chunk

                # 获取 Content-Disposition（统一小写）
                content_disposition = response.headers.get(
                    "content-disposition", "").lower()

                # JSON 响应体加入 traceId
                if "application/json" in content_type and not content_disposition.startswith("attachment"):
                    try:
                        data = json.loads(response_body)
                        new_body = response_body
                        if data:
                            data["traceId"] = trace_id  # 响应体也加入
                            new_body = json.dumps(
                                data, ensure_ascii=False).encode()

                        # 重建响应，确保 header 包含 x-traceId-header
                        response = Response(
                            content=new_body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )
                        response.headers["content-length"] = str(len(new_body))
                        response.headers["x-traceId-header"] = trace_id  # 再次兜底
                        # 恢复 CORS 头
                        for k, v in cors_headers.items():
                            response.headers[k] = v
                    except json.JSONDecodeError:
                        # 非 JSON 响应：仅更新长度，强制加入 traceId
                        response = Response(
                            content=response_body,
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )
                        response.headers["content-length"] = str(
                            len(response_body))
                        response.headers["x-traceId-header"] = trace_id  # 强制加入
                        for k, v in cors_headers.items():
                            response.headers[k] = v
                else:
                    # 非 JSON 响应：强制加入 traceId
                    response = Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )
                    response.headers["content-length"] = str(
                        len(response_body))
                    response.headers["x-traceId-header"] = trace_id  # 强制加入
                    for k, v in cors_headers.items():
                        response.headers[k] = v
            except StopAsyncIteration:
                pass

            # 构建响应日志（包含 traceId）
            response_message = {
                "traceId": trace_id,  # 响应日志加入 traceId
                "status_code": response.status_code,
                "response_body": response_body.decode('utf-8', errors='ignore'),
            }
            response_message_str = json.dumps(
                response_message, ensure_ascii=False)
            SYLogger.info(response_message_str)

            # ========== 最终兜底：确保响应头必有 x-traceId-header ==========
            try:
                response.headers["x-traceId-header"] = trace_id
            except AttributeError:
                new_headers = dict(response.headers) if hasattr(
                    response.headers, 'items') else {}
                new_headers["x-traceId-header"] = trace_id
                if hasattr(response, "init_headers"):
                    response.init_headers(new_headers)

            return response
        except Exception as e:
            # 异常日志也加入 traceId
            error_message = {
                "traceId": trace_id,
                "error": str(e),
                "query_params": query_params,
                "request_body": request_body,
                "uploaded_files": files_info if files_info else None
            }
            error_message_str = json.dumps(error_message, ensure_ascii=False)
            SYLogger.error(error_message_str)
            raise
        finally:
            # 清理上下文变量
            SYLogger.reset_trace_id(token)
            SYLogger.reset_headers(header_token)

    return app
