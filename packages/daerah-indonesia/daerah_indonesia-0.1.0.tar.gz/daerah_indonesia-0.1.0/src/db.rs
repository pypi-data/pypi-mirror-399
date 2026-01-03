use pyo3::{ PyResult, exceptions::PyIOError };
use std::{fs, io::Cursor, path::PathBuf};

// Embed file db
const COMPRESSED_DB: &[u8] = include_bytes!("daerah.sqlite.zst");
const DB_VERSION: &str = "v0_1";

pub fn get_db_path() -> PyResult<PathBuf> {
    let cache_dir = dirs::cache_dir().unwrap_or_else(|| std::env::temp_dir());
    let db_file = format!("daerah_{}.sqlite", DB_VERSION);
    let db_path = cache_dir.join(db_file);

    if !db_path.exists() {
        let mut reader = Cursor::new(COMPRESSED_DB);
        let mut out_file = fs::File::create(&db_path).map_err(|e| {
            PyIOError::new_err(format!("Gagal membuat file temp: {}", e))
        })?;
        
        zstd::stream::copy_decode(&mut reader, &mut out_file).map_err(|e| {
            PyIOError::new_err(format!("Gagal dekompresi db: {}", e))
        })?;
    }

    Ok(db_path)
}
