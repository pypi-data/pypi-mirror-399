#!/usr/bin/env python3
"""
生成变更日志的脚本
使用大语言模型根据git差异文件生成change log
"""

import argparse
import os
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class Config:
    """配置类"""
    api_key: str
    base_url: str
    diff_file: str
    language: str
    model: str
    prompt_file: str

class ChangeLogGenerator:
    """变更日志生成器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = self._init_openai_client()
    
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        try:
            # 尝试导入openai库
            import openai
            # 设置API配置
            openai.api_key = self.config.api_key
            openai.base_url = self.config.base_url.rstrip('/') + '/'
            
            # 创建客户端
            client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url.rstrip('/') + '/'
            )
            return client
        except ImportError:
            print("错误: 请安装openai库: pip install openai")
            sys.exit(1)
        except Exception as e:
            print(f"初始化OpenAI客户端失败: {e}")
            sys.exit(1)
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"错误: 文件未找到: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            sys.exit(1)
    
    def generate_changelog(self) -> str:
        """生成变更日志"""
        try:
            # 读取提示词和差异文件
            prompt_template = self.read_file(self.config.prompt_file)
            diff_content = self.read_file(self.config.diff_file)
            language = self.config.language
            
            if "{language}" in prompt_template:
                prompt_template = prompt_template.replace("{language}", language)
            
            # 将差异内容插入到提示词中
            # 假设提示词中包含 {diff} 占位符
            if "{diff}" in prompt_template:
                prompt_template = prompt_template.replace("{diff}", diff_content)
            else:
                # 如果没有占位符，直接将差异内容附加到提示词后
                prompt_template = f"{prompt_template}\n\n下面是git差异内容：\n\n{diff_content}"
            prompt = prompt_template
            # 调用大语言模型
            print(f"正在使用模型 {self.config.model} 生成变更日志...")
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的软件工程师，擅长分析代码变更并生成清晰、专业的变更日志。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            # 提取生成的变更日志
            changelog = response.choices[0].message.content.strip()
            
            return changelog
            
        except Exception as e:
            print(f"生成变更日志失败: {e}")
            sys.exit(1)
    
    def save_changelog(self, changelog: str, output_file: Optional[str] = None):
        """保存变更日志到文件"""
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(changelog)
                print(f"变更日志已保存到: {output_file}")
            except Exception as e:
                print(f"保存变更日志到文件失败: {e}")
        
        # 同时输出到控制台
        print("\n" + "="*80)
        print("生成的变更日志:")
        print("="*80)
        print(changelog)
        print("="*80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='根据git差异文件生成变更日志',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
%(prog)s  --apikey sk-xxx --baseurl https://api.openai.com/v1 --model gpt-4 \\
            --promptfile prompt.txt --diffile changes.diff

%(prog)s  --apikey sk-xxx --baseurl http://localhost:8080/v1 --model llama-2-7b \\
            --promptfile prompt.txt --diffile changes.diff --output changelog.md
        """
    )
    
    parser.add_argument(
        '--baseurl',
        required=True,
        help='API基础URL，例如: https://api.openai.com/v1'
    )
    
    parser.add_argument(
        '--apikey',
        required=True,
        help='API密钥'
    )
    
    parser.add_argument(
        '--model',
        required=True,
        help='模型名称，例如: gpt-4, gpt-3.5-turbo, llama-2-7b等'
    )
    
    parser.add_argument(
        '--language',
        required=True,
        default='zh-CN',
        help='输出语言, 例如: zh, en等'
    )
    
    parser.add_argument(
        '--promptfile',
        required=True,
        help='提示词文件路径'
    )
    
    parser.add_argument(
        '--diffile',
        required=True,
        help='git差异文件路径'
    )
    
    parser.add_argument(
        '--output',
        default='CHANGELOG.md',
        help='输出文件路径 (可选) , 默认为CHANGELOG.md'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式，不实际调用API'
    )
    
    args = parser.parse_args()
    
    # 创建配置
    config = Config(
        api_key=args.apikey,
        base_url=args.baseurl,
        diff_file=args.diffile,
        language=args.language,
        model=args.model,
        prompt_file=args.promptfile,
    )
    
    # 检查文件是否存在
    if not os.path.exists(config.prompt_file):
        print(f"错误: 提示词文件不存在: {config.prompt_file}")
        sys.exit(1)
    
    if not os.path.exists(config.diff_file):
        print(f"错误: 差异文件不存在: {config.diff_file}")
        sys.exit(1)
    
    # 测试模式
    if args.test:
        print("测试模式: 检查配置和文件...")
        print(f"API Key: {config.api_key[:10]}...")
        print(f"Base URL: {config.base_url}")
        print(f"Model: {config.model}")
        print(f"Prompt文件: {config.prompt_file}")
        print(f"Diff文件: {config.diff_file}")
        
        # 读取并显示文件内容预览
        try:
            with open(config.prompt_file, 'r', encoding='utf-8') as f:
                prompt_preview = f.read(200)
                print(f"\n提示词预览(前200字符):\n{prompt_preview}...")
        except:
            pass
        
        try:
            with open(config.diff_file, 'r', encoding='utf-8') as f:
                diff_preview = f.read(200)
                print(f"\n差异文件预览(前200字符):\n{diff_preview}...")
        except:
            pass
        
        print("\n测试完成，如果要实际调用API，请去掉 --test 参数")
        sys.exit(0)
    
    # 创建生成器并执行
    generator = ChangeLogGenerator(config)
    changelog = generator.generate_changelog()
    generator.save_changelog(changelog, args.output if args.output else None)

if __name__ == "__main__":
    main()
