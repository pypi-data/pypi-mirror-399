pub mod model;
pub mod db;

use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use rusqlite::{Connection, OptionalExtension};
use chrono::{Datelike, Utc};
use model::{Wilayah, Pos, Nik, WilayahInfo};
use db::get_db_path;


#[pyfunction]
fn provinsi() -> PyResult<Vec<Wilayah>> {
    let db_path = get_db_path()?;

    let conn = Connection::open(db_path).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let mut stmt = conn.prepare("SELECT province_code, province_name FROM provinces")
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    let daerah_iter = stmt.query_map([], |row| {
        Ok(Wilayah {
            kode: row.get(0)?,
            nama: row.get(1)?,
        })
    }).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    let mut results = Vec::new();
    for daerah in daerah_iter {
        results.push(daerah.map_err(|e| PyRuntimeError::new_err(e.to_string()))?);
    }

    Ok(results)
}

#[pyfunction]
fn daerah(daerah: String, kode_daerah: i64) -> PyResult<Vec<Wilayah>> {
    
    let query_str = match daerah.as_str() {
        "kab_kota" => "SELECT city_code, city_name FROM cities WHERE city_province_code = ?1",
        "kecamatan" => "SELECT sub_district_code, sub_district_name FROM sub_districts WHERE sub_district_city_code = ?1",
        "kelurahan" => "SELECT village_code, village_name FROM villages WHERE village_sub_district_code = ?1",
        _ => return Err(PyValueError::new_err(format!("Daerah {} tidak valid. Gunakan kab_kota, kecamatan atau kelurahan", daerah)))
    };

    let db_path = get_db_path()?;
    let conn = Connection::open(db_path).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let mut stmt = conn.prepare(query_str).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let daerah_iter = stmt.query_map([kode_daerah], |row| {
        Ok(Wilayah {
            kode: row.get(0)?,
            nama: row.get(1)?,
        })
    }).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    let mut results = Vec::new();
    for daerah in daerah_iter {
        results.push(daerah.map_err(|e| PyRuntimeError::new_err(e.to_string()))?);
    }
    
    Ok(results)
}

#[pyfunction]
fn kode_pos(daerah: String, kode_daerah: i64) -> PyResult<Vec<Pos>> {
    let query_str = match daerah.as_str() {
        "provinsi" => "SELECT province_name AS nama,  province_postal_codes AS kode_pos FROM provinces WHERE province_code = ?1",
        "kab_kota" => "SELECT city_name AS nama, city_postal_codes AS kode_pos FROM cities WHERE city_code = ?1",
        "kecamatan" => "SELECT sub_district_name AS nama,  sub_district_postal_codes AS kode_pos FROM sub_districts WHERE sub_district_code = ?1",
        "kelurahan" => "SELECT village_name AS nama, village_postal_codes AS kode_pos FROM villages WHERE village_code = ?1",
        _ => return Err(PyValueError::new_err(format!("Daerah {} tidak valid. Gunakan: provinsi, kab_kota, kecamatan, atau kelurahan", daerah)))
    };

    let db_path = get_db_path()?;
    
    let conn = Connection::open(db_path).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let mut stmt = conn.prepare(query_str).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let pos_iter = stmt.query_map([kode_daerah], |row| {
        Ok(Pos {
            nama: row.get(0)?,
            kode_pos: row.get(1)?,
        })
    }).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let mut results = Vec::new();
    for pos in pos_iter {
        results.push(pos.map_err(|e| PyRuntimeError::new_err(e.to_string()))?);
    }

    Ok(results)
}

#[pyfunction]
fn data_nik(nik: String) -> PyResult<Nik> {
    // Cek panjang 16 digit dan harus angka semua
    if nik.len() != 16 || !nik.chars().all(|c| c.is_numeric()) {
        return Err(PyValueError::new_err(format!("NIK '{}' tidak valid. Harus 16 digit angka.", nik)));
    }

    // Kode Kecamatan (6 digit awal + "0")
    let kode_kecamatan_str = format!("{}0", &nik[0..6]);
    let kode_kecamatan: i64 = kode_kecamatan_str.parse().map_err(|_| {
        PyValueError::new_err("Gagal parsing kode wilayah.")
    })?;

    // Tanggal lahir gunakan unwrap_or(0), jika string gagal parse (walau sudah dicek is_numeric)
    let tgl: u32 = nik[6..8].parse().unwrap_or(0);
    let bln: u32 = nik[8..10].parse().unwrap_or(0);
    let thn_singkat: u32 = nik[10..12].parse().unwrap_or(0);

    // Cek Jenis Kelamin (Jika tgl > 40, kurangi 40)
    let (tgl_lahir, jenis_kelamin) = if tgl > 40 {
        (tgl - 40, "Perempuan")
    } else {
        (tgl, "Laki-laki")
    };

    // Validasi Tanggal & Bulan
    if tgl_lahir == 0 || tgl_lahir > 31 || bln == 0 || bln > 12 {
        return Err(PyValueError::new_err("tanggal/bulan dalam NIK tidak valid."));
    }

    // Tentukan Tahun Lahir (Y2K)
    let thn_sekarang_singkat = (Utc::now().year() % 100) as u32;
    let thn_lahir = if thn_singkat > thn_sekarang_singkat {
        1900 + thn_singkat
    } else {
        2000 + thn_singkat
    };

    let tanggal_lahir_str = format!("{:04}-{:02}-{:02}", thn_lahir, bln, tgl_lahir);
    let no_registrasi = &nik[12..16];

    let db_path = get_db_path()?; 
    let conn = Connection::open(db_path).map_err(|e| {
        PyRuntimeError::new_err(e.to_string())
    })?;

    let query = "
        SELECT 
            p.province_name, 
            c.city_name, 
            s.sub_district_name 
        FROM sub_districts AS s
        JOIN cities AS c ON s.sub_district_city_code = c.city_code
        JOIN provinces as p ON c.city_province_code = p.province_code
        WHERE s.sub_district_code = ?1
    ";

    let wilayah_opt = conn.query_row(query, [kode_kecamatan], |row| {
        Ok(WilayahInfo {
            provinsi: row.get(0)?,
            kab_kota: row.get(1)?,
            kecamatan: row.get(2)?,
        })
    }).optional().map_err(|e| PyRuntimeError::new_err(e.to_string()))?;


    match wilayah_opt {
        Some(w) => {
            Ok(Nik {
                nik: nik.clone(),
                provinsi: w.provinsi,
                kab_kota: w.kab_kota,
                kecamatan: w.kecamatan,
                jenis_kelamin: jenis_kelamin.to_string(),
                tanggal_lahir: tanggal_lahir_str,
                no_registrasi: no_registrasi.to_string(),
            })
        },
        None => {
            Err(PyValueError::new_err(format!("Kode wilayah NIK '{}' tidak ditemukan di database.", nik)))
        }
    }
}

#[pymodule]
fn daerah_indonesia(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(provinsi, m)?)?;
    m.add_function(wrap_pyfunction!(daerah, m)?)?;
    m.add_function(wrap_pyfunction!(kode_pos, m)?)?;
    m.add_function(wrap_pyfunction!(data_nik, m)?)?;
    
    m.add_class::<Wilayah>()?;
    m.add_class::<Pos>()?;
    m.add_class::<Nik>()?;
    Ok(())
}
