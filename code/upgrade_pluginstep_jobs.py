#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
合并脚本：从 Jenkins 拉取所有 Job 名称(alljobs),
以及从 Amamba 插件接口拉取作业选项(plugins_jobs).
最后计算差集: alljobs、plugins_jobs

依赖：
- jenkinsapi  (pip install jenkinsapi)
- requests    (pip install requests)

作者: Weibing.Ma
"""

import json
import re
import sys
import yaml
from typing import List, Dict


# 第1部分：Jenkins
try:
    from jenkinsapi.jenkins import Jenkins
except Exception as e:
    Jenkins = None  # 允许在没有 jenkinsapi 的环境下查看脚本
    print("警告：未能导入 jenkinsapi,请确认已安装该库。错误：", e, file=sys.stderr)

# 第2部分：HTTP 请求
import requests
import urllib3

# 可选：禁用自签名证书警告（如果你的接口是自签名证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# -------------------------
# Jenkins: 获取所有 Job 名称
# -------------------------
def get_jenkins_all_jobs(jenkins_url: str, username: str, password: str, timeout: int = 15) -> List[str]:
    """
    从 Jenkins 获取所有 Job 名称。

    :param jenkins_url: Jenkins 服务器 URL
    :param username: Jenkins 用户名
    :param password: Jenkins 密码或 API Token
    :param timeout: 连接超时秒数
    :return: 字符串列表(Job 名称）
    """
    if Jenkins is None:
        raise RuntimeError("jenkinsapi 未安装或导入失败，无法连接 Jenkins。")

    # jenkinsapi 不提供 requests 的超时参数；这里主要确保 URL 合理
    jenkins = Jenkins(jenkins_url, username=username, password=password)
    jobs_iter = jenkins.get_jobs()  # 生成器：yield (name, Job)
    names = []
    for name, _job in jobs_iter:
        if name:
            names.append(str(name))
    return names


# --------------------------------------
# Amamba 插件接口：获取 plugins_jobs 列表
# --------------------------------------
def get_plugins_jobs(url: str, token: str, verify_ssl: bool = False, timeout: int = 15) -> List[str]:
    """
    调用 Amamba 插件接口，解析 spec.parameters[*].validateConfig.options[*].label

    :param url: 插件版本 API URL
    :param token: Bearer Token
    :param verify_ssl: 是否校验证书（自签名可设为 False)
    :param timeout: 请求超时秒数
    :return: 字符串列表(label)
    """
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=timeout)
    resp.raise_for_status()

    data = resp.json()

    # 如果存在 raw 字段则删除（避免冗余）
    if isinstance(data, dict) and "raw" in data:
        del data["raw"]

    # 解析 label 列表
    labels = []
    spec = data.get("spec", {})
    parameters = spec.get("parameters", [])
    for param in parameters:
        options = param.get("validateConfig", {}).get("options", [])
        for opt in options:
            label = opt.get("label")
            if label:
                labels.append(str(label))

    return labels


def replace_parameters_key(data):
    """
    递归替换 dict/list 中的 'parameters' → 'params'
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = "params" if key == "parameters" else key
            new_dict[new_key] = replace_parameters_key(value)
        return new_dict

    elif isinstance(data, list):
        return [replace_parameters_key(i) for i in data]

    return data


def get_plugins_jobs_data(url: str, token: str, verify_ssl: bool = False, timeout: int = 15) -> List[str]:
    """
    调用 Amamba 插件接口，解析 spec.parameters[*].validateConfig.options[*].label

    :param url: 插件版本 API URL
    :param token: Bearer Token
    :param verify_ssl: 是否校验证书（自签名可设为 False)
    :param timeout: 请求超时秒数
    :return: 字符串列表(label)
    """
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=timeout)
    resp.raise_for_status()

    data = resp.json()

    # 如果存在 raw 字段则删除（避免冗余）
    if isinstance(data, dict) and "raw" in data:
        del data["raw"]

    # 替换 parameters → params
    params_data = replace_parameters_key(data=data)
    
    return params_data

    
def put_plugin_data(url: str, token: str, result: Dict, verify_ssl: bool = False, timeout: int = 15) -> Dict:
    """
    通用 PUT 请求函数，接收外部准备好的 result 字典。

    :param url: API URL
    :param token: Bearer Token
    :param result: PUT 请求体（你外部构造好的 dict）
    :param verify_ssl: 是否验证 SSL
    :param timeout: 超时时间
    :return: 返回 JSON 响应
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.put(
        url,
        headers=headers,
        json=result,        # 你已构造好的 dict
        verify=verify_ssl,
        timeout=timeout
    )

    # 不直接 raise，先输出服务器返回的错误内容
    if resp.status_code >= 400:
        print("\n==== 服务端返回的错误信息 ====")
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except:
            print(resp.text)
        print("================================\n")

        # 再抛出异常
        resp.raise_for_status()

    # resp.raise_for_status()
    return resp.json()


# ---------------
# 主流程入口
# ---------------
def main():
    # ===== 在此填入你的实际连接信息（建议改用环境变量或配置文件） =====
    # Jenkins
    JENKINS_URL = "http://ip:port"
    JENKINS_USERNAME = "username"
    JENKINS_PASSWORD = "password"

    # Amamba 插件接口
    PLUGIN_URL = "https://ip:port/apis/pipeline.amamba.io/v1alpha1/plugins/jobtask-joblist/versions/v1.0.0"
    BEARER_TOKEN = "token"
    # ===========================================================

    alljobs: List[str] = []
    plugins_jobs: List[str] = []

    try:
        print(">> 开始从 Jenkins 拉取全部 Job 名称 ...")
        alljobs = get_jenkins_all_jobs(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        # 去重
        alljobs = sorted(set(alljobs))
        print(f"Jenkins Job 数量: {len(alljobs)}")

    except Exception as e:
        print(f"[错误] 拉取 Jenkins Job 失败: {e}", file=sys.stderr)

    try:
        print(">> 开始从 Amamba 插件接口拉取自定义步骤中 Job 选项 ...")
        plugins_jobs = get_plugins_jobs(PLUGIN_URL, BEARER_TOKEN, verify_ssl=False)
        # 去重
        plugins_jobs = sorted(set(plugins_jobs))
        print(f"插件 Job 数量：{len(plugins_jobs)}")

    except Exception as e:
        print(f"[错误] 拉取插件 Job 失败：{e}", file=sys.stderr)

    # 差集：alljobs \ plugins_jobs
    jenkins_only = sorted(set(alljobs) - set(plugins_jobs))

    print("\n================ 结果汇总 ================")
    print(f"Jenkins 全部 Job(去重后): {len(alljobs)} 个")
    print(f"插件列出的 Job (去重后):{len(plugins_jobs)} 个")
    print(f"差集(Jenkins 独有，未出现在插件列表中）：{len(jenkins_only)} 个")
    print("Jenkins 独有的 Job =", jenkins_only)

    if not jenkins_only:
        print(">> 无需更新，插件自定义步骤已包含所有 Jenkins Job ...")
    else:
        try:
            print(">> 重构 Amamba 插件自定义步骤配置 ...")
            plugins_jobs_data = get_plugins_jobs_data(PLUGIN_URL, BEARER_TOKEN, verify_ssl=False)

            options_list = plugins_jobs_data["spec"]["params"][0]["validateConfig"]["options"]

            # 去重并统计 plugins_jobs_data 中总的 options 数量
            existing = {o["value"] for o in options_list}
            for item in jenkins_only:
                if item not in existing:
                    options_list.append({"label": item, "value": item})

            print(f"重构 Amamba 自定义步骤配置数：{len(options_list)} 个")

            # 转为 amamba_coustom_steps 的 YAML 为字符串
            yaml_str = yaml.safe_dump(plugins_jobs_data, sort_keys=False, allow_unicode=True)

            yaml_str_sort = re.sub(r"sort:\s*'(\d+)'", r"sort: \1", yaml_str)

            result = {
                'name': 'dominos-joblist',
                'version': 'v1.0.0',
                'data': yaml_str_sort
            }

            # 更新 amamba 插件自定义步骤中流水线列表
            put_plugin_data(PLUGIN_URL, BEARER_TOKEN, result, verify_ssl=False)

        except Exception as e:
            print(f"[错误] 重构步骤配置失败：{e}", file=sys.stderr)


    # 如需同时打印两个原始列表，可取消下面两行注释
    # print("alljobs =", alljobs)
    # print("plugins_jobs =", plugins_jobs)

    # 如需导出为 JSON 文件，可取消下面一段注释
    # result = {
    #     "alljobs": alljobs,
    #     "plugins_jobs": plugins_jobs,
    #     "jenkins_only": jenkins_only
    # }
    # with open("jobs_diff.json", "w", encoding="utf-8") as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    # print("已导出 jobs_diff.json")


if __name__ == "__main__":
    main()
