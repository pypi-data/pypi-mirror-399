#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频批量生成脚本
"""

import os
import sys
import time
import argparse
import logging
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def replace_roles(text: str, roles: dict) -> str:
    """替换提示词中的 @角色名 为角色值"""
    if not isinstance(text, str):
        return text
    
    # 匹配 @ 后面跟着的英文字母，直到遇到非英文字母字符
    pattern = r'@([A-Za-z]+)'
    
    def replacer(match):
        role_name = match.group(1)
        if role_name in roles:
            return "@" + roles[role_name]
        else:
            # 未找到映射，保持原样但记录警告
            logger.warning(f"未找到角色映射: @{role_name}")
            return match.group(0)
    
    return re.sub(pattern, replacer, text)


def check_role_mappings(tasks: list, roles: dict) -> bool:
    """检查所有任务的角色映射是否完整"""
    missing_roles = set()
    
    for task in tasks:
        prompt = task.get('提示词', '')
        if not isinstance(prompt, str):
            continue
            
        # 找出所有 @角色名（只提取英文字母部分）
        pattern = r'@([A-Za-z]+)'
        role_names = re.findall(pattern, prompt)
        
        for role_name in role_names:
            if role_name not in roles:
                missing_roles.add(role_name)
    
    if missing_roles:
        logger.error("=" * 60)
        logger.error("错误：以下角色未在 角色 sheet中定义：")
        for role in sorted(missing_roles):
            logger.error(f"  - @{role}")
        logger.error("=" * 60)
        return False
    
    return True


def load_excel(excel_path: str):
    """加载Excel文件"""
    logger.info(f"读取Excel: {excel_path}")
    
    # 读取任务
    tasks_df = pd.read_excel(excel_path, sheet_name='任务')
    tasks = tasks_df.to_dict('records')
    logger.info(f"读取到 {len(tasks)} 个任务")
    
    # 读取角色
    try:
        roles_df = pd.read_excel(excel_path, sheet_name='角色')
        roles = dict(zip(roles_df['角色名'].astype(str), roles_df['角色值'].astype(str)))
        logger.info(f"读取到 {len(roles)} 个角色")
        
        # 显示角色映射
        logger.info("角色映射:")
        for role_name, role_value in roles.items():
            logger.info(f"  @{role_name} → {role_value}")
            
    except Exception as e:
        roles = {}
        logger.warning(f"未找到角色sheet或读取失败: {e}")
    
    return tasks, roles


def generate_video(api_url: str, api_key: str, output_dir: Path, job: dict) -> tuple:
    """生成单个视频"""
    task_id = str(job['编号']).strip()
    index = job['index']
    
    # 输出文件名
    filename = f"{task_id}_{index:03d}.mp4"
    output_path = output_dir / filename
    
    # 如果已存在则跳过
    if output_path.exists():
        return True, f"已存在: {filename}", None
    
    try:
        # 准备请求
        files = {
            'prompt': (None, job['提示词']),
            'model': (None, job.get('model', 'sora-2')),
            'seconds': (None, str(job.get('时长', 5))),
            'size': (None, job.get('尺寸', '1920x1080'))
        }
        
        # 图生视频：添加图片
        image_path = job.get('图片')
        if image_path and os.path.exists(str(image_path)):
            with open(image_path, 'rb') as f:
                files['input_reference'] = (os.path.basename(image_path), f.read())
        
        headers = {'Authorization': f'Bearer {api_key}'}
        
        logger.info(f"生成 {filename}: {job['提示词'][:50]}...")
        
        # 调用API
        response = requests.post(api_url, files=files, headers=headers, timeout=600)
        response.raise_for_status()
        result = response.json()
        
        # 获取视频URL
        video_url = None
        if result.get('data') and len(result['data']) > 0:
            video_url = result['data'][0].get('url')
        
        if not video_url:
            return False, f"未获取到URL: {filename}", None
        
        # 下载视频
        video_response = requests.get(video_url, timeout=300)
        video_response.raise_for_status()
        
        # 保存
        with open(output_path, 'wb') as f:
            f.write(video_response.content)
        
        return True, f"成功: {filename}", str(output_path)
        
    except Exception as e:
        return False, f"失败: {filename} - {str(e)}", None


def create_jobs(tasks: list, roles: dict, mode: str) -> list:
    """创建任务列表"""
    jobs = []
    
    for task in tasks:
        # 基础信息
        task_id = str(task.get('编号', '')).strip()
        prompt = str(task.get('提示词', '')).strip()
        count = int(task.get('生成数量', 1))
        
        # 替换角色
        prompt = replace_roles(prompt, roles)
        
        # 生成多个job
        for i in range(count):
            job = {
                '编号': task_id,
                'index': i + 1,
                '提示词': prompt,
                '时长': int(task.get('时长', 5)),
                '尺寸': str(task.get('尺寸', '1920x1080')).strip(),
                '图片': task.get('图片'),
                'model': 'sora-2'
            }
            jobs.append(job)
    
    # 根据模式排序
    if mode == 'balanced':
        # 均衡模式：按index排序，让不同任务交替进行
        jobs.sort(key=lambda x: (x['index'], x['编号']))
    else:
        # 顺序模式：按编号排序
        jobs.sort(key=lambda x: (x['编号'], x['index']))
    
    return jobs


def main():
    parser = argparse.ArgumentParser(description='批量视频生成工具')
    parser.add_argument('excel_path', help='Excel文件路径')
    parser.add_argument('--api-url', default='http://localhost:9200/v1/videos',
                        help='API地址 (默认: http://localhost:9200/v1/videos)')
    parser.add_argument('--api-key', default='han1234',
                        help='API密钥 (默认: han1234)')
    parser.add_argument('--output-dir', default='视频生成结果',
                        help='输出目录 (默认: 视频生成结果)')
    parser.add_argument('--workers', type=int, default=10,
                        help='并发数 (默认: 10)')
    parser.add_argument('--interval', type=float, default=1.0,
                        help='新任务间隔秒数 (默认: 1.0)')
    parser.add_argument('--mode', choices=['balanced', 'sequential'],
                        default='balanced',
                        help='执行模式 (默认: balanced)')
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.excel_path):
        logger.error(f"文件不存在: {args.excel_path}")
        sys.exit(1)
    
    # 加载Excel
    tasks, roles = load_excel(args.excel_path)
    
    if not tasks:
        logger.error("没有任务")
        sys.exit(1)
    
    # 检查角色映射
    logger.info("检查角色映射...")
    if not check_role_mappings(tasks, roles):
        sys.exit(1)
    
    logger.info("✓ 所有角色映射完整")
    
    # 创建任务列表
    jobs = create_jobs(tasks, roles, args.mode)
    total = len(jobs)
    
    logger.info(f"共 {len(tasks)} 个任务配置，展开为 {total} 个生成任务")
    logger.info(f"模式: {args.mode}, 并发: {args.workers}, 间隔: {args.interval}s")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 统计
    success = 0
    skipped = 0
    failed = 0
    
    # 并发执行
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        
        for job in jobs:
            time.sleep(args.interval)  # 间隔
            
            future = executor.submit(
                generate_video,
                args.api_url,
                args.api_key,
                output_dir,
                job
            )
            futures[future] = job
        
        # 处理结果
        for future in as_completed(futures):
            job = futures[future]
            ok, msg, path = future.result()
            
            if ok:
                if "已存在" in msg:
                    skipped += 1
                else:
                    success += 1
                logger.info(f"✓ [{success + skipped}/{total}] {msg}")
            else:
                failed += 1
                logger.error(f"✗ [{success + skipped + failed}/{total}] {msg}")
    
    # 总结
    logger.info("=" * 60)
    logger.info(f"完成! 成功: {success}, 跳过: {skipped}, 失败: {failed}")
    logger.info(f"输出目录: {args.output_dir}")
    logger.info("=" * 60)
    
    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()