def create_chunks(row, encoding, chunk_size, overlap):
    
    d_content = row.doc_content
    
    tokens = encoding.encode(d_content)
    
    document_token_chunks = [tokens[token_id: token_id + chunk_size] for token_id in range(0, len(tokens), chunk_size-overlap)]
    document_context_chunks = [encoding.decode(chunk) for chunk in document_token_chunks]
    
    row['doc_token_lenth'] =  len(tokens)
    row['doc_content_ids'] = [f'{row.doc_name}_'+str(id) for id in range(len(document_context_chunks))]
    row['doc_content_chunks'] = document_context_chunks
    
    
    return row
    

def upsert_to_chromadb(row, chroma_client):
    try:
        
        chunks = row.doc_content_chunks
        chunk_ids = row.doc_content_ids
        
        chroma_client.upsert(documents=chunks, ids=chunk_ids)
        
        row['upserted'] = True
    except Exception as ex:
        print(f'Failed to upsert the embeddings to chroma db , exception: {ex}')
    
    return row
    
    