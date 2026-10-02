import re

def parse_markdown_to_blocks(md_text: str) -> list[dict]:
      """把 MinerU 的 markdown 输出切成 block 列表"""
      blocks = []
      table_block = []
      paragraph = []
      in_table = False 
      in_paragraph = False
      
      #把markdown输出按页切块
      parts = re.split(r'<!-- page (\d+) of (\d+) -->',md_text)

      #按title/table/text分类存为block
      for i in range(3,len(parts),3):
            lines = parts[i].splitlines()
            for line in lines:
                 #判断表格是否结束，结束则存储完整表格
                  if in_table and (not line.startswith("|")): 
                        blocks.append({
                              'page':parts[i-2],
                              'type':'table',
                              'text':table_block
                        })
                        table_block = []
                        in_table = False 

                  #判断段落text是否结束，结束则存储完整段落
                  if in_paragraph and (line.startswith("|") or (line.startswith('#')) or (line.startswith(r"<table>"))): 
                        blocks.append({
                              'page':parts[i-2],
                              'type':'text',
                              'text':'\n'.join(paragraph)
                        })
                        paragraph = []
                        in_paragraph = False

                  #噪声过滤
                  line = line.strip()
                  if is_noise(line):
                        continue

                  #处理每行情况，按类存储为字典
                  if not line:
                        continue
                  elif line.startswith('#'):
                        blocks.append({
                              'page':parts[i-2],
                              'type':'title',
                              'text':line
                        })
                  elif line.startswith(r"<table>"):
                        blocks.append({
                              'page':parts[i-2],
                              'type':'table',
                              'text':[line]
                        })
                  elif line.startswith('|'):
                        in_table = True
                        table_block.append(line)
                  else: 
                        in_paragraph = True 
                        paragraph.append(line)
      
            #如果文章最后是表格结尾，存储完整表格
            if in_table:
                  blocks.append({
                              'page':parts[i-2],
                              'type':'table',
                              'text':table_block
                        })
                  table_block = []
                  in_table = False 

            #如果文章最后是text结尾，存储完整段落    
            if in_paragraph:
                  blocks.append({
                        'page':parts[i-2],
                        'type':'text',
                        'text':'\n'.join(paragraph)
                  })
                  paragraph = []
                  in_paragraph = False

      #优化表格
      blocks = _merge_table_captions(blocks)

      return blocks

def is_noise(line:str) -> bool:
      """ 噪声过滤 """
      if line.isdigit():
        return True
      if line == 'ASME B16.5-2025':
            return True
      if re.fullmatch(r'[ivxlc]+', line):            # 罗马数字页
            return True
      if 'INTENTIONALLY LEFT BLANK' in line:         # 留白页
            return True
      if re.search(r'ð\**\d+\**Þ', line):            # 页眉乱码 ð25Þ / ð**25**Þ
            return True
      return False

def _merge_table_captions(blocks:list[dict]) -> list[dict]:
      """ 优化表格block（合并表格标题与表格）"""
      i = 0
      final_blocks = []
      while i < len(blocks):
            if i+1 < len(blocks) and blocks[i]['type'] == 'text' and blocks[i]['text'].startswith('Table') and blocks[i+1]['type'] == 'table':
                  final_blocks.append({
                        'page':blocks[i+1]['page'],
                        'type':'table',
                        'caption':blocks[i]['text'],
                        'text':blocks[i+1]['text']
                  })
                  i = i+2
            else:
                  final_blocks.append(blocks[i])
                  i = i+1
      return final_blocks


if __name__  == '__main__':
      with open ("output_tables.md", "r", encoding="utf-8") as f:
                  md_text = f.read()
      parse_block = parse_markdown_to_blocks(md_text=md_text)
      # print(parse_block)

      print(f'总共有{len(parse_block)}块')
      title_num = table_num = text_num = 0
      for i in range(len(parse_block)):
            if parse_block[i]['type'] == 'title' :
                  title_num +=1
            elif parse_block[i]['type'] == 'table' :
                  table_num +=1
            else:
                  text_num +=1
      print(f'表格有{table_num}个')
      print(f'标题有{title_num}个')
      print(f'正文有{text_num}个')

      # i = 0
      # for block in parse_block:
      #       if block['type'] != 'table':
      #             print(block['type'])
      #             print(block['text'][0:60])
      #       else:
      #             i += 1
      #             print(block['type'])
      #             print(block)
      #       if i == 5:
      #             break

      for b in parse_block:
            print(b['page'], b['type'], repr(b.get('text', b.get('caption', ''))[:60]), sep=' | ')


                        
                  
      

      












      

            







          