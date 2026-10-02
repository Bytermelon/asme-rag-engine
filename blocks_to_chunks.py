def block_to_child_text(block:dict) -> str:
    """block → 可嵌入的纯文本（表格拼上标题）"""
    if block['type'] == 'table':
        if block.get('caption',''):
            child_text = block['caption']+':'+'\n'.join(block['text'])
        else:
            child_text = '\n'.join(block['text'])
    else:
        child_text = block['text']
    return child_text


def blocks_to_chunks(blocks:list[dict]) -> list[dict]:
    """ blocks → 子块列表（每块一个，含 page）"""
    children = []
    for block in blocks:
        children.append({
            'page':block['page'],
            'text':block_to_child_text(block)
        })
    return children

def blocks_to_parents(blocks:list[dict]) -> list[dict]:
    """blocks → 父块列表（按页拼成父块，含page）"""
    page = blocks[0]['page']
    parents = []
    chunk = []
    for block in blocks:
        if page != block['page']:
            parents.append({
                    'page':page,
                    'text':'\n\n'.join(chunk)
                })
            chunk = []
            page = block['page']
        chunk.append(block_to_child_text(block))       
    #最后一页存为父块
    parents.append({
        'page':page,
        'text':'\n\n'.join(chunk)
    })
    return parents


import json

def  write_chunks_for_rag1(children:list[dict], parents:list[dict]) -> None:
    """把父子块及关联落盘"""
    new_children = []
    new_parents = []
    for i,chunk_1 in enumerate(children):
        new_children.append({
            'child_id': f'block_{i:04d}',
            'parent_ref_id':f"page_{chunk_1['page']}",
            'page':chunk_1['page'],
            'searchable_content':chunk_1['text']
        })
    for chunk_2 in parents:
        new_parents.append({
            'parent_id':f"page_{chunk_2['page']}",
            'page':chunk_2['page'],
            'full_content':chunk_2['text']
        })

    with open ("child_chunks.json",'w',encoding='utf-8')as f:
        json.dump(new_children,f,ensure_ascii=False,indent=4)
    with open ("parent_chunks.json",'w',encoding='utf-8')as f:
        json.dump(new_parents,f,ensure_ascii=False,indent=4)

    return None
    






if __name__ == '__main__':
    from mineru_parser import parse_markdown_to_blocks
    with open ("output_tables.md", "r", encoding="utf-8") as f:
        md_text = f.read()
    parse_block = parse_markdown_to_blocks(md_text=md_text)
    children = blocks_to_chunks(parse_block)
    parents = blocks_to_parents(parse_block)
    write_chunks_for_rag1(children=children,parents=parents)

    # print(f'子块数量为{len(children)}')
    # print(f'父块数量为{len(parents)}')
    # print(f'页数量为{len(set(b['page'] for b in parse_block))}')
    # print(f'父块第一块{parents[0]}')
        


        



