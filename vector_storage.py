import json
from sentence_transformers import SentenceTransformer
import chromadb
from config import EMBEDDING_MODEL, CHILD_JSON, PARENT_JSON, DB_PATH, RETRIEVAL_TOP_K
from reranker import RetrievedChunk

class VectorStorage:
    def __init__(self):
        self.retrieval_top_k = RETRIEVAL_TOP_K
        self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection(name = 'pdf_fragments')
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        parents = self.load(PARENT_JSON)
        self.parent_lookup = {p['parent_id']: p['full_content'] for p in parents}
        
    def load(self,file_name:str)-> list[dict]:
        "加载原始json文件"
        with open(file_name,'r',encoding='utf-8')as f:
            return json.load(f)

    def embed(self,text:str)->list[float]:
        "将子块内容向量化"
        vector = self.model.encode(text).tolist()
        return vector

    def store(self, chunks: list[dict])->None:
        "存储向量化的文件块"
        for chunk in chunks:
            self.collection.add(
                ids = [chunk['child_id']],
                embeddings = [self.embed(chunk['searchable_content'])],
                documents = [chunk['searchable_content']],
                metadatas = [
                    {"parent_ref_id": chunk['parent_ref_id'], "page": chunk['page']}
                ]
            )
        return None

    def search(self,query:str)->list[RetrievedChunk]:
        "向量检索出k个可能的文本"
        query_vector = self.embed(query)
        results = self.collection.query(
            query_embeddings = [query_vector],
            n_results = self.retrieval_top_k
        )
        retrievalchunk = []
        for i in range(len(results['ids'][0])):
            chunk = RetrievedChunk(
                chunk_id=results['ids'][0][i],
                content=results['documents'][0][i],
                page_num=results['metadatas'][0][i]['page'],
                metadata=results['metadatas'][0][i]
            )
            retrievalchunk.append(chunk)
        return retrievalchunk

    def get_parent(self, parent_ref_ids: list[str])->list[dict]:
        "根据检索结果召回父块"
        seen = set()
        result = []
        for pid in parent_ref_ids:
            if pid not in seen:
                seen.add(pid)
                result.append({
                    'page':pid.replace('page_', ''),
                    'content':self.parent_lookup.get(pid)
                })
        return result

if __name__ == '__main__':
    storage = VectorStorage()
    # chunks = storage.load(CHILD_JSON)   # 读文件——调用方的活
    # storage.store(chunks)
    # r = storage.search("法兰")
    # print(r)
    
    
    import re
    child_content = storage.load(CHILD_JSON)
    blank_num = 0
    mark_num = 0
    ocr_num = 0
    OCR_GARBAGE = re.compile(r'[ðÐÞþøØ]')
    for content in child_content:
        if 'INTENTIONALLY LEFT BLANK' in content['searchable_content']:
            blank_num += 1
        if '$' in content['searchable_content']:
            mark_num += 1
            print(f"公式 {content['child_id']}: ...{content['searchable_content']}...")
        m = OCR_GARBAGE.search(content['searchable_content'])   
        if m:
            start = max(0, m.start() - 20)
            end = m.end() + 20
            ocr_num += 1
            print(f"乱码 {content['child_id']}: ...{content['searchable_content'][start:end]}...")
    print(f'空白说明{blank_num}个')
    print(f'公式{mark_num}个')
    print(f'乱码{ocr_num}个')

        

    


    