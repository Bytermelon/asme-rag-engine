"""子块数据质量检查：统计空白页说明 / 公式 / OCR 乱码"""
import json
import re
import sys
from pathlib import Path

# 保证无论从哪里运行，都能从项目根目录导入 config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CHILD_JSON

OCR_GARBAGE = re.compile(r'[ðÐÞþøØ]')


def main() -> None:
    with open(CHILD_JSON, encoding='utf-8') as f:
        children = json.load(f)

    blank_num = 0
    mark_num = 0
    ocr_num = 0
    for c in children:
        text = c['searchable_content']
        if 'INTENTIONALLY LEFT BLANK' in text:
            blank_num += 1
        if '$' in text:
            mark_num += 1
            print(f"公式 {c['child_id']}: ...{text}...")
        m = OCR_GARBAGE.search(text)
        if m:
            start = max(0, m.start() - 20)
            end = m.end() + 20
            ocr_num += 1
            print(f"乱码 {c['child_id']}: ...{text[start:end]}...")

    print(f'空白说明 {blank_num} 个')
    print(f'公式 {mark_num} 个')
    print(f'乱码 {ocr_num} 个')


if __name__ == '__main__':
    main()