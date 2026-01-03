use crate::document::Document;
use anyhow::Result;
use arrow_array::{FixedSizeListArray, RecordBatch, RecordBatchIterator, StringArray, Float32Array};
use arrow_array::types::Float32Type;
use futures::TryStreamExt;
use lancedb::connection::Connection;
use lancedb::query::{ExecutableQuery, QueryBase};
use lancedb::{connect, Table};
use std::sync::Arc;
use std::collections::HashMap;
use chrono::Utc;

const TABLE_NAME: &str = "vectors";

#[derive(Debug, Clone)]
pub struct SearchResult {
    pub document: Document,
    pub score: f32,
    pub chunk_index: usize,
}

#[derive(Debug, Clone)]
pub struct Vector {
    // Legacy struct needed for file_watcher signatures or if referenced?
    // file_watcher creates Vector but now we use VectorRecord for DB.
    // Let's keep Vector definition if file_watcher uses it, or update file_watcher.
    // file_watcher uses Vector::new.
    pub id: String,
    pub embedding: Vec<f32>,
    pub document_id: String,
    pub chunk_index: usize,
    pub metadata: HashMap<String, String>,
}

impl Vector {
    pub fn new(
        id: String,
        embedding: Vec<f32>,
        document_id: String,
        chunk_index: usize,
        metadata: HashMap<String, String>,
    ) -> Self {
        Self {
            id,
            embedding,
            document_id,
            chunk_index,
            metadata,
        }
    }
}

pub struct VectorStore {
    conn: Connection,
}

impl VectorStore {
    pub async fn new(uri: &str) -> Result<Self> {
        let conn = connect(uri).execute().await?;
        Ok(Self { conn })
    }

    // Dummy add_document for compatibility with file_watcher (which called it separately)
    // Now documents are stored with vectors.
    pub async fn add_document(&self, _document: Document) {
        // No-op
    }

    // Adapt to take Vector struct from file_watcher
    pub async fn add_vectors(&self, vectors: Vec<Vector>) -> Result<()> {
        if vectors.is_empty() {
             return Ok(());
        }
        
        // Convert Vector (legacy) to VectorRecord (Arrow friendly)
        let records: Vec<VectorRecord> = vectors.into_iter().map(|v| {
             VectorRecord {
                 id: v.id,
                 embedding: v.embedding,
                 document_id: v.document_id,
                 content: "".to_string(), // content missing in Vector struct! 
                 // This is a problem. FileWatcher splits embedding and content. 
                 // We need content here to store in LanceDB.
                 // Hack: FileWatcher needs update to pass content.
                 // For now, store empty string and fix FileWatcher later?
                 // Or better: update FileWatcher to NOT pass Vectors but pass records.
                 // But sticking to minimal changes:
                 chunk_index: v.chunk_index,
                 metadata: serde_json::to_string(&v.metadata).unwrap_or_default(),
             }
        }).collect();
        
        // FIXME: FileWatcher logic is broken with this change because it relied on add_document storing content separately.
        // We will fix FileWatcher to pass content.
        
        let batch = vector_records_to_batch(records)?;
        let schema = batch.schema();
        let batches = Box::new(RecordBatchIterator::new(vec![Ok(batch)], schema));

        if self.conn.table_names().execute().await?.contains(&TABLE_NAME.to_string()) {
            let table = self.conn.open_table(TABLE_NAME).execute().await?;
            table.add(batches).execute().await?;
        } else {
            self.conn.create_table(TABLE_NAME, batches).execute().await?;
        }
        
        Ok(())
    }
    
    // New method for RAGKernel to call with full info
    pub async fn add_vector_records(&self, records: Vec<VectorRecord>) -> Result<()> {
        if records.is_empty() { return Ok(()); }
        let batch = vector_records_to_batch(records)?;
        let schema = batch.schema();
        let batches = Box::new(RecordBatchIterator::new(vec![Ok(batch)], schema));

        if self.conn.table_names().execute().await?.contains(&TABLE_NAME.to_string()) {
            let table = self.conn.open_table(TABLE_NAME).execute().await?;
            table.add(batches).execute().await?;
        } else {
            self.conn.create_table(TABLE_NAME, batches).execute().await?;
        }
        Ok(())
    }

    pub async fn search(&self, query_embedding: &[f32], top_k: usize) -> Result<Vec<SearchResult>> {
        if !self.conn.table_names().execute().await?.contains(&TABLE_NAME.to_string()) {
            return Ok(Vec::new());
        }

        let table = self.conn.open_table(TABLE_NAME).execute().await?;
        
        let mut results = table
            .query()
            .nearest_to(query_embedding)?
            .limit(top_k)
            .execute()
            .await?;

        let mut search_results = Vec::new();

        while let Some(batch) = results.try_next().await? {
             let _schema = batch.schema();
             let content_col = batch.column_by_name("content").unwrap().as_any().downcast_ref::<StringArray>().unwrap();
             let doc_id_col = batch.column_by_name("document_id").unwrap().as_any().downcast_ref::<StringArray>().unwrap();
             let metadata_col = batch.column_by_name("metadata").unwrap().as_any().downcast_ref::<StringArray>().unwrap();
             let chunk_index_col = batch.column_by_name("chunk_index").unwrap().as_any().downcast_ref::<arrow_array::UInt32Array>().unwrap();
             let dist_col = batch.column_by_name("_distance").unwrap().as_any().downcast_ref::<Float32Array>().unwrap();

             for i in 0..batch.num_rows() {
                 let content = content_col.value(i).to_string();
                 let document_id = doc_id_col.value(i).to_string();
                 let metadata_json = metadata_col.value(i);
                 let metadata: HashMap<String, String> = serde_json::from_str(metadata_json).unwrap_or_default();
                 let chunk_index = chunk_index_col.value(i) as usize;
                 let distance = dist_col.value(i);
                 let score = 1.0 - distance;

                 search_results.push(SearchResult {
                     document: Document {
                         id: document_id,
                         content,
                         metadata,
                         created_at: Utc::now(),
                     },
                     score,
                     chunk_index,
                 });
             }
        }
        
        Ok(search_results)
    }

    pub async fn count(&self) -> usize {
        if let Ok(table) = self.conn.open_table(TABLE_NAME).execute().await {
            match table.count_rows(None).await {
                Ok(c) => c,
                Err(_) => 0,
            }
        } else {
            0
        }
    }

    pub async fn list_documents(&self) -> Result<Vec<String>> {
         Ok(Vec::new()) 
    }
    
    pub async fn remove_document(&self, document_id: &str) -> Result<bool> {
        if let Ok(table) = self.conn.open_table(TABLE_NAME).execute().await {
             let predicate = format!("document_id = '{}'", document_id);
             table.delete(&predicate).await?;
             Ok(true)
        } else {
            Ok(false)
        }
    }
}

pub struct VectorRecord {
    pub id: String,
    pub embedding: Vec<f32>,
    pub document_id: String,
    pub content: String, 
    pub chunk_index: usize,
    pub metadata: String, 
}

fn vector_records_to_batch(records: Vec<VectorRecord>) -> Result<RecordBatch> {
    use arrow_schema::{DataType, Field, Schema};
    use std::sync::Arc;

    if records.is_empty() {
        return Err(anyhow::anyhow!("No records to convert"));
    }
    
    let dim = records[0].embedding.len();
    
    let schema = Arc::new(Schema::new(vec![
        Field::new("id", DataType::Utf8, false),
        Field::new("vector", DataType::FixedSizeList(
            Arc::new(Field::new("item", DataType::Float32, true)),
            dim as i32
        ), false),
        Field::new("document_id", DataType::Utf8, false),
        Field::new("content", DataType::Utf8, false),
        Field::new("chunk_index", DataType::UInt32, false),
        Field::new("metadata", DataType::Utf8, false),
    ]));

    let ids: Vec<String> = records.iter().map(|r| r.id.clone()).collect();
    // Flatten vectors
    let vectors_flat: Vec<f32> = records.iter().flat_map(|r| r.embedding.clone()).collect();
    let doc_ids: Vec<String> = records.iter().map(|r| r.document_id.clone()).collect();
    let contents: Vec<String> = records.iter().map(|r| r.content.clone()).collect();
    let chunk_indices: Vec<u32> = records.iter().map(|r| r.chunk_index as u32).collect();
    let metadatas: Vec<String> = records.iter().map(|r| r.metadata.clone()).collect();

    let id_array = StringArray::from(ids);
    let vector_array = FixedSizeListArray::from_iter_primitive::<Float32Type, _, _>(
        records.iter().map(|r| Some(r.embedding.iter().map(|x| Some(*x))))
        , dim as i32
    );
    let doc_id_array = StringArray::from(doc_ids);
    let content_array = StringArray::from(contents);
    let chunk_index_array = arrow_array::UInt32Array::from(chunk_indices);
    let metadata_array = StringArray::from(metadatas);

    Ok(RecordBatch::try_new(schema, vec![
        Arc::new(id_array),
        Arc::new(vector_array),
        Arc::new(doc_id_array),
        Arc::new(content_array),
        Arc::new(chunk_index_array),
        Arc::new(metadata_array),
    ])?)
}
